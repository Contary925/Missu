import random

async def choose_random_item(client, message, content):
    items = content.split(',')
    for item in items:
        item = item.strip()
    result = random.choice(items)
    return await message.channel.send(F'The winner is: **{result}**!')