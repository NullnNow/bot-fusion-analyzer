import datetime
import re
import math

from aiohttp.abc import HTTPException
from discord import Embed, Message, Thread, Forbidden, NotFound, HTTPException

from bot.setup import get_bot_client, ctx

CHANNEL_URL_PATTERN = r"discord\.com/channels/(\d+)/(\d+)"
CHANNEL_ALT_PATTERN = r"discordapp\.com/channels/(\d+)/(\d+)"

async def get_spritework_thread_times(message: Message) -> Embed:
    description = ""
    channel_mentions = message.channel_mentions
    if not channel_mentions:
        channel_mentions = await get_threads_from_urls_in_message(message)
    for spritework_thread in channel_mentions:
        if not isinstance(spritework_thread, Thread):
            continue
        creation_date = spritework_thread.created_at
        now = datetime.datetime.now(datetime.timezone.utc)
        time_delta = now - creation_date
        if time_delta.days >= 1:
            description += f"**{spritework_thread.name}**: created **over a day ago**\n"
        else:
            hours_delta = math.floor(time_delta.seconds / 3600)
            if (hours_delta >= 1) and (hours_delta < 2):
                hours = "hour"
            else:
                hours = "hours"
            description += f"**{spritework_thread.name}**: created **{hours_delta:.0f} {hours} ago**\n"

    if description == "":
        description = "No linked threads have been found."

    return Embed(title="Spritework thread creation dates", description=description)


async def get_threads_from_urls_in_message(message: Message) -> list[Thread]:
    threads = await find_threads_with_pattern(CHANNEL_URL_PATTERN, message.content)
    if threads:
        return threads

    # Alternate format:discordapp.com instead
    threads = await find_threads_with_pattern(CHANNEL_ALT_PATTERN, message.content)
    return threads


async def find_threads_with_pattern(pattern: str, content: str) -> list[Thread]:
    urls = re.finditer(pattern, content)
    threads = []
    # Format: discord.com/channels/SERVER_ID/THREAD_ID
    for url_match in urls:
        url_string = url_match.group(0)
        linked_thread = await grab_thread_from_url(url_string)
        if linked_thread:
            threads.append(linked_thread)
    return threads


async def grab_thread_from_url(url_string: str) -> Thread|None:
    thread_id = await get_thread_id(url_string)
    if thread_id is None:
        return None
    try:
        return await get_or_fetch_channel(thread_id)
    except (HTTPException, NotFound, Forbidden) as exception:
        error_message = f"Exception {exception} retrieving linked thread {thread_id}"
        print(error_message)
        await ctx().doodledoo.debug.send(error_message)
        return None

async def get_thread_id(url_string: str) -> int|None:
    url_parts = url_string.split("/")
    if len(url_parts) < 4:
        return None
    return int(url_parts[3])

async def get_or_fetch_channel(thread_id: int) -> Thread|None:
    client = get_bot_client()
    if client is None:
        return None
    channel = client.get_channel(thread_id)
    if channel is not None:
        return channel
    return await client.fetch_channel(thread_id)    # API call, used only as safeguard
