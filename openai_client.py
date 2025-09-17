import os
import openai
from openai import OpenAI
import requests
from typing import Optional
import json
from datetime import datetime
import re

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                print("OpenAI client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def check_api_availability(self) -> bool:
        if not self.client or not self.api_key:
            return False
        try:
            response = self.client.models.list()
            return True
        except Exception as e:
            print(f"OpenAI API not available: {e}")
            return False
    
    async def generate_medical_infographic(self, pathology_text: str) -> str:
        if not self.client:
            raise Exception("OpenAI client not available")
        extracted_data = self._extract_medical_data(pathology_text)
        image_prompt = self._create_image_prompt(extracted_data)
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1792",
                quality="hd",
                n=1
            )
            image_url = response.data[0].url
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"temp/medical_infographic_{timestamp}.png"
            img_response = requests.get(image_url)
            with open(image_path, 'wb') as f:
                f.write(img_response.content)
            return image_path
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    async def generate_health_summary(self, pathology_text: str) -> str:
        if not self.client:
            raise Exception("OpenAI client not available")
        summary_prompt = f"""
        Analyze the provided health test results and create a comprehensive health report summary following this format:

        HEALTH REPORT SUMMARY

        For each parameter, provide:

        [Parameter Name]
        - Result: [Value] [Unit]
        - Status: [HIGH/LOW/NORMAL]
        - Reference Range: [Display as: < X | X-Y | > Y]
        - Your Value Position: [Show where patient falls in range]
        - Meaning: [Explain what this parameter indicates and why the current level is concerning/normal]
        - Tips: [Provide 2-3 specific dietary/lifestyle recommendations]

        Format requirements:
        - List parameters in order of concern (abnormal values first)
        - Use clear medical terminology with patient-friendly explanations
        - Provide actionable, specific advice
        - Include foods to avoid and foods to include
        - Mention lifestyle changes where relevant
        - Keep explanations concise but informative
        - Use consistent formatting throughout

        Pathology Report:
        {pathology_text}
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical professional analyzing pathology reports and providing patient-friendly health summaries."},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _extract_medical_data(self, text: str) -> dict:
        extracted = {
            "patient_name": "Patient Name",
            "age": "Adult",
            "gender": "Male",
            "tests": [],
            "health_score": None
        }
        text_lower = text.lower()
        if any(word in text_lower for word in ['female', 'woman', 'mrs', 'ms']):
            extracted["gender"] = "Female"
        elif any(word in text_lower for word in ['child', 'pediatric']) and 'years' in text_lower:
            extracted["gender"] = "Child"
        test_patterns = {
            "TSH": r"tsh[:\s]*(\d+\.?\d*)",
            "Cholesterol": r"cholesterol[:\s]*(\d+\.?\d*)",
            "Hemoglobin": r"hemoglobin[:\s]*(\d+\.?\d*)",
            "HbA1c": r"hba1c[:\s]*(\d+\.?\d*)",
        }
        for test_name, pattern in test_patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                extracted["tests"].append({
                    "name": test_name,
                    "value": match.group(1)
                })
        return extracted
    
    def _create_image_prompt(self, data: dict) -> str:
        base_prompt = """
        Create a clean medical infographic with the following layout:
        
        - Top header: "Personalized Summary & Vital Parameters"
        - Top-right: "Your Health Score" card with orange badge (if score provided)
        - Center: Human silhouette made of blue dots/mesh pattern for {gender} patient
        - Left and right columns with circular medical test cards
        - Each card shows: icon, test name, value, status (green/yellow/red)
        - Clean white background with medical dashboard style
        - Use colors: teal #0ea5a7, orange #f97316, green #10b981, yellow #f59e0b, red #ef4444
        - Medical icons for heart, kidney, liver, blood, thyroid, etc.
        - Bottom text: "All lab results are subject to clinical interpretation"
        - Portrait orientation, professional medical design
        """.format(gender=data.get("gender", "Adult Male"))
        return base_prompt

