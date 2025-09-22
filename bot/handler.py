import asyncio

import discord
from discord import Message, Thread, HTTPException, PartialEmoji, DMChannel, TextChannel
from analysis import Analysis
from analyzer import send_full_analysis, generate_analysis, send_analysis
from bot.analyzer import send_extra_embeds
from bot.opt_out_options import is_opted_out_user
from bot.tutorial_mode import send_tutorial_mode_prompt, user_is_potential_spriter
from bot.utils import fancy_print
from issues import DifferentSprite # If the package is named bot.issues, Python thinks they're different types
from bot.setup import ctx
from enums import AnalysisType, Severity
from message_identifier import is_assets_gallery
from spritework_checker import get_spritework_thread_times


ERROR_EMOJI_NAME = "NANI"
ERROR_EMOJI_ID = f"<:{ERROR_EMOJI_NAME}:770390673664114689>"
SPRITE_MANAGER_PING = "<@&900867033175040101>"
ERROR_EMOJI = PartialEmoji(name=ERROR_EMOJI_NAME).from_str(ERROR_EMOJI_ID)


# Handler methods

async def handle_sprite_gallery(message: Message):
    await handle_gallery(message, is_assets=False)


async def handle_assets_gallery(message: Message):
    await handle_gallery(message, is_assets=True)


async def handle_gallery(message: Message, is_assets: bool = False):
    if is_assets:
        log_event("Assets  >", message)
    else:
        log_event("Gallery >", message)

    for specific_attachment in message.attachments:
        if is_assets:
            analysis_type = AnalysisType.assets_gallery
        else:
            analysis_type = AnalysisType.sprite_gallery

        analysis = generate_analysis(message, specific_attachment, analysis_type)

        if analysis.issues.has_issue(DifferentSprite):
            await handle_misnumbered_in_gallery(message, analysis)
            return

        if analysis.severity.is_warn_severity():
            try:
                await message.add_reaction(ERROR_EMOJI)
            except HTTPException:
                await message.add_reaction("😡")  # Nani failsafe
        try:
            await send_full_analysis(analysis, ctx().pif.logs, message.author)
        except HTTPException:  # Rate limit
            await asyncio.sleep(300)
            await send_full_analysis(analysis, ctx().pif.logs, message.author)


async def handle_zigzag_galpost(message: Message):
    embed = message.embeds[0]
    fancy_print("Zigzag  >", embed.author.name, message.channel.name, embed.title)

    if is_assets_gallery(message):
        analysis_type = AnalysisType.zigzag_base
    else:
        analysis_type = AnalysisType.zigzag_fusion

    analysis = generate_analysis(message, specific_attachment=None, analysis_type=analysis_type)
    if analysis.severity == Severity.refused:       # Only for refused tier
        channel = ctx().pif.zigzagoon
    else:
        channel = ctx().pif.logs
    await send_analysis(analysis, channel)
    await send_extra_embeds(analysis, channel)


async def handle_reply_message(message: Message, auto_spritework: bool = False):
    channel = message.channel
    if auto_spritework:
        analysis_type = AnalysisType.auto_spritework
    else:
        analysis_type = AnalysisType.ping_reply
    for specific_attachment in message.attachments:
        analysis = generate_analysis(message, specific_attachment, analysis_type)
        try:
            await notify_if_ai(analysis, message, analysis_type, channel)
            await send_full_analysis(analysis, channel, message.author)
        except discord.Forbidden:
            await ctx().doodledoo.debug.send(f"Missing permissions in {channel.name}: {channel.jump_url}")


async def handle_spriter_application(thread: Thread):
    application_message = await fetch_thread_message(thread)
    if not application_message:
        return
    log_event("Spr App >", application_message)
    try:
        await handle_reply_message(application_message)
        await handle_spritework_thread_times(application_message)
    except Exception as message_exception:
        print(" ")
        print(application_message)
        print(" ")
        await ctx().doodledoo.debug.send(
            f"ERROR in #{application_message.channel} ({application_message.jump_url})")
        raise RuntimeError from message_exception


async def handle_spritework_thread_times(message: Message):
    times_embed = await get_spritework_thread_times(message)
    try:
        await message.channel.send(embed=times_embed)
    except discord.Forbidden:
        await ctx().doodledoo.debug.send(f"Spriter Application: Missing permissions in {message.channel}")


