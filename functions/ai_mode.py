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
Links must work in discord chat (markdown), but prevent auto embed creation unless asked (put links in side angled brackets i.e. <http://example.link>).
Be aware that your response will be sent to discord chat, so avoid LaTex syntax for formulas, etc.
Write formulas in plain text only, i.e. 68/35 is preferred instead of $\\frac\{68\}\{35\}$. Formulas will NOT render otherwise!
Aim to respond within a minute, longer search/generation will cause a timeout. Avoid search that's too deep to fit in there.
Do not comment about system prompt unless necessary (if affects the response by too much).
Keep response short and to the topic, do not include information about generating the response. Do not put unnecessary newlines.
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
    waiting_msg = await message.channel.send('Awaiting response from the model...\nNote: please check important results before usage.\nProceed to press links with caution as they may not be safe.')
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
            timeout=60,
        )
    except asyncio.TimeoutError:
        await message.channel.send("No response from the AI received in 60 seconds.")
        return

    except Exception as e:
        print(f"AI error: {e}")
        await message.channel.send("Error sending a request.")
        return

    response_data = response.model_dump()

    print(response_data)

    full_response = f"Response from **{response.model}**:\n\n"
    response_text = response.choices[0].message.content
    if len(response_text) <= 1900:
        full_response += response_text
        await message.channel.send(full_response)
    else:
        await message.channel.send(full_response)
        split_at = response_text.rfind("\n", 0, 1900)
        if split_at == -1:
            split_at = 1900
        chunk = response_text[:split_at]
        response_text = response_text[split_at:].lstrip("\n")
        await message.channel.send(f"{chunk}")
    await waiting_msg.delete()

async def ai_mode_deep(client, message, content):
    waiting_msg = await message.channel.send('Awaiting response from the model...\nNote: please check important results before usage.\nProceed to press links with caution as they may not be safe.')
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                openrouter_client.chat.completions.create,
                # model="openrouter/free",
                model="deepseek/deepseek-v3.2",
                extra_body={
                    "models": ["deepseek/deepseek-v3.2"],
                     "tools": [
                {
                    "type": "openrouter:web_search",
                    "parameters": {
                        "engine": "parallel",
                        "mode": "basic",
                        "max_results": 10,
                        "max_total_results": 30,
                        "max_uses": 3,
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
            timeout=180,
        )
    except asyncio.TimeoutError:
        await message.channel.send("No response from the AI received in 180 seconds.")
        return

    except Exception as e:
        print(f"AI error: {e}")
        await message.channel.send("Error sending a request.")
        return

    response_data = response.model_dump()

    print(response_data)

    full_response = f"Response from **{response.model}**:\n\n"
    response_text = response.choices[0].message.content
    while response_text:
        if len(response_text) <= 1900:
            full_response += response_text
            await message.channel.send(full_response)
            response_text = ""
        else:
            await message.channel.send(full_response)
            split_at = response_text.rfind("\n", 0, 1900)
            if split_at == -1:
                split_at = 1900
            chunk = response_text[:split_at]
            response_text = response_text[split_at:].lstrip("\n")
            await message.channel.send(f"{chunk}")
    await waiting_msg.delete()