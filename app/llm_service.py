import os
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()


class LLMDiscountService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def create_discount_prompt(self, age: int, is_disabled: bool, medical_conditions: Optional[List[str]]) -> str:
        """Create a well-engineered prompt for discount calculation"""
        
        prompt = f"""
You are a discount calculation expert for a bowling shoe rental service. 
Your task is to determine the appropriate discount percentage based on customer information.

DISCOUNT RULES:
1. Age-based discounts:
   - Age 0-12: 20% discount
   - Age 13-18: 10% discount  
   - Age 65 and above: 15% discount

2. Disability status:
   - Disabled customers: 25% discount

3. Medical conditions:
   - Diabetes: 10% discount
   - Hypertension: 10% discount
   - Chronic condition: 10% discount

IMPORTANT RULES:
- If multiple discounts apply, choose the HIGHEST discount percentage
- Only apply ONE discount (the highest one)
- Valid medical conditions are: diabetes, hypertension, chronic condition
- Discount percentages should be returned as decimal (e.g., 0.25 for 25%)

CUSTOMER INFORMATION:
- Age: {age}
- Disabled: {is_disabled}
- Medical conditions: {medical_conditions if medical_conditions else 'None'}

Please analyze this customer information and provide:
1. The discount percentage (as decimal, e.g., 0.25 for 25%)
2. The reason for the discount

Respond ONLY in JSON format:
{{
    "discount_percentage": 0.XX,
    "reason": "explanation of why this discount was applied"
}}
"""
        return prompt

    async def calculate_discount(self, age: int, is_disabled: bool, medical_conditions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Calculate discount using Gemini LLM with fallback to rule-based system"""
        
        try:
            # Try Gemini-based calculation
            prompt = self.create_discount_prompt(age, is_disabled, medical_conditions)
            
            # Generate content using Gemini
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=150,
                )
            )

            result_text = response.text.strip()
            
            # Clean up the response (remove markdown formatting if present)
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            elif result_text.startswith('```'):
                result_text = result_text.replace('```', '').strip()
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
                discount_percentage = float(result.get("discount_percentage", 0))
                reason = result.get("reason", "No discount applied")
                
                # Validate discount percentage
                if 0 <= discount_percentage <= 1:
                    return {
                        "discount_percentage": discount_percentage,
                        "reason": reason,
                        "source": "gemini"
                    }
                else:
                    raise ValueError("Invalid discount percentage from Gemini")
                    
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"Error parsing Gemini response: {e}")
                print(f"Raw response: {result_text}")
                # Fallback to rule-based system
                return await self.calculate_discount_fallback(age, is_disabled, medical_conditions)
                
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            # Fallback to rule-based system
            return await self.calculate_discount_fallback(age, is_disabled, medical_conditions)

    async def calculate_discount_fallback(self, age: int, is_disabled: bool, medical_conditions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fallback rule-based discount calculation"""
        
        discounts = []
        
        # Age-based discounts
        if 0 <= age <= 12:
            discounts.append((0.20, "Age 0-12 discount (20%)"))
        elif 13 <= age <= 18:
            discounts.append((0.10, "Age 13-18 discount (10%)"))
        elif age >= 65:
            discounts.append((0.15, "Age 65+ discount (15%)"))
        
        # Disability discount
        if is_disabled:
            discounts.append((0.25, "Disability discount (25%)"))
        
        # Medical condition discounts
        if medical_conditions:
            valid_conditions = ['diabetes', 'hypertension', 'chronic condition']
            for condition in medical_conditions:
                if condition.lower() in valid_conditions:
                    discounts.append((0.10, f"Medical condition discount - {condition} (10%)"))
        
        # Choose the highest discount
        if discounts:
            highest_discount = max(discounts, key=lambda x: x[0])
            return {
                "discount_percentage": highest_discount[0],
                "reason": highest_discount[1],
                "source": "rule_based"
            }
        else:
            return {
                "discount_percentage": 0.0,
                "reason": "No discount applicable",
                "source": "rule_based"
            }

    async def validate_discount_logic(self, age: int, is_disabled: bool, medical_conditions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Validate discount logic by comparing Gemini and rule-based results"""
        
        gemini_result = await self.calculate_discount(age, is_disabled, medical_conditions)
        rule_result = await self.calculate_discount_fallback(age, is_disabled, medical_conditions)
        
        return {
            "gemini_result": gemini_result,
            "rule_result": rule_result,
            "match": abs(gemini_result["discount_percentage"] - rule_result["discount_percentage"]) < 0.01
        }


# Global LLM service instance
llm_service = LLMDiscountService() 