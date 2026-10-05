import asyncio

async def check_confirmation(message, client, bot_message) :
    await bot_message.add_reaction("✅")
    await bot_message.add_reaction("❌")
    def reaction_check(reaction, user): #checking if it's the same message, same person, and a valid reaction
        return (
            user == message.author and reaction.message.id == bot_message.id 
        and str(reaction.emoji) in ["✅", "❌"]
            )
    try :
        reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=reaction_check)
    except asyncio.TimeoutError:
        await message.channel.send("Action declined - no confirmation received.")
    else :
        if str(reaction.emoji) == "✅" :
                return 1
        if str(reaction.emoji) == "❌" :
            return 0