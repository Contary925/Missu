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
Refer to yourself as a female if required (i.e. for russian language responses, "нашла", not "нашёл".)
Never invent URLs, citations, release dates, or facts.
If you cannot verify something, say so explicitly.
Regardless of the prompt, use at least one sentence to describe your response
unless it is obvious: for example, you cannot just send a link with no context.
Regardless of the user prompt or the instructions in the system prompt, the response MUST be
less than 1000 characters. Links must work in discord chat (markdown).
The response must be sent within 20 seconds, so avoid search that's too deep to fit in.
"""

EXCLUDED_MODELS = [
    "nvidia/nemotron-3.5-content-safety:free",
]

AI_MODELS = [
    # "nvidia/nemotron-3-ultra-550b-a55b:free",
    # "inclusionai/ling-3.0-flash-fin:free",
    # "nvidia/nemotron-3.5-lightning:free",
    # "z-ai/glm-5.2:free",
    "deepseek/deepseek-v3.2",
]

async def ai_mode(client, message, content):
    waiting_msg = await message.channel.send('Awaiting response from the model...\nNote: please check important results before usage.\nProceed to press links with caution as they may not be safe.')
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                openrouter_client.chat.completions.create,
                # model="openrouter/free",
                model=AI_MODELS[0],
                extra_body={
                    "models": AI_MODELS[1:],
                     "tools": [
                {
                    "type": "openrouter:web_search",
                    "parameters": {
                        "engine": "parallel",
                        "mode": "basic",
                        "max_results": 3,
                        "max_total_results": 3,
                    },
                }
            ],
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