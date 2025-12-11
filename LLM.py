# LLM.py
import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load variables from .env in the project root
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL" ,"openai/gpt-oss-120b")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set. Check your .env file.")

client = Groq(api_key=GROQ_API_KEY)


def medi_Extract(prescription_text: str):
    """
    Use Groq LLM to extract ONLY medicine/injection/saline names
    from raw prescription text.
    Returns a list of strings.
    """
    if not prescription_text or not prescription_text.strip():
        return []

    prompt = f"""
You are a medical prescription parser.

From the text below, extract ONLY the names of medicines, injections,
or saline solutions prescribed.

Rules:
- Return UNIQUE medication names only.
- Do NOT include dose, strength, route, frequency or quantity.
- Ignore headings, allergies, diagnosis, physician info, dates, etc.
- If a line has "Vitamin € ", return just "Vitamin C".
- Output MUST be valid JSON in exactly this format:

{{
  "medications": ["name1", "name2", "name3"]
}}

Here is the text:

\"\"\"{prescription_text}\"\"\"
"""

    chat_completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = chat_completion.choices[0].message.content

    meds: list[str] = []

    try:
        data = json.loads(content)
        raw = data.get("medications", [])
        if isinstance(raw, str):
            meds = [raw.strip()] if raw.strip() else []
        elif isinstance(raw, list):
            meds = [str(m).strip() for m in raw if str(m).strip()]
    except json.JSONDecodeError:
        # Fallback: parse as simple list
        for line in content.splitlines():
            line = line.strip().strip("-•,*")
            if line:
                meds.append(line)

    # Deduplicate (case-insensitive)
    seen = set()
    unique_meds = []
    for m in meds:
        key = m.lower()
        if key not in seen:
            seen.add(key)
            unique_meds.append(m)

    return unique_meds
