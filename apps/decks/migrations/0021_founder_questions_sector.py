from django.db import migrations

NEW_USER_PROMPT = """Analyze the attached pitch deck and return this exact JSON structure:

{
  "startup_name": "The exact brand/trading name of the startup as it appears in the deck.",

  "registered_name": "The legal registered company name (e.g. Acme Technologies Private Limited). Search the entire deck — footer text, legal notices, incorporation details, about pages, team slides, any mention of 'Pvt Ltd', 'Private Limited', 'Inc', 'LLC', 'LLP'. If not explicitly stated, infer from the brand name by appending the most likely legal suffix for the country of incorporation (e.g. 'Private Limited' for India). Never return empty string — always return your best inference.",

  "website": "The official website URL of the startup (e.g. https://www.example.com). Search the entire deck — cover slide, footer, contact page, team slide, QR codes, any URL shown. If not found in the deck, infer the most likely URL from the startup name (e.g. startupname.com or startupname.in for Indian startups). Never return empty string.",

  "sector": "Primary sector label only (e.g. Fintech or Healthtech or SaaS). Single label, no commas.",

  "sub_sector": "2-3 more specific sub-sector or theme tags, comma-separated (e.g. Lending, B2B, Embedded Finance).",

  "one_liner": "One crisp sentence (max 20 words) describing what the company does and for whom. No hype.",

  "founder_email_1": "First email address found in the deck (founder, co-founder, or company contact). If not found, return 'N/A'.",

  "founder_email_2": "Second email address found in the deck. If not found, return 'N/A'.",

  "founder_email_3": "Third email address found in the deck. If not found, return 'N/A'.",

  "business_model": "Write a sharp investor-grade explanation of what the company does, who pays them, how revenue is generated, what customer workflow they fit into, why customers would switch from current alternatives, and what must happen for revenue to scale materially. Avoid generic wording.",

  "industry_context": {
    "value_chain_position": "Be precise and layered. First name the macro industry. Then name the sub-vertical. Then map the full value chain top-to-bottom. State exactly which layer this startup occupies. One paragraph, dense and specific.",
    "market_size": "Give the India TAM and SAM with real numbers. Then give the global comparable market size. State the current penetration rate and the realistic addressable opportunity for a startup at this stage.",
    "market_timing": "What structural shifts are creating the window right now? Name 2-3 specific tailwinds with dates or data points. Also name 1 headwind or timing risk.",
    "competitive_landscape": {
      "market_structure": "One paragraph: is this market fragmented or consolidated, winner-take-all or multi-player?",
      "competitors_india": [
        { "name": "Company name", "description": "What they do", "scale": "Revenue / users / funding if known", "relevance": "Direct competitor / indirect / adjacent" }
      ],
      "competitors_global": [
        { "name": "Company name", "description": "What they do", "scale": "Revenue / users / funding if known", "relevance": "What happened to them / are they entering India" }
      ],
      "trends": [
        { "trend": "Trend name", "detail": "What is happening and how it affects this startup" }
      ]
    },
    "unit_economics": "Typical gross margins, CAC:LTV ratio, payback period, dominant cost lines. Flag if this startup's model implies different economics.",
    "regulatory": "Specific regulatory bodies, licenses, compliance requirements in India. Recent regulatory changes. Flag any unaddressed regulatory risk.",
    "failure_modes": "2-3 real companies in this space that failed and precisely why. What assumptions do founders consistently get wrong?",
    "winners_playbook": "What have the 1-2 category leaders done that others have not? What does the path to category leadership look like?"
  },

  "key_risks": [
    "Risk 1 — precise mechanism tied to this deck.",
    "Risk 2...",
    "Risk 3...",
    "Risk 4...",
    "Risk 5..."
  ],

  "founder_questions": [
    {"question": "Question about legal structure, cap table, or compliance", "answer": "", "sector": "Others and Legal and Compliance"},
    {"question": "Question challenging a core business model assumption", "answer": "", "sector": "Business Model"},
    {"question": "Question about product differentiation vs alternatives", "answer": "", "sector": "Problem and Product"},
    {"question": "Question about traction quality, retention, or revenue proof", "answer": "", "sector": "Financials and Traction"},
    {"question": "Question about GTM efficiency or customer acquisition", "answer": "", "sector": "Market and GTM"},
    {"question": "Question about scalability, tech stack, or operational bottlenecks", "answer": "", "sector": "Growth and Technology"},
    {"question": "Question about why now / market timing", "answer": "", "sector": "Market and GTM"},
    {"question": "Question about fundraising use of funds or milestones", "answer": "", "sector": "Financials and Traction"},
    {"question": "Question about the core problem and whether it is acute enough", "answer": "", "sector": "Problem and Product"},
    {"question": "Sharp investor diligence question triggered by the deck", "answer": "", "sector": "Business Model"}
  ]
}

Rules:
- registered_name and website must NEVER be empty — always infer if not explicitly stated.
- founder_email_1/2/3: return the email string if found, or exactly 'N/A' if not found.
- key_risks: 4-5 items, concrete and tied to this deck.
- founder_questions: 7-10 items. Each item MUST have exactly three keys: "question", "answer" (always empty string ""), and "sector".
- The "sector" field on each question MUST be one of these exact values:
    "Problem and Product"
    "Business Model"
    "Market and GTM"
    "Financials and Traction"
    "Growth and Technology"
    "Others and Legal and Compliance"
  Assign the sector that best fits the question's focus. Do not invent other sector names.
- competitive_landscape: real named companies with actual scale/funding data. 5 india, 5 global, 3-5 trends.
- Return only raw JSON. No markdown fences. No text before or after the JSON."""


def update_prompt(apps, schema_editor):
    Prompt = apps.get_model('setup', 'Prompt')
    Prompt.objects.filter(key='user_prompt').update(body=NEW_USER_PROMPT)


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0020_merge_0018_update_user_prompt_0019_update_user_prompt'),
    ]

    operations = [
        migrations.RunPython(update_prompt, reverse_code=migrations.RunPython.noop),
    ]