async def handle_spritework_post(thread: Thread):
    spritework_message = await fetch_thread_message(thread)
    if not spritework_message:
        return

    author = spritework_message.author
    if await is_opted_out_user(author):
        return

    log_event("SprWork >", spritework_message)
    await handle_reply_message(message=spritework_message, auto_spritework=True)

    if user_is_potential_spriter(author):
        await asyncio.sleep(1)
        await send_tutorial_mode_prompt(author, thread)


async def handle_reply(message: Message):
    reply_message = await get_reply_message(message)
    log_event("Reply   >", reply_message)
    await handle_reply_message(reply_message)


async def handle_misnumbered_in_gallery(message: Message, analysis: Analysis):
    misnumbered_issue = None
    for issue in analysis.issues.issue_list:
        if isinstance(issue, DifferentSprite):
            misnumbered_issue = issue
            break

    if misnumbered_issue is None:
        return

    copied_message = await ctx().pif.logs.send(f"Hi {message.author.mention}, here's your gallery message, you can copy the block "
                                               f"below and it will have the same text you just sent:\n```{message.content}```")
    await message.channel.send(content=
                               f"Hi {message.author.mention}, \n\nUnfortunately your latest gallery message had a "
                               f"**misnumbered dex id**, either in the message or filename, because they didn't match eachother:\n\n"
                               f"* **Filename ID: {misnumbered_issue.filename_fusion_id}**\n"
                               f"* **Message ID: {misnumbered_issue.content_fusion_id}**\n\n"
                               f"You can recover and copy your message text at: {copied_message.jump_url} "
                               f"so that you can fix the issue and post it here again.\n\nThank you!",
                               delete_after=20)
    await message.delete()


def log_event(decorator: str, event: Message | Thread):
    if isinstance(event, Message):
        _log_message(decorator, event)


def _log_message(decorator: str, message: Message):
    channel_name = get_channel_name_from_message(message)
    split_lines = message.content.splitlines()
    if split_lines:
        first_line = split_lines[0]
    else:
        first_line = ""

    fancy_print(decorator, message.author.name, channel_name, first_line)


def get_channel_name_from_message(message: Message) -> str:
    try:
        channel = message.channel
        if isinstance(channel, DMChannel):
            return "DIRECT MESSAGE"
        channel_name = channel.name  # type: ignore
        if not isinstance(channel_name, str):
            return "INVALID"
    except SystemExit:
        raise
    except BaseException:
        channel_name = "UNKNOWN"
    return channel_name


async def get_reply_message(message: Message):
    if message.reference is None:
        raise RuntimeError(message)

    reply_id = message.reference.message_id
    if reply_id is None:
        raise RuntimeError(message)

    return await message.channel.fetch_message(reply_id)


async def fetch_thread_message(thread: Thread) -> Message|None:
    await asyncio.sleep(5)     # If it's too soon after thread creation, Discord returns errors
    try:
        caught_message = await thread.fetch_message(thread.id)
    except discord.errors.NotFound:
        last_message_id = thread.last_message_id
        try:
            caught_message = await thread.fetch_message(last_message_id)
        except discord.errors.NotFound:
            await ctx().doodledoo.debug.send(f"Could not fetch messages from thread {thread.name}: {thread.jump_url}")
            return None
    except discord.errors.Forbidden:
        await ctx().doodledoo.debug.send("Discord returned Forbidden while fetching thread message")
        return None
    if caught_message is None:
        await ctx().doodledoo.debug.send("Could not fetch message on thread creation")
        return None

    return caught_message


async def notify_if_ai(analysis: Analysis, message: Message, analysis_type: AnalysisType,
                       channel: TextChannel | Thread | DMChannel):
    new_user_in_spritework = (user_is_potential_spriter(message.author)
                              and analysis_type.is_automatic_spritework_analysis())
    if analysis.ai_suspicion >= 10 and new_user_in_spritework:
        warn_message = f"{SPRITE_MANAGER_PING} Potential AI sprite: {message.jump_url}"
        await ctx().pif.bot_chat.send(content=warn_message)
    if analysis.ai_suspicion >= 5 and new_user_in_spritework:
        await channel.send(content="Thanks for posting to spritework!\n"
                                   "As a general reminder to new users, sprites here are meant to be made by "
                                   "the users who submit them, without the use of AI at any stage.\n"
                                   "Welcome to the community!")
        await asyncio.sleep(5)