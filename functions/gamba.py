import random
from classes.user import User
import re

async def choose(client, message, content):
    [command, args] = (content+' ').split(' ', maxsplit=1) #an extra space prevents breaking if there's only one space
    command = command.strip()
    args = args.strip()
    match command:   
        case 'create':
            return await create_items_list(client, message, args)
        case 'add':
            return await add_items_to_list(client, message, args)
        case 'remove':
            return await remove_items_from_list(client, message, args)
    await choose_random_item(client, message, content)

async def choose_random_item(client, message, content):
    user = User(message.author.id)
    user_gamble_lists = user.gamble_lists
    mutations = None
    for list_name in user_gamble_lists:
        if content.startswith(list_name):
            mutations = content.split(list_name, maxsplit=1)[1]
            break
    if mutations is not None:
        items = user_gamble_lists[list_name]
        if items == []:
            return await message.channel.send('The list is empty!')
        mutations = re.findall(r'([+-])\s*(.*?)(?=\s+[+-]|$)', mutations)
        added = []
        removed = []
        for sign, mutation in mutations:
            if sign == '+':
                added.append(mutation.strip())
            else:
                removed.append(mutation.strip())   
        print(added)
        print(removed)
        print(items)
        items = list(dict.fromkeys(items + added)) 
        for item_to_remove in removed:
                try:
                    items.remove(item_to_remove)
                except ValueError:
                    continue
        print(items)
        result = random.choice(items)
        return await message.channel.send(F'The winner is: **{result.strip()}**!')
    else:
        items = content.split(',')
        result = random.choice(items)
        return await message.channel.send(F'The winner is: **{result.strip()}**!')
    

async def create_items_list(client, message, args):
    user = User(message.author.id)
    [list_name, items_string] = (args+'=').split('=', maxsplit=1) #an extra space prevents breaking if there's no =
    list_name = list_name.strip()
    items_string = items_string.strip()
    items_temp = items_string.split(',')
    items = []
    for i in range(0, len(items_temp)-1):
        items_temp[i].strip()
        if items_temp[i] != '':
            items.append(items_temp[i])
    user_gamble_lists = user.gamble_lists
    user_gamble_lists[list_name] = items
    user.data_update('gamble_lists', user_gamble_lists)
    return await message.channel.send(f'Done! Created a list **{list_name}** containing **{len(items)}** items!')

async def add_items_to_list(client, message, args):
    user = User(message.author.id)
    user_gamble_lists = user.gamble_lists
    for list_name in user_gamble_lists:
        if args.startswith(list_name):
            items_string = args.split(list_name, maxsplit=1)[1]
            break
    if not items_string:
        return await message.channel.send("Unknown list!")
    items_string = items_string.strip()
    items_temp = items_string.split(',')
    items = []
    for i in range(0, len(items_temp)-1):
        items_temp[i].strip()
        if items_temp[i] != '':
            items.append(items_temp[i])
    user_gamble_lists[list_name] = list(dict.fromkeys(user_gamble_lists[list_name] + items))
    user.data_update('gamble_lists', user_gamble_lists)
    return await message.channel.send(f'Done! Added **{len(items)}** items to list **{list_name}**!')

async def remove_items_from_list(client, message, args):
    user = User(message.author.id)
    user_gamble_lists = user.gamble_lists
    for list_name in user_gamble_lists:
        if args.startswith(list_name):
            items_string = args.split(list_name, maxsplit=1)[1]
            break
    if not items_string:
        return await message.channel.send("Unknown list!")
    items_string = items_string.strip()
    items_temp = items_string.split(',')
    items = []
    for i in range(0, len(items_temp)-1):
        items_temp[i].strip()
        if items_temp[i] != '':
            items.append(items_temp[i])
    not_in_list_counter = 0
    for item in items:
        try:
            user_gamble_lists.remove(item)
        except ValueError:
            not_in_list_counter += 1
            continue
    user.data_update('gamble_lists', user_gamble_lists)
    return await message.channel.send(f'Done! Removed **{len(items) - not_in_list_counter}** items from list **{list_name}**!')