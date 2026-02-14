import requests
import json
import logging

logger = logging.getLogger(__name__)

from logic.llm_client import KaggleClient

class ProspectAnalyzer:
    def __init__(self, llm_url="https://preocular-repudiatory-jeana.ngrok-free.dev"):
        self.client = KaggleClient(base_url=llm_url)

    def analyze_profile(self, raw_text):
        """
        Sends raw profile text to the remote LLM to extract structured data 
        and infer psychological/communication traits.
        """
        system_prompt = """You are an expert sales researcher. Extract structured data from profiles into JSON.
        
        🚨 CRITICAL EXTRACTION RULES:
        1. GROUPED EXPERIENCE: If someone has multiple roles at the SAME company (e.g., "Founder and Managing Partner" then "Founder" both at "ajvc"), extract the MOST RECENT/CURRENT role and that company.
        2. COMPANY NAME: When company name appears BEFORE the role (like "ajvc logo\najvc\n7 yrs 11 mos\nFounder and Managing Partner"), the company is "ajvc", NOT "Founder".
        3. OWNER ONLY: The profile OWNER's name appears FIRST. IGNORE any other people's names, titles, or companies that appear later - those are sidebar suggestions.
        4. CURRENT POSITION: If there are multiple positions, extract the one marked as "Present" or the most recent date range.
        5. ROLE FORMAT: Extract ONLY the role title (e.g., "Founder and Managing Partner"), NOT the company name in the role field.
        
        EXAMPLE OF GROUPED EXPERIENCE:
        Input: "ajvc\n7 yrs 11 mos\nFounder and Managing Partner\nAug 2024 - Present · 1 yr 7 mos\nIndia\nInvesting in Indian pre-seed startups"
        Correct extraction: company="ajvc", role="Founder and Managing Partner"
        WRONG extraction: company="Founder and Managing Partner", role="ajvc"
        """

        example_input = """
        Name: Sarah Jones
        Role: VP Marketing at CloudScale
        Bio: 10 years driving growth for SaaS startups. Loves data-driven marketing and hiking.
        Experience:
        - VP Marketing, CloudScale (2020-Present)
        - Director of Demand Gen, TechStart (2015-2020)
        Education:
        - MBA, Stanford University
        - B.A. Communications, UCLA
        Certifications:
        - Google Analytics Certified
        - HubSpot Inbound Marketing
        Recent Activity:
        - Shared a post about "The Future of AI in Marketing".
        """

        example_output = json.dumps({
            "name": "Sarah Jones",
            "company": "CloudScale",
            "role": "VP Marketing",
            "industry": "SaaS / Technology",
            "seniority": "Executive",
            "education": ["MBA, Stanford University", "B.A. Communications, UCLA"],
            "certifications": ["Google Analytics Certified", "HubSpot Inbound Marketing"],
            "recent_activity": ["Shared a post about 'The Future of AI in Marketing'"],
            "psychological_profile": {
                "decision_authority": "High",
                "pain_points": ["Scaling growth", "Data analytics"],
                "goals": ["Drive revenue", "Brand awareness"],
                "communication_preference": "Data-driven"
            },
            "communication_style": {
                "formality": "Casual",
                "tone": "Enthusiastic",
                "vocabulary": "Simple"
            },
            "key_insights": ["Experienced in SaaS growth", "Outdoor enthusiast"],
            "personalization_hooks": ["Mention Stanford MBA", "Discuss AI in Marketing post", "Ask about hiking"]
        })

        user_prompt = f"""
        EXAMPLE INPUT:
        {example_input}
        
        EXAMPLE JSON OUTPUT:
        {example_output}
        
        REAL INPUT:
        {raw_text[:8000]}
        
        REAL JSON OUTPUT:
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response_text = self.client.chat(messages)
            
            json_res = self.client.extract_json(response_text)
            if json_res:
                return json_res
            
            # Fallback or return raw text if that's what we got (though analyzer expects dict)
            return {"error": "Failed to parse JSON response", "raw_response": response_text}
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": str(e)}
