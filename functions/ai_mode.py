import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
from openai import OpenAI

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
)

system_prompt = """
If asked for a link, find a real one rather than generate it.
"""

async def ai_mode(client, message, content):
    waiting_msg = await message.channel.send('Awaiting response from the model...')
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                openrouter_client.chat.completions.create,
                model="openrouter/free",
                messages=[
                    {
                        "role": "user",
                        "content": content + ". Use one paragraph at maximum.",
                    }
                ],
            ),
            timeout=10,
        )
    except asyncio.TimeoutError:
        await message.channel.send("No response from the AI received in 10 seconds.")
        return

    except Exception as e:
        print(f"AI error: {e}")
        await message.channel.send("Error sending a request.")
        return

    response_data = response.model_dump()

    print(response_data)

    await message.channel.send(f"Response from **{response.model}**:\n\n{response.choices[0].message.content}")
    await waiting_msg.delete()