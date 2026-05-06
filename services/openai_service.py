import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])


def analyze_deck(pdf_path: str) -> dict:
    from apps.setup.models import Prompt
    system_prompt = Prompt.objects.get(key='system_prompt').body
    user_prompt = Prompt.objects.get(key='user_prompt').body

    with open(pdf_path, 'rb') as f:
        uploaded_file = client.files.create(file=f, purpose='assistants')

    file_id = uploaded_file.id

    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': user_prompt},
                    {'type': 'file', 'file': {'file_id': file_id}},
                ],
            },
        ],
    )

    raw = response.choices[0].message.content.strip()
    result = json.loads(raw)
    result['openai_file_id'] = file_id
    return result
