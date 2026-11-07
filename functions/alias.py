import functions.call_function
from classes.user import User
import discord

async def alias(client, message, content):
    new_content = "alias_" + content
    #if there's nothing making sense after "alias" then call_function will just pass anyway
    called = await functions.call_function.call_function(client, message, new_content)
    if not called: #if failed to call a function, send instructions
        await message.channel.send("Usage: uwu alias add/remove text1=text2.\nFor example: uwu alias add Missu=<@1529029241566662746>")

async def alias_add(message, content):
    user = User(message.author.id, message.author.display_name)
    [keys, value] = content.split("=", maxsplit = 2)
    counter = 0
    for key in keys.split(", "):
        key = key.strip().casefold()
        if key and value:
            if user.update_alias(key, value):
                counter += 1
            else:
                return await message.channel.send("Something went wrong when adding an alias.")
        else:
            return await message.channel.send("Usage: uwu alias add text1=text2.\nFor example: uwu alias add Missu=<@1529029241566662746>")
    match counter:
        case 1:
            return await message.channel.send(f'Done! "{key.strip().casefold()}" now means "{value.strip()}" for me in your messages.', allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=False))
        case _:
            return await message.channel.send(f'Done! Added **{counter}** new aliases for {value.strip()}.', allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=False))

async def alias_remove(message, content):
    user = User(message.author.id, message.author.display_name)
    key = content.casefold()
    if key :
        if user.delete_alias(key):
            await message.channel.send(f'Done! "{key}" is now associated with nothing else.')
        else :
            await message.channel.send(f'The specified alias does not exist. Usage: uwu alias remove text')
    else:
        await message.channel.send('Something went wrong. Usage: uwu alias remove text')

async def alias_list(message, content) :
    user = User(message.author.id, message.author.display_name)
    alias = user.alias
    alias_list = f"{user.name}'s alias list: \n"
    for item in alias :
        alias_list += f"{item}: {alias[item]}\n"
    if alias_list == f"{user.name}'s alias list: \n" :
        await message.channel.send("Your alias list is empty!")
    else :
        await message.channel.send(alias_list, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=False))
