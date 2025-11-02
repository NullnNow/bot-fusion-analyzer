# coding: utf-8
import os

import discord
from discord import app_commands, Thread
from discord.message import Message
from discord.user import User

import command_actions
from bot.context.message_identifier import (is_zigzag_galpost, is_sprite_gallery, is_mentioning_reply,
                                            is_spriter_application, is_message_from_ignored_bots,
                                            is_spritework_post, is_mentioning_bot, is_assets_gallery)
from bot.context.setup import set_bot_up, ctx
from bot.handler import (handle_zigzag_galpost, handle_sprite_gallery, handle_assets_gallery,
                         handle_spriter_application, handle_reply, handle_spritework_post, handle_direct_ping)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

intents = discord.Intents.default()
intents.guild_messages = True
intents.members = True
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


# Commands and bot events

@tree.command(name="help", description="Fusion bot help")
async def help_command(interaction: discord.Interaction):
    await command_actions.help_action(interaction)


@tree.command(name="similar", description="Get the list of similar colors")
async def similar_command(interaction: discord.Interaction, sprite: discord.Attachment):
    await command_actions.similar_action(interaction, sprite)


@bot.event
async def on_ready():
    await tree.sync()
    await set_bot_up(bot)
    await ctx().doodledoo.logs.send(content="Bot online")


@bot.event
async def on_message(message: Message):
    try:
        if is_message_from_ignored_bots(message):
            return

        if is_zigzag_galpost(message):
            await handle_zigzag_galpost(message)
        elif is_sprite_gallery(message):
            await handle_sprite_gallery(message)
        elif is_assets_gallery(message):
            await handle_assets_gallery(message)
        elif is_mentioning_reply(message):
            await handle_reply(message)
        elif is_mentioning_bot(message):
            await handle_direct_ping(message)

    except Exception as message_exception:
        print(" ")
        print(message)
        print(" ")
        await ctx().doodledoo.debug.send(
            f"ERROR in #{message.channel} ({message.jump_url})")
        raise RuntimeError from message_exception


@bot.event
async def on_thread_create(thread: Thread):
    try:
        if is_spriter_application(thread):
            await handle_spriter_application(thread)
        elif is_spritework_post(thread):
            await handle_spritework_post(thread)
    except Exception as message_exception:
        await ctx().doodledoo.debug.send(
            f"ERROR in #{thread} ({thread.jump_url})")
        raise RuntimeError from message_exception



def get_user(user_id) -> (User | None):
    return bot.get_user(user_id)


def get_discord_token():
    token_dir = os.path.join(CURRENT_DIR, "..", "token", "discord.txt")
    token = open(token_dir).read().rstrip()
    return token



if __name__ == "__main__":
    discord_token = get_discord_token()
    bot.run(discord_token)

