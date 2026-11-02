from shared.ID import OWNER_ID

async def check_owner(message):
    return message.author.id == OWNER_ID
