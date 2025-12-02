import google.generativeai as genai
from .config import settings

genai.configure(api_key=settings.gemini_api_key)

model = genai.GenerativeModel("gemini-2.5-flash")   # or gemini-pro / gemini-1.5-pro

async def summarize_email(content: str) -> str:
    prompt = f"""
    Summarize the following email in 2-3 short sentences, keeping it professional and concise.
    Email:
    {content}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

async def generate_reply(email_content: str, extra_instruction: str | None = None) -> str:
    inst = extra_instruction or "Write a well-structured professional reply to this email."
    prompt = f"""
    {inst}

    Original email:
    {email_content}

    Reply:
    """
    response = model.generate_content(prompt)
    return response.text.strip()

async def daily_digest(emails: list[dict]) -> str:
    text = "\n\n".join(
        [f"From: {e['sender']}\nSubject: {e['subject']}\nBody: {e['body']}" for e in emails]
    )
    prompt = f"""
    Create a single daily digest summary for these emails. Include key points and recommended actions:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

async def categorize_emails(emails: list[dict]) -> dict:
    text = "\n\n".join(
        [f"Email {i+1}:\nFrom: {e['sender']}\nSubject: {e['subject']}\nBody: {e['body']}"
         for i, e in enumerate(emails)]
    )
    prompt = f"""
    Categorize the following emails into groups such as Work, Personal, Promotions, Urgent, Others.
    Respond in JSON format with categories as keys and lists of email numbers as values.
    {text}
    """
    response = model.generate_content(prompt)
    return response.text.strip()
