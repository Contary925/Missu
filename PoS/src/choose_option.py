import asyncio

NUM_EMOJIS  = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

async def choose_option(player, client, game_msg, num, start_with_zero = True):
    match start_with_zero:
        case True:
            emojis = NUM_EMOJIS[0:num]
        case False:
            emojis = NUM_EMOJIS[1:num+1]
    for emoji in emojis:
        await game_msg.add_reaction(emoji)
    def reaction_check(reaction, user):
        return (
            user == player and reaction.message.id == game_msg.id 
        and str(reaction.emoji) in emojis
            )
    try:
        reaction, user = await client.wait_for(
            "reaction_add",
            timeout=60.0,
            check=reaction_check,
        )
    except asyncio.TimeoutError:
        await game_msg.edit(
            content="Selection timed out."
        )
        return -1
    index = NUM_EMOJIS.index(str(reaction.emoji))
    return index
