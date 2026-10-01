import os
import shutil
from functions.check_owner import check_owner
from auto_git_push import sync_to_github
from functions.shutdown import shutdown

async def reboot(client, message):
    if not await check_owner(message):
        return
    await shutdown(client, message)
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv not found")
    os.environ["REBOOT_NOTICE"] = "1"
    os.environ["REBOOT_CHANNEL_ID"] = message.channel.id
    os.execv(uv, [uv, "run", "main.py"])