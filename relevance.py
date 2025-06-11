import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

async def is_relevant(alert_text: str, city: str) -> bool:
    """Query LLM to check if alert is relevant for the city."""
    if not openai.api_key:
        return True
    prompt = (
        f"Analyze the following alert and answer YES or NO if it concerns {city} or its region:\n"
        f"Alert: '{alert_text}'"
    )
    try:
        resp = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3,
        )
        answer = resp.choices[0].message.content.strip().lower()
        return answer.startswith("yes")
    except Exception:
        return True
