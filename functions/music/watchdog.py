import asyncio
from functions.music.music import music_queues, manual_skips, play_song

recovery_locks = {}
recovering_guilds = set()
playback_generations = {}
playback_text_channels = {}
voice_disconnect_since = {}
voice_retry_at = {}
voice_recovery_attempts = {}
voice_watchdog_task = None
voice_recovery_channels = {}

#reconnection helpers

def next_playback_generation(guild_id):
    generation = playback_generations.get(guild_id, 0) + 1
    playback_generations[guild_id] = generation
    return generation


def is_current_generation(guild_id, generation):
    return playback_generations.get(guild_id) == generation

async def recover_voice_connection(guild):
    guild_id = guild.id
    lock = recovery_locks.setdefault(guild_id, asyncio.Lock())

    async with lock:
        voice_client = guild.voice_client

        channel = (
            voice_client.channel
            if voice_client is not None
            else voice_recovery_channels.get(guild_id)
        )

        if channel is None:
            print(f"[VOICE] Cannot recover guild {guild_id}: channel is unknown")
            return False

        if voice_client is not None and voice_client.is_connected():
            return True

        queue = music_queues.get(guild_id)
        current_song = queue.current_song if queue else None
        text_channel = playback_text_channels.get(guild_id)

        if current_song is not None and text_channel is None:
            print(f"[VOICE] Cannot recover guild {guild_id}: text channel is unknown")
            return False

        voice_recovery_channels[guild_id] = channel

        generation = next_playback_generation(guild_id)
        manual_skips.discard(guild_id)
        recovering_guilds.add(guild_id)

        try:
            print(f"[VOICE] Recovering connection for guild {guild_id}")

            if voice_client is not None:
                await voice_client.disconnect(force=True)

            new_voice_client = await channel.connect(
                timeout=20,
                reconnect=True
            )

            if not is_current_generation(guild_id, generation):
                await new_voice_client.disconnect(force=True)
                return False

            if current_song is not None and queue is not None:
                await play_song(
                    new_voice_client,
                    current_song,
                    queue,
                    text_channel
                )

            voice_recovery_channels.pop(guild_id, None)

            print(f"[VOICE] Recovery successful for guild {guild_id}")
            return True

        except Exception as e:
            print(f"[VOICE] Recovery failed for guild {guild_id}: {e}")
            return False

        finally:
            recovering_guilds.discard(guild_id)

async def voice_watchdog(client):
    loop = asyncio.get_running_loop()

    print("[VOICE] Watchdog started")

    while not client.is_closed():
        try:
            for guild in client.guilds:
                guild_id = guild.id
                voice_client = guild.voice_client

                if voice_client is None and guild_id not in voice_recovery_channels:
                    voice_disconnect_since.pop(guild_id, None)
                    voice_retry_at.pop(guild_id, None)
                    voice_recovery_attempts.pop(guild_id, None)
                    continue

                if voice_client is not None and voice_client.is_connected():
                    voice_disconnect_since.pop(guild_id, None)
                    voice_retry_at.pop(guild_id, None)
                    voice_recovery_attempts.pop(guild_id, None)
                    continue

                queue = music_queues.get(guild_id)

                # No current song means there is nothing to recover.
                if queue is None or queue.current_song is None:
                    continue

                now = loop.time()
                disconnected_at = voice_disconnect_since.setdefault(
                    guild_id, now
                )

                # Give discord.py time to reconnect on its own.
                if now - disconnected_at < 3:
                    continue

                if now < voice_retry_at.get(guild_id, 0):
                    continue

                print(
                    f"[VOICE] Connection lost for over 3 seconds "
                    f"in guild {guild_id}. Starting recovery."
                )

                success = await recover_voice_connection(guild)

                if success:
                    voice_disconnect_since.pop(guild_id, None)
                    voice_retry_at.pop(guild_id, None)
                    voice_recovery_attempts.pop(guild_id, None)
                else:
                    attempts = voice_recovery_attempts.get(guild_id, 0) + 1
                    voice_recovery_attempts[guild_id] = attempts

                    delays = [5, 10, 20, 30]
                    delay = delays[min(attempts - 1, len(delays) - 1)]

                    voice_retry_at[guild_id] = loop.time() + delay

                    print(
                        f"[VOICE] Recovery attempt {attempts} failed. "
                        f"Retrying in {delay} seconds."
                    )

        except Exception as e:
            print(f"[VOICE] Watchdog error: {e}")

        await asyncio.sleep(5)


def start_voice_watchdog(client):
    global voice_watchdog_task

    if voice_watchdog_task is None or voice_watchdog_task.done():
        voice_watchdog_task = asyncio.create_task(
            voice_watchdog(client)
        )