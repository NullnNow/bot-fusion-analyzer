import re

import discord
from discord import Message, Thread

from . import setup
from .bot_context import (id_channel_gallery_pif, id_channel_assets_pif,
                          id_spriter_apps_pif, id_spritework)

ZIGZAG_ID = 1185671488611819560 #1185671488611819560
YANMEGA_ID = 204255221017214977

TAG_CUSTOMIZATION_ID = 1200461437726883921
TAG_NON_IF_ID = 1058148169986342963
TAG_OTHER_ID = 1051367034673434634
IGNORED_SPRITEWORK_TAGS = [TAG_CUSTOMIZATION_ID, TAG_NON_IF_ID, TAG_OTHER_ID]

PATTERN_CUSTOM_BASE = r'[cC]ustom [bB]ase'


def is_sprite_gallery(message: Message) -> bool:
    return message.channel.id == id_channel_gallery_pif


def is_assets_custom_base(message: Message) -> bool:
    return is_assets_gallery(message) and has_custom_base_in_message(message)


def is_assets_gallery(message: Message) -> bool:
    return message.channel.id == id_channel_assets_pif


def is_mentioning_reply(message: Message) -> bool:
    return is_mentioning_bot(message) and is_reply(message)


def is_reply(message: Message) -> bool:
    return message.reference is not None


def is_zigzag_galpost(message: Message) -> bool:
    return is_zigzag_message(message) and (is_sprite_gallery(message) or is_assets_gallery(message))


def is_zigzag_message(message: Message) -> bool:
    return message.author.id == ZIGZAG_ID


def is_message_from_ignored_bots(message: Message) -> bool:
    bot_id = setup.get_bot_id()
    return message.author.id in [bot_id, YANMEGA_ID]


def is_mentioning_bot(message: Message) -> bool:
    result = False
    fusion_bot_id = setup.get_bot_id()
    for user in message.mentions:
        if fusion_bot_id == user.id:
            result = True
            break
    return result


def is_spriter_application(thread: Thread):
    if thread.parent.type != discord.ChannelType.forum:
        return False
    return thread.parent_id == id_spriter_apps_pif


def is_spritework_post(thread: Thread):
    if thread.parent.type != discord.ChannelType.forum:
        return False
    return thread.parent_id == id_spritework


def has_ignored_spritework_tags(thread: Thread) -> bool:
    for tag in thread.applied_tags:
        if tag.id in IGNORED_SPRITEWORK_TAGS:
            return True
    return False


def has_custom_base_in_message(message: Message) -> bool:
    result = re.search(PATTERN_CUSTOM_BASE, message.content)
    return result is not None


def is_intentional_transparency(message: Message) -> bool:
    content = message.content
    if not content:
        return False
    result = re.search(r'(?i)\b(intentional|intended)\s+transparency\b', content)
    return result is not None