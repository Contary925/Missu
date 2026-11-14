from classes.user import User

async def check_for_alias(id, content) -> str:
    user = User(id)
    if content in user.full_command_alias:
        return user.full_command_alias[content]
    else:
        return content

async def full_command_alias(message, content):
    HANDLERS = {
            "create": fca_create,
            "add": fca_create,
            "delete": fca_delete,
            "remove": fca_delete,
            "view": fca_view
        }
    COMMAND_KEYS = sorted(HANDLERS.keys(), key=len, reverse=True)
    content = content.strip()
    if content == "":
        content = "view"
    for cmd in COMMAND_KEYS:
        if content.casefold() == cmd or content.casefold().startswith(cmd + " "):
            args = content[len(cmd):].strip()
            handler = HANDLERS[cmd]
            return await handler(message, args)
    await message.channel.send("Invalid syntax!")

async def fca_create(message, args):
    res = args.casefold().split("=", maxsplit=1)
    if len(res) != 2:
        return await message.channel.send("Invalid syntax! Example: uwu commandalias add play music = uwu play favlist -s")
    [key, value] = res
    user = User(message.author.id)
    if key in user.full_command_alias:
        return await message.channel.send(f"The alias \"{key}\" already exists!")
    if "commandalias" in key:
        return await message.channel.send("Alias key contains prohibited words (avoid using \"commandalias\" in your alias as this may mess up with interpretation)")
    user.create_full_command_alias(key, value)
    await message.channel.send(f"Done! __{key}__ now means **{value}** for me in your messages! Run \"uwu commandalias remove {key}\" to remove it!")
    
async def fca_delete(message, args):
    key = args
    user = User(message.author.id)
    if not key in user.full_command_alias:
        return await message.channel.send(f"Couldn't find any alias for \"{key}\"!")
    user.delete_full_command_alias(key)
    await message.channel.send(f"Done! Deleted the alias for \"{key}\"!")

async def fca_view(message, args):
    user = User(message.author.id)
    text = ""
    counter = 0
    for fca in user.full_command_alias:
        counter += 1
        text += f"\n{counter}. __{fca}__: **{user.full_command_alias[fca]}**"
    if counter == 0:
        return await message.channel.send("You don't have any command alias set!")
    return await message.channel.send(text)
    