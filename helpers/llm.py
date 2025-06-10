from typing import List
from openai import OpenAI

client = OpenAI()

def create_embedding(text: List[str]) -> List[str]:
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return embedding.data
 
def chat_completion(query: str, SYSTEM_PROMPT: str):
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )
    return chat_completion.choices[0].message.content