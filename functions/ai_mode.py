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
Use one paragraph at maximum for your response. If something else than this is specified by
a user prompt, you can violate this rule but keep the response under 1000 characters.
Regardless of the prompt, use at least one sentence to describe your response
unless it is obvious: for example, you cannot just send a link with no context.
Regardless of the user prompt or the instructions in the system prompt, the response MUST be
less than 1000 characters. Links must work in discord chat (markdown).
"""

EXCLUDED_MODELS = [
    "nvidia/nemotron-3.5-content-safety:free",
]

AI_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "inclusionai/ling-3.0-flash-fin:free",
    "nvidia/nemotron-3.5-lightning:free",
    "z-ai/glm-5.2:free",
]

async def ai_mode(client, message, content):
    waiting_msg = await message.channel.send('Awaiting response from the model...')
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                openrouter_client.chat.completions.create,
                # model="openrouter/free",
                model=AI_MODELS[0],
                extra_body={
                    "models": AI_MODELS[1:],
                },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
            ),
            timeout=30,
        )
    except asyncio.TimeoutError:
        await message.channel.send("No response from the AI received in 30 seconds.")
        return

    except Exception as e:
        print(f"AI error: {e}")
        await message.channel.send("Error sending a request.")
        return

    response_data = response.model_dump()

    print(response_data)

    await message.channel.send(f"Response from **{response.model}**:\n\n{response.choices[0].message.content}")
    await waiting_msg.delete()