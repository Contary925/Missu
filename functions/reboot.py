import os
import shutil
import sys
import subprocess
from functions.check_owner import check_owner
from auto_git_push import sync_to_github
from functions.shutdown import shutdown

async def reboot(client, message):
    if not await check_owner(message):
        return
    # await message.channel.send("Rebooting...")
    sync_success = await sync_to_github(message)
    if not sync_success:
        await message.channel.send(
            "Git sync failed, but reboot will continue."
        )
    await shutdown(client, message)
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv not found")
    os.execv(uv, [uv, "run", "main.py"])