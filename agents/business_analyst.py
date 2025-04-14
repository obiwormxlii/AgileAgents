import json
from google import genai
from pydantic import BaseModel


class BAdocument(BaseModel):
    text: str
    document_text: str
    confidence: float
    document_generated: bool


def businessAnalyst(prompt, client, context=None) -> BAdocument:
    if context is not None:
        prompt = f"<context>{context}</context>\n{prompt}"
    reply = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BAdocument,
            "system_instruction": prompts["system"]["ba"],
        },
    )
    return json.loads(reply.text)
