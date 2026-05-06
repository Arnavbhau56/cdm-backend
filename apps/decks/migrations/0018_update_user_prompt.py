from django.db import migrations

NEW_USER_PROMPT = """Analyze the attached pitch deck and return this exact JSON structure:

{
  "startup_name": "The exact brand/trading name of the startup as it appears in the deck.",

  "registered_name": "The legal registered company name (e.g. Acme Technologies Private Limited). Search the entire deck — footer text, legal notices, incorporation details, about pages, team slides, any mention of 'Pvt Ltd', 'Private Limited', 'Inc', 'LLC', 'LLP'. If not explicitly stated, infer from the brand name by appending the most likely legal suffix for the country of incorporation (e.g. 'Private Limited' for India). Never return empty string — always return your best inference.",

  "website": "The official website URL of the startup (e.g. https://www.example.com). Search the entire deck — cover slide, footer, contact page, team slide, QR codes, any URL shown. If not found in the deck, infer the most likely URL from the startup name (e.g. startupname.com or startupname.in for Indian startups). Never return empty string.",

  "sector": "Primary sector label only (e.g. Fintech or Healthtech or SaaS). Single label, no commas.",

  "sub_sector": "2-3 more specific sub-sector or theme tags, comma-separated (e.g. Lending, B2B, Embedded Finance).",

  "one_liner": "One crisp sentence (max 20 words) describing what the company does and for whom. No hype.",

  "founder_email": "Find up to 3 email addresses from the deck (founder, co-founder, or company contact). Return them as a newline-separated string in this exact format:\\n1. email1@example.com\\n2. email2@example.com\\n3. email3@example.com\\nIf fewer than 3 are found, fill the remaining slots with N/A. Example if only 1 found: '1. founder@startup.com\\n2. N/A\\n3. N/A'. If none found at all, return '1. N/A\\n2. N/A\\n3. N/A'.",

  "business_model": "Write a sharp investor-grade explanation of what the company does, who pays them, how revenue is generated, what customer workflow they fit into, why customers would switch from current alternatives, and what must happen for revenue to scale materially. Avoid generic wording.",

  "industry_context": {
    "value_chain_position": "Be precise and layered. First name the macro industry (e.g. Fintech). Then name the sub-vertical within it (e.g. WealthTech > Retail Investment Platforms). Then map the full value chain top-to-bottom: who are the upstream providers (data, infrastructure, capital, regulation), who are the platform/middleware layer, who are the product/distribution layer, and who are the end customers. State exactly which layer this startup occupies, what they depend on upstream, and who they compete with or displace at their layer. One paragraph, dense and specific.",
    "market_size": "Give the India TAM and SAM with real numbers (cite the basis — e.g. RBI data, SEBI filings, industry reports, or your own bottom-up reasoning). Then give the global comparable market size. State the current penetration rate and the realistic addressable opportunity for a startup at this stage. Do not use vague ranges — give a specific number and explain how you arrived at it.",
    "market_timing": "What structural shifts — regulatory, technological, demographic, or behavioural — are creating the window right now? Name 2-3 specific tailwinds with dates or data points where possible. Also name 1 headwind or timing risk that could slow adoption.",
    "competitive_landscape": {
      "market_structure": "One paragraph: is this market fragmented or consolidated, winner-take-all or multi-player? Where does this startup sit relative to incumbents — attacking from below, above, or a different axis?",
      "competitors_india": [
        { "name": "Company name", "description": "What they do", "scale": "Revenue / users / funding if known", "relevance": "Direct competitor / indirect / adjacent" },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." }
      ],
      "competitors_global": [
        { "name": "Company name", "description": "What they do", "scale": "Revenue / users / funding if known", "relevance": "What happened to them / are they entering India" },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." }
      ],
      "trends": [
        { "trend": "Trend name", "detail": "What is happening, why it matters for this space, and how it affects this startup specifically" },
        { "trend": "...", "detail": "..." },
        { "trend": "...", "detail": "..." }
      ]
    },
    "unit_economics": "What are the typical gross margins in this sub-sector and why? What does a healthy CAC:LTV ratio look like here? What is the typical payback period? What does the P&L of a scaled player in this space look like? If this startup's model implies different economics, flag the assumption.",
    "regulatory": "List the specific regulatory bodies, licenses, and compliance requirements relevant to this business in India. Note any recent regulatory changes that help or hurt this model. Flag any regulatory risk not addressed in the deck.",
    "failure_modes": "Name 2-3 real companies in this space (India or global) that failed or struggled and explain precisely why. What assumptions do founders in this space consistently get wrong?",
    "winners_playbook": "What have the 1-2 category leaders in this space done that others have not? Is the moat distribution, data network effects, regulatory capture, product depth, or pricing? What does the path to category leadership look like?"
  },

  "key_risks": [
    "Risk 1 — Explain the precise mechanism of risk. Reference specific claims, omissions, metrics, GTM assumptions, competition, unit economics, legal structure, founder dependency, or unclear evidence from the deck.",
    "Risk 2...",
    "Risk 3...",
    "Risk 4...",
    "Risk 5..."
  ],

  "founder_questions": [
    {"question": "Question 1 — highest priority legal / structural / ownership / compliance issue based on the deck", "answer": ""},
    {"question": "Question 2 — challenge a core business model assumption using something specific in the deck", "answer": ""},
    {"question": "Question 3 — ask about product differentiation vs current alternatives or competitors", "answer": ""},
    {"question": "Question 4 — ask about traction quality, retention, cohort, or revenue proof", "answer": ""},
    {"question": "Question 5 — ask about GTM efficiency or customer acquisition model", "answer": ""},
    {"question": "Question 6 — ask about scalability or operational bottlenecks", "answer": ""},
    {"question": "Question 7 — ask about why now / market timing", "answer": ""},
    {"question": "Question 8 — ask about fundraising use of funds or milestones", "answer": ""},
    {"question": "Question 9 — ask about next critical execution risk", "answer": ""},
    {"question": "Question 10 — any sharp investor diligence question triggered by the deck", "answer": ""}
  ]
}

Rules:
- registered_name and website must NEVER be empty — always infer if not explicitly stated.
- founder_email must always be in the 3-line numbered format with N/A for missing slots.
- Think deeply before answering. Prefer insight over repetition.
- Use evidence from the deck wherever possible.
- business_model must be specific, nuanced, and useful to an investor unfamiliar with the sector.
- industry_context is a JSON object with 8 keys. Every text field must be substantive — minimum 3-4 sentences. competitive_landscape must contain real named companies with actual scale/funding data. trends must contain 3-5 items.
- key_risks must contain 4–5 items only. Each should be concrete, non-generic, and tied to this deck.
- founder_questions must contain 7–10 items only, each as {"question":"","answer":""}.
- Order founder_questions by investment priority: legal/structure first, then business model truth-testing, then traction, then growth.
- Return only raw JSON. No markdown fences. No text before or after the JSON."""


def update_user_prompt(apps, schema_editor):
    Prompt = apps.get_model('setup', 'Prompt')
    Prompt.objects.filter(key='user_prompt').update(body=NEW_USER_PROMPT)


class Migration(migrations.Migration):
    dependencies = [
        ('decks', '0017_deck_website_email_text'),
    ]

    operations = [
        migrations.RunPython(update_user_prompt, reverse_code=migrations.RunPython.noop),
    ]
