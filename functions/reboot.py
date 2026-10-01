import os
import shutil
from functions.shutdown import shutdown
from classes.user import User

async def reboot(client, message):
    user = User(message.author.id, None)
    if not user.perms == "administrator":
        return await message.channel.send("This command can only be executed by an admin.")
    await shutdown(client, message)
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv not found")
    os.environ["REBOOT_NOTICE"] = "1"
    os.environ["REBOOT_CHANNEL_ID"] = str(message.channel.id)
    os.execv(uv, [uv, "run", "main.py"])