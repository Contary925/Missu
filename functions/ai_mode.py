import os
from dotenv import load_dotenv

load_dotenv()
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
from openai import OpenAI

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
)

async def ai_mode(client, message, content):
    response = openrouter_client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": "Have I successfully send a prompt to you? Use twenty words maximum.",
            }
        ],
    )
    await message.channel.send(f"Response from ...: {response}")