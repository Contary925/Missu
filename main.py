from auto_git_pull import pull_from_github
import discord
import os
pull_from_github()

from shared.ID import *
from login import log_in
[client, api_key] = log_in()
from functions.on_msg import on_msg

from functions.music.watchdog import start_voice_watchdog

@client.event
async def on_ready() :
    await client.change_presence(activity=discord.Game(name="uwu help"))
    start_voice_watchdog(client) #watching voice connection and runs a reconnection attempt, because essentially discord is doind
    #a pretty bad job at this
    print(f"Logged in as {client.user}")
    if os.environ.pop("REBOOT_NOTICE", None) != "1":
        return
    channel_id = os.environ.pop("REBOOT_CHANNEL_ID", None)
    if channel_id is None:
        return
    try:
        channel = client.get_channel(int(channel_id))
        if channel is None:
            channel = await client.fetch_channel(int(channel_id))
        await channel.send("Back to work!")
    except Exception as e:
        print(f"Failed to send reboot notification: {e}")


@client.event
async def on_message(message):
    await on_msg(client, message)

client.run(api_key)