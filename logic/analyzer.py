import requests
import json
import logging
import re

logger = logging.getLogger(__name__)

from logic.llm_client import KaggleClient

class ProspectAnalyzer:
    def __init__(self, llm_url="https://ununited-laudable-anya.ngrok-free.dev"):
        self.client = KaggleClient(base_url=llm_url)
    
    def _clean_scraped_text(self, text):
        """Clean scraped text by removing duplicates and noise."""
        lines = text.split('\n')
        seen = set()
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            # Skip LinkedIn UI noise
            if any(noise in line for noise in ['notifications', 'new message', 'new feed']):
                continue
            # Remove duplicate consecutive lines
            if line not in seen or len(line) > 50:  # Keep longer lines even if duplicate
                cleaned_lines.append(line)
                seen.add(line)
        
        return '\n'.join(cleaned_lines)
    
    def _replace_nulls(self, data):
        """Replace null values with appropriate defaults."""
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    # Determine appropriate replacement based on key
                    if isinstance(data.get(key), list) or key in ['education', 'certifications', 'recent_activity', 'pain_points', 'goals', 'key_insights', 'personalization_hooks']:
                        data[key] = []
                    elif isinstance(data.get(key), dict):
                        data[key] = {}
                    else:
                        data[key] = "Unknown"
                elif isinstance(value, dict):
                    data[key] = self._replace_nulls(value)
                elif isinstance(value, list):
                    data[key] = [self._replace_nulls(item) if isinstance(item, (dict, list)) else (item if item is not None else "Unknown") for item in value]
        return data

    def analyze_profile(self, raw_text):
        """
        Sends raw profile text to the remote LLM to extract structured data 
        and infer psychological/communication traits.
        """
        # Clean the raw text first
        cleaned_text = self._clean_scraped_text(raw_text)
        
        system_prompt = """You are an expert sales researcher. Extract structured data from profiles into JSON. 

CRITICAL RULES:
1. Return ONLY valid JSON, no other text
2. COMBINE ALL DATA: The input may contain multiple sections (LinkedIn, Resume, Text). MERGE all information about the SAME PERSON
3. ONLY extract data for the profile owner (the FIRST person mentioned)
4. IGNORE any other names appearing later (those are LinkedIn sidebar suggestions)
5. For students: use their university as "company" and their year/major as "role"
6. NEVER use null - if a field is unknown, use "Unknown" string
7. Always fill in all fields with reasonable values based on ALL provided data sources"""

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
        """

        example_output = json.dumps({
            "name": "Sarah Jones",
            "company": "CloudScale",
            "role": "VP Marketing",
            "industry": "SaaS / Technology",
            "seniority": "Executive",
            "education": ["MBA, Stanford University", "B.A. Communications, UCLA"],
            "certifications": [],
            "recent_activity": [],
            "psychological_profile": {
                "decision_authority": "High",
                "pain_points": ["Scaling growth", "Data analytics"],
                "goals": ["Drive revenue", "Brand awareness"],
                "communication_preference": "Data-driven"
            },
            "communication_style": {
                "formality": "Professional",
                "tone": "Enthusiastic",
                "vocabulary": "Business-oriented"
            },
            "key_insights": ["Experienced in SaaS growth", "Outdoor enthusiast"],
            "personalization_hooks": ["Mention Stanford MBA", "Ask about hiking"]
        }, indent=2)
        
        student_example_input = """
        Sanskar Nalegaonkar
        Sophomore @ VIT Pune | Explorer of Tech & Ideas | Passionate About Data Science
        Experience:
        - Outreach Council Member, I2IOC - Training and Placement Cell, VIT Pune
        - Finance Coordinator, EPEC VIT PUNE
        Education:
        - Information Technology, Vishwakarma Institute Of Technology
        """
        
        student_example_output = json.dumps({
            "name": "Sanskar Nalegaonkar",
            "company": "VIT Pune",
            "role": "Sophomore - Information Technology Student",
            "industry": "Education / Technology",
            "seniority": "Student",
            "education": ["Information Technology, Vishwakarma Institute Of Technology"],
            "certifications": [],
            "recent_activity": [],
            "psychological_profile": {
                "decision_authority": "Low",
                "pain_points": ["Learning new skills", "Building experience", "Career preparation"],
                "goals": ["Gain practical experience", "Build portfolio", "Network with professionals"],
                "communication_preference": "Enthusiastic"
            },
            "communication_style": {
                "formality": "Casual",
                "tone": "Eager",
                "vocabulary": "Simple"
            },
            "key_insights": ["Active in college clubs", "Interested in Data Science"],
            "personalization_hooks": ["Mention club activities", "Discuss tech interests"]
        }, indent=2)
        
        # Add example showing combination of multiple sources
        combined_example_input = """
=== LINKEDIN PROFILE DATA ===
Sarah Jones
VP Marketing at CloudScale
Experience:
- VP Marketing, CloudScale (2020-Present)

=== RESUME / CV DATA ===
SARAH JONES
Education:
- MBA, Stanford University (2015)
- B.A. Communications, UCLA (2010)
Skills: Marketing Strategy, Data Analytics, Team Leadership
Certifications: Google Analytics Certified
"""
        
        combined_example_output = json.dumps({
            "name": "Sarah Jones",
            "company": "CloudScale",
            "role": "VP Marketing",
            "industry": "SaaS / Technology",
            "seniority": "Executive",
            "education": ["MBA, Stanford University (2015)", "B.A. Communications, UCLA (2010)"],
            "certifications": ["Google Analytics Certified"],
            "recent_activity": [],
            "psychological_profile": {
                "decision_authority": "High",
                "pain_points": ["Scaling growth", "Data-driven decisions"],
                "goals": ["Drive revenue", "Build high-performing teams"],
                "communication_preference": "Data-driven"
            },
            "communication_style": {
                "formality": "Professional",
                "tone": "Confident",
                "vocabulary": "Business-focused"
            },
            "key_insights": ["Strong educational background", "Experienced executive", "Analytics-focused"],
            "personalization_hooks": ["Mention Stanford MBA", "Discuss marketing analytics", "Reference leadership experience"]
        }, indent=2)

        user_prompt = f"""
EXAMPLE 1 - PROFESSIONAL:
Input:
{example_input}

Output:
{example_output}

EXAMPLE 2 - STUDENT:
Input:
{student_example_input}

Output:
{student_example_output}

EXAMPLE 3 - COMBINED SOURCES (LinkedIn + Resume):
Input:
{combined_example_input}

Output:
{combined_example_output}

NOW ANALYZE THIS PROFILE:
The following data may contain MULTIPLE SECTIONS (LinkedIn, Resume, Text Notes).
COMBINE all information about the SAME person into ONE comprehensive profile.

{cleaned_text[:8000]}

CRITICAL INSTRUCTIONS:
- MERGE information from ALL sections above
- If LinkedIn says "VP Marketing" and Resume adds "MBA Stanford", include BOTH
- Return ONLY valid JSON
- NEVER use null, use "Unknown" or empty array [] instead
- For students, use university as company
- Extract data only for the FIRST person mentioned (ignore sidebar suggestions)
- Fill all fields with information gathered from ALL provided sources

JSON OUTPUT:
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response_text = self.client.chat(messages, max_new_tokens=1500)
            
            # Debug: Log the raw response
            logger.info(f"LLM Response (first 300 chars): {response_text[:300]}")
            
            # Try to extract JSON
            json_res = self.client.extract_json(response_text)
            if json_res:
                logger.info("Successfully extracted JSON from response")
                # Clean up null values
                json_res = self._replace_nulls(json_res)
                return json_res
            
            # Fallback: Try to find JSON between ```json and ```
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    logger.info("Found JSON in markdown code block")
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # Try finding JSON after common prefixes
            for prefix in ["JSON OUTPUT:", "REAL JSON OUTPUT:", "Here is the JSON:", "```", "{", "Output:"]:
                if prefix in response_text:
                    after_prefix = response_text[response_text.find(prefix) + len(prefix):].strip()
                    try:
                        parsed = json.loads(after_prefix.split("```")[0].strip())
                        logger.info(f"Successfully parsed JSON after finding prefix: {prefix}")
                        return parsed
                    except:
                        continue
            
            # Last resort: try to parse the whole response
            try:
                cleaned = response_text.strip().replace("```json", "").replace("```", "").strip()
                parsed = json.loads(cleaned)
                logger.info("Successfully parsed cleaned response")
                return parsed
            except:
                pass
            
            # If all parsing fails, create a basic profile from the text
            logger.warning("All JSON parsing failed, creating minimal profile from text")
            
            # Extract basic info with regex as fallback
            name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', cleaned_text, re.MULTILINE)
            
            # Try to find role/headline (usually comes after name)
            lines = cleaned_text.split('\n')
            name = "Unknown"
            role = "Unknown"
            company = "Unknown"
            
            if name_match:
                name = name_match.group(1).strip()
                # Role is usually the next substantive line after the name
                for i, line in enumerate(lines):
                    if name in line and i + 1 < len(lines):
                        potential_role = lines[i + 1].strip()
                        if len(potential_role) > 10 and '@' in potential_role:
                            # Format: "Role @ Company"
                            parts = potential_role.split('@')
                            role = parts[0].strip() if len(parts) > 0 else "Unknown"
                            company = parts[1].strip() if len(parts) > 1 else "Unknown"
                        elif len(potential_role) > 10:
                            role = potential_role
                        break
            
            fallback_profile = {
                "name": name,
                "company": company,
                "role": role,
                "industry": "Unknown",
                "seniority": "Unknown",
                "education": [],
                "certifications": [],
                "recent_activity": [],
                "psychological_profile": {
                    "decision_authority": "Unknown",
                    "pain_points": ["Business growth"],
                    "goals": ["Professional development"],
                    "communication_preference": "Professional"
                },
                "communication_style": {
                    "formality": "Professional",
                    "tone": "Friendly",
                    "vocabulary": "Standard"
                },
                "key_insights": ["Professional with experience"],
                "personalization_hooks": ["Industry expertise"],
                "error_note": "⚠️ Limited data - LLM response could not be parsed properly. Using basic extraction.",
                "raw_response_preview": response_text[:200]
            }
            
            return fallback_profile
            
        except Exception as e:
            logger.error(f"Analysis failed with exception: {e}")
            return {"error": f"Analysis failed: {str(e)}. Please check your LLM endpoint connection."}
