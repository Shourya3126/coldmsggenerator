# Template Editing + Regeneration Feature

## Overview
The Template Editing + Regeneration feature allows you to create, manage, and use custom message templates to control the tone, style, and approach of your AI-generated outreach messages.

## Features

### 1. **Pre-built Templates**
The system comes with 5 default templates:
- **Professional & Direct**: Straightforward, business-focused approach
- **Warm & Conversational**: Friendly, relationship-focused approach
- **Problem-Agitation-Solution**: Highlight pain points and present solution
- **Question-Based Opener**: Start with thought-provoking questions
- **Value-First**: Lead with free value before making asks

### 2. **Template Management**
Access the **Templates** tab to:
- **View Templates**: Browse all available templates with detailed information
- **Create New Template**: Design custom templates with specific:
  - Style instructions
  - Tone guidelines
  - Message length rules
  - Personalization levels
  - CTA (Call-to-Action) styles
- **Edit Template**: Modify existing templates
- **Delete Template**: Remove templates you no longer need

### 3. **Template Selection**
In the **New Campaign** tab:
- Select a template before analyzing a prospect
- The AI will generate messages following the template's guidelines
- Templates are automatically marked as "recently used"

### 4. **Regeneration**
After generating messages:
- Use the **🎨 Regenerate with Template** dropdown to select a different template
- Click **Regenerate** to create new messages with the selected style
- Instantly compare different approaches without re-analyzing the prospect

### 5. **A/B Testing with Templates**
- The A/B variant feature now respects your selected template
- Generate variant B using the same template for consistent style testing

## How to Use

### Creating a Custom Template

1. Go to the **Templates** tab
2. Select **Create New Template**
3. Fill in the form:
   - **Template ID**: Unique identifier (e.g., `my_custom_style`)
   - **Name**: Display name (e.g., "My Custom Style")
   - **Description**: When to use this template
   - **Style Instructions**: Detailed guidelines for the AI (bullet points work well)
   - **Message Length**: Guidelines for message length
   - **Tone**: Desired tone (e.g., "professional", "casual", "urgent")
   - **Personalization Level**: How much to personalize
   - **CTA Style**: Type of call-to-action
4. Click **Create Template**

### Using a Template

1. In the **New Campaign** tab, select your desired template from the dropdown
2. Continue with your normal workflow (scrape LinkedIn, upload resume, or paste text)
3. The generated messages will follow your template's style

### Regenerating with Different Templates

1. After generating messages, scroll to the **Generated Messages** section
2. In the **🎨 Regenerate with Template** dropdown, select a different template
3. Click **Regenerate**
4. The system will create new messages instantly using the new template

## Template Structure

Each template contains:
- **name**: Display name
- **description**: Purpose and use case
- **style_instructions**: Detailed AI instructions
- **message_length**: Length guidelines
- **tone**: Tone specifications
- **personalization_level**: How much to personalize
- **cta_style**: Call-to-action approach
- **created_at**: Creation timestamp
- **last_used**: Last usage timestamp

## Tips for Creating Effective Templates

1. **Be Specific**: Clear instructions lead to better results
2. **Use Examples**: Include examples in style instructions
3. **Test Variations**: Create multiple templates for different scenarios
4. **Iterate**: Edit templates based on what works
5. **Document Use Cases**: Write clear descriptions so you remember when to use each template

## Technical Details

- Templates are stored in `templates.json` in the root directory
- The `TemplateManager` class handles all CRUD operations
- Templates integrate with the message generation pipeline
- Template data is passed to the LLM to customize system prompts

## Files Modified/Added

### New Files:
- `logic/templates.py` - Template management system

### Modified Files:
- `app.py` - Added template UI and selection
- `logic/generator.py` - Added template support in generation

## Example Template

```json
{
  "name": "Consultative Expert",
  "description": "Position yourself as a trusted advisor offering insights",
  "style_instructions": "
- Lead with a valuable insight or observation
- Ask consultative questions
- Show expertise through the value provided
- Build credibility before any pitch
- Use collaborative language (\"we\", \"together\")
  ",
  "message_length": "6-8 lines for short channels, 10-12 lines for email",
  "tone": "Expert, consultative, collaborative, helpful",
  "personalization_level": "High - demonstrate deep understanding of their challenges",
  "cta_style": "Invitation to explore solutions together"
}
```

## Benefits

1. **Consistency**: Maintain consistent messaging across campaigns
2. **Flexibility**: Quickly adapt style for different audiences
3. **Speed**: Regenerate without re-analyzing prospects
4. **Control**: Fine-tune AI output to match your brand voice
5. **Testing**: Easily A/B test different approaches

## Future Enhancements

Potential additions:
- Template categories/tags
- Template sharing/export
- Performance tracking per template
- Template recommendations based on prospect type
- Template versioning

---

**Need Help?** Check the existing templates for examples or experiment with the default templates to understand the system before creating custom ones.
