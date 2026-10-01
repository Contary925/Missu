import subprocess
from functions.check_owner import check_owner

async def sync_to_github(message):
    if not await check_owner(message):
        return False
    try:
        await message.channel.send("Uploading to GitHub...")
        subprocess.run(["git", "add", "."], check=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode == 0:
            await message.channel.send("Nothing to commit. Working tree is up to date.")
        elif result.returncode == 1:
            subprocess.run(
                [
                    "git", "commit", "-m",
                    "Auto-commit on bot shutdown",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            # await message.channel.send("Changes committed!")
        else:
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                output=result.stdout,
                stderr=result.stderr,
            )
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
        await message.channel.send("Uploaded successfully!")
        return True
    except subprocess.CalledProcessError as e:
        error = e.stderr or e.stdout or str(e)
        await message.channel.send(f"Git sync failed with error:\n```text\n{error[:1500]}\n```")
        return False