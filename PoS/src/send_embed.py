import discord

async def send_embed(message, title, text):
    embed = discord.Embed(
        title=title,
        color=0x258cb7,
        description=text,
    )
    result_msg = await message.channel.send(embed = embed)
    return result_msg