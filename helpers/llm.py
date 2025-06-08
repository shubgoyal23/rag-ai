from ast import List
import os
from openai import OpenAI

from helpers.milvus import search_similar_text

client = OpenAI()

def create_embedding(text: str) -> List[str]:
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    search_results = search_similar_text(
        query=embedding.data[0].embedding
    )
    return search_results
 
def chat_completion(query: str, SYSTEM_PROMPT: str):
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )
    return chat_completion.choices[0].message.content