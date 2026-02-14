import requests
import json
import logging

logger = logging.getLogger(__name__)

from logic.llm_client import KaggleClient

class MessageGenerator:
    def __init__(self, llm_url="https://preocular-repudiatory-jeana.ngrok-free.dev"):
        self.client = KaggleClient(base_url=llm_url)

    def generate_campaign(self, profile_data, my_offering, context_prospects=None, variant_mode=False, template_data=None):
        """
        Generates 5-channel outreach messages based on the analyzed profile.
        If context_prospects is provided, uses them as "success stories".
        If variant_mode is True, generates an alternative "B" version.
        If template_data is provided, uses it to customize the generation style.
        """
        
        context_str = ""
        if context_prospects:
            company_raw = profile_data.get('company') if isinstance(profile_data, dict) else ''
            target_company = (company_raw or '').lower()
            
            # Build domain-aware social proof using match reasons from KB
            direct_refs = []   # Same company — strongest
            peer_refs = []     # Same career stage / college — bootcamp relevant
            industry_refs = [] # Same industry / similar role — general
            
            for p in context_prospects[:3]:
                name = p.get('name', 'someone')
                role = p.get('role', 'a professional')
                company = p.get('company', '')
                reasons = p.get('_match_reasons', [])
                
                if 'same_company' in reasons:
                    direct_refs.append({'name': name, 'role': role, 'company': company})
                elif 'similar_career_stage' in reasons or 'similar_skills' in reasons:
                    peer_refs.append({'name': name, 'role': role, 'company': company})
                elif 'same_industry' in reasons or 'similar_role' in reasons:
                    industry_refs.append({'name': name, 'role': role, 'company': company})
            
            parts = []
            
            # TIER 1: Same company = must reference
            if direct_refs:
                ref = direct_refs[0]
                parts.append(
                    f"DIRECT REFERENCE (USE THIS): We previously worked with "
                    f"{ref['name']} ({ref['role']}) at {ref['company']}. "
                    f"You MUST naturally mention this in email and LinkedIn — e.g., "
                    f"'We recently collaborated with {ref['name']} from your team at {ref['company']}...' or "
                    f"'Your colleague {ref['name']} already uses our solution...'. "
                    f"Keep it warm and natural."
                )
            
            # TIER 2: Same career stage / college = peer reference (bootcamp-style)
            if peer_refs:
                names = [f"{p['name']} ({p['company']})" if p['company'] and p['company'] != 'Unknown' 
                         else p['name'] for p in peer_refs]
                names_str = ", ".join(names)
                parts.append(
                    f"PEER REFERENCE (USE THIS): Students/professionals at a similar stage — "
                    f"{names_str} — have already benefited from our offering. "
                    f"You should reference this naturally — e.g., "
                    f"'Your batchmate {peer_refs[0]['name']} recently joined our program...' or "
                    f"'Students from {peer_refs[0].get('company', 'your college')} have found success with us...'. "
                    f"Make it feel relatable, like a peer recommendation."
                )
            
            # TIER 3: Same industry / similar role = soft reference
            if industry_refs:
                names = [f"{p['name']} ({p['role']} at {p['company']})" for p in industry_refs 
                         if p['company'] and p['company'] != 'Unknown']
                if names:
                    names_str = ", ".join(names)
                    parts.append(
                        f"SOFT REFERENCE (optional): Professionals in similar roles — "
                        f"{names_str} — have connected with us. "
                        f"Mention subtly if relevant, e.g., 'Engineers at {industry_refs[0]['company']} have used our platform...'."
                    )
            
            if parts:
                context_str = "\nSOCIAL PROOF FROM KNOWLEDGE BASE:\n" + "\n".join(parts)

        variant_instruction = ""
        if variant_mode:
            variant_instruction = "\n\nIMPORTANT: This is an A/B test variant. Try a DIFFERENT angle than usual (e.g., if you usually lead with value, lead with a question, or be more direct)."

        # Build template-specific instructions
        template_instruction = ""
        message_length_rule = "4-5 lines minimum (not counting greeting/signature)"
        tone_rule = "Professional yet conversational"
        personalization_rule = "Weave them into a narrative"
        cta_rule = "Clear next step"
        
        if template_data:
            template_name = template_data.get("name", "Custom Template")
            template_instruction = f"\n=== TEMPLATE: {template_name} ===\n"
            template_instruction += f"DESCRIPTION: {template_data.get('description', '')}\n"
            template_instruction += f"\nSTYLE GUIDELINES:\n{template_data.get('style_instructions', '')}\n"
            
            # Override defaults with template specs
            message_length_rule = template_data.get("message_length", message_length_rule)
            tone_rule = template_data.get("tone", tone_rule)
            personalization_rule = template_data.get("personalization_level", personalization_rule)
            cta_rule = template_data.get("cta_style", cta_rule)

        system_prompt = f"""
        You are a world-class SDR and Copywriter.
        Your task is to generate hyper-personalized outreach messages that feel warm and well-researched.
        {template_instruction}
        
        ╔═══════════════════════════════════════════════════════════════╗
        ║  OFFERING CONTEXT (THIS IS WHAT YOU ARE SELLING - USE THIS!) ║
        ╚═══════════════════════════════════════════════════════════════╝
        "{my_offering}"
        
        🚨 CRITICAL ANTI-HALLUCINATION RULES:
        1. YOU MUST use the OFFERING CONTEXT above in your messages. Do NOT make up products, services, or companies.
        2. DO NOT mention "DevOps", "infrastructure", "AWS", "talent platform", or ANY other service unless it's explicitly in the OFFERING CONTEXT.
        3. The example below uses "AI-driven talent platform" - THIS IS JUST AN EXAMPLE. Replace it with the actual OFFERING CONTEXT.
        4. Connect the prospect's profile to the OFFERING CONTEXT specifically. Explain why YOUR offering (from context) helps THEIR situation.
        
        GENERATION RULES:
        1. MESSAGE LENGTH: {message_length_rule}
           - Each message should be comprehensive and compelling. Do NOT generate 1-liners.
        2. PERSONALIZATION: {personalization_rule}
        3. OFFERING INTEGRATION: Bridge prospect's details (pain points, activity) with the OFFERING CONTEXT above. Make it specific to them.
        4. TONE: {tone_rule}
        5. CALL TO ACTION: {cta_rule}
        {variant_instruction}
        {context_str}
        """

        example_profile = json.dumps({
            "name": "Sarah Jones",
            "company": "CloudScale",
            "role": "VP Marketing",
            "education": ["MBA, Stanford"],
            "certifications": ["Google Analytics"],
            "recent_activity": ["Posted about AI in Marketing"],
            "psychological_profile": {"pain_points": ["Scaling growth", "Data overload"]},
            "key_insights": ["Loves hiking"],
            "personalization_hooks": ["Mention Stanford", "Discuss AI post"]
        }, indent=2)

        example_output = json.dumps({
            "email": {
                "subject": "Thoughts on your AI post + Stanford connection?",
                "body": "Hi Sarah,\n\nI was just reading your recent post about AI in Marketing - couldn't agree more about the need for automation. It's clear you're forward-thinking.\n\nNoticed you're a Stanford MBA grad as well (impressive program). That rigorous analytical background really shows in your strategic approach.\n\nGiven your focus on scaling growth at CloudScale and handling data overload, our AI-driven talent platform can help you build the right team to execute that vision without the headache.\n\nWould you be open to a quick chat next Tuesday about how we can support your scaling efforts?"
            },
            "linkedin": "Hi Sarah, loved your thoughts on AI in Marketing. As a fellow data-nerd (saw your Google Analytics cert!), I wanted to connect.\n\nI see you're tackling growth scaling at CloudScale. It's a tough challenge, but crucial.",
            "whatsapp": "Hi Sarah, saw your post on AI. We're building something similar for scaling teams...\n\nYour background at Stanford suggests you value high-leverage tools. Our platform aligns perfectly with that philosophy.\n\nWe help leaders like you cut through the noise and find top-tier talent instantly.\n\nWould love to send over a case study if you're interested? Let me know!",
            "sms": "Sarah, quick question about your AI post. It really resonated with our team's mission.\n\nWe specialize in helping VPs like you scale growth without the burnout.\n\nGiven your focus on efficiency, I think our solution could be a game-changer for CloudScale.\n\nFree for a 5-min call this week to discuss strategies?",
            "instagram": "Hey Sarah, huge fan of your content on AI - it's spot on!\n\nI noticed you're also into hiking; that's awesome. We believe in work-life balance too.\n\nAt our core, we help marketing leaders automate the heavy lifting so they can focus on strategy (and trails!).\n\nCheck out our link if you need help scaling your team effectively.",
            "analysis": {
                "personalization_score": "9.5/10",
                "reasoning": "weaved in post + education + certs naturally."
            }
        }, indent=2)

        user_prompt = f"""
        IMPORTANT REMINDER: The example below is ONLY for format reference. DO NOT copy the offering from the example.
        You MUST use the OFFERING CONTEXT from the system prompt in your actual messages.
        
        EXAMPLE INPUT PROFILE (for format reference only):
        {example_profile}
        
        EXAMPLE JSON OUTPUT (for format reference only - DO NOT copy the offering):
        {example_output}
        
        ═══════════════════════════════════════════════════════════
        NOW GENERATE FOR THE REAL PROFILE BELOW:
        ═══════════════════════════════════════════════════════════
        
        REAL INPUT PROFILE:
        {json.dumps(profile_data, indent=2)}
        
        Remember: Use the OFFERING CONTEXT from the system prompt, NOT the example offering!
        
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
                # Add offering validation warning
                json_res = self._add_offering_validation(json_res, my_offering)
                return json_res

            # Fallback or return raw text if that's what we got (though analyzer expects dict)
            return {"error": "Failed to parse JSON response", "raw_response": response_text}
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {"error": str(e)}
    
    def _add_offering_validation(self, generated_messages, offering_context):
        """
        Add a validation warning if generated content doesn't seem to match the offering.
        This helps detect hallucinations.
        """
        # Common hallucination keywords that shouldn't appear unless in offering
        hallucination_keywords = [
            "devops", "infrastructure", "aws", "cloud services", "terraform",
            "kubernetes", "docker", "ci/cd pipeline", "jenkins", 
            "talent platform", "recruitment", "hiring platform"
        ]
        
        offering_lower = offering_context.lower()
        
        # Get all message text
        all_text = ""
        if isinstance(generated_messages, dict):
            email_body = generated_messages.get("email", {}).get("body", "") if isinstance(generated_messages.get("email"), dict) else ""
            linkedin = generated_messages.get("linkedin", "")
            all_text = (email_body + " " + linkedin).lower()
        
        # Check for hallucinations
        hallucinated_terms = []
        for keyword in hallucination_keywords:
            if keyword in all_text and keyword not in offering_lower:
                hallucinated_terms.append(keyword)
        
        # Add warning if hallucinations detected
        if hallucinated_terms:
            if "analysis" not in generated_messages:
                generated_messages["analysis"] = {}
            generated_messages["analysis"]["offering_alignment_warning"] = (
                f"⚠️ Detected terms not in offering: {', '.join(hallucinated_terms)}. "
                "Please verify the message aligns with your actual offering."
            )
            logger.warning(f"Possible hallucination detected: {hallucinated_terms}")
        
        return generated_messages
