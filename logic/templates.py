import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages message generation templates with CRUD operations."""
    
    def __init__(self, templates_file="templates.json"):
        self.templates_file = templates_file
        self.templates = self._load_templates()
        
        # Create default templates if none exist
        if not self.templates:
            self._create_default_templates()
    
    def _load_templates(self):
        """Load templates from JSON file."""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load templates: {e}")
                return {}
        return {}
    
    def _save_templates(self):
        """Save templates to JSON file."""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save templates: {e}")
            return False
    
    def _create_default_templates(self):
        """Create default templates for common use cases."""
        
        # Template 1: Professional & Direct
        self.templates["professional_direct"] = {
            "name": "Professional & Direct",
            "description": "Straightforward, business-focused approach with clear value proposition",
            "style_instructions": """
- Be professional and direct
- Lead with value proposition
- Keep tone business-focused
- Use concrete data and metrics when possible
- Clear, specific call-to-action
            """,
            "message_length": "4-6 lines for short channels, 8-10 lines for email",
            "tone": "Professional, confident, results-oriented",
            "personalization_level": "Moderate - mention key achievements and pain points",
            "cta_style": "Direct ask for meeting/call",
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        # Template 2: Warm & Conversational
        self.templates["warm_conversational"] = {
            "name": "Warm & Conversational",
            "description": "Friendly, relationship-focused approach that builds rapport",
            "style_instructions": """
- Start with genuine compliment or shared interest
- Use conversational language (contractions, friendly tone)
- Build rapport before pitching
- Show authentic interest in their work
- Soft, low-pressure call-to-action
            """,
            "message_length": "5-7 lines for short channels, 10-12 lines for email",
            "tone": "Friendly, warm, authentic, relationship-focused",
            "personalization_level": "High - weave in personal details, interests, and recent activity",
            "cta_style": "Soft suggestion or question",
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        # Template 3: Problem-Agitation-Solution
        self.templates["problem_agitation"] = {
            "name": "Problem-Agitation-Solution",
            "description": "Highlight pain points, amplify urgency, then present solution",
            "style_instructions": """
- Open with a pain point they're likely facing
- Agitate by showing consequences or missed opportunities
- Present your solution as the answer
- Use emotional language that resonates with frustration
- Strong, urgent call-to-action
            """,
            "message_length": "5-7 lines for short channels, 9-11 lines for email",
            "tone": "Empathetic but urgent, solution-focused",
            "personalization_level": "High - identify specific pain points from their profile",
            "cta_style": "Urgent invitation to solve the problem",
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        # Template 4: Question-Based
        self.templates["question_based"] = {
            "name": "Question-Based Opener",
            "description": "Start with thought-provoking question to drive engagement",
            "style_instructions": """
- Open with a relevant, thought-provoking question
- Make them curious or self-reflective
- Follow up with context showing you understand their situation
- Present solution naturally as answer to the question
- CTA should be another question or invitation to discuss
            """,
            "message_length": "4-6 lines for short channels, 8-10 lines for email",
            "tone": "Curious, consultative, thought-provoking",
            "personalization_level": "High - question must be specific to their role/industry",
            "cta_style": "Question or invitation to explore further",
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        # Template 5: Value-First
        self.templates["value_first"] = {
            "name": "Value-First (Give Before Ask)",
            "description": "Lead with free value, insight, or resource before any ask",
            "style_instructions": """
- Start by offering something valuable for free (insight, resource, tip)
- Show expertise through the value you provide
- Build credibility before pitching
- Make the ask secondary to the value provided
- Low-pressure CTA that continues value exchange
            """,
            "message_length": "5-7 lines for short channels, 10-12 lines for email",
            "tone": "Generous, helpful, consultative, expert",
            "personalization_level": "Moderate to High - value must be relevant to their needs",
            "cta_style": "Offer more value or continue conversation",
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        self._save_templates()
        logger.info("Created default templates")
    
    def get_all_templates(self):
        """Get all templates."""
        return self.templates
    
    def get_template(self, template_id):
        """Get a specific template by ID."""
        return self.templates.get(template_id)
    
    def create_template(self, template_id, template_data):
        """Create a new template."""
        if template_id in self.templates:
            return False, "Template ID already exists"
        
        template_data["created_at"] = datetime.now().isoformat()
        template_data["last_used"] = None
        self.templates[template_id] = template_data
        
        if self._save_templates():
            return True, "Template created successfully"
        return False, "Failed to save template"
    
    def update_template(self, template_id, template_data):
        """Update an existing template."""
        if template_id not in self.templates:
            return False, "Template not found"
        
        # Preserve created_at
        template_data["created_at"] = self.templates[template_id].get("created_at", datetime.now().isoformat())
        self.templates[template_id] = template_data
        
        if self._save_templates():
            return True, "Template updated successfully"
        return False, "Failed to save template"
    
    def delete_template(self, template_id):
        """Delete a template."""
        if template_id not in self.templates:
            return False, "Template not found"
        
        del self.templates[template_id]
        
        if self._save_templates():
            return True, "Template deleted successfully"
        return False, "Failed to save templates"
    
    def mark_used(self, template_id):
        """Mark a template as recently used."""
        if template_id in self.templates:
            self.templates[template_id]["last_used"] = datetime.now().isoformat()
            self._save_templates()
    
    def get_template_names(self):
        """Get a list of template IDs and names for selection."""
        return {tid: t.get("name", tid) for tid, t in self.templates.items()}
