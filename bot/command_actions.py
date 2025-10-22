import discord
import requests
from PIL import UnidentifiedImageError
from PIL.Image import open as image_open
from colormath.color_objects import sRGBColor
from discord import Interaction, DMChannel
from discord.embeds import Embed

from bot.core import sprite_analysis
from bot.spritework.tutorial_mode import PromptButtonsView
from bot.misc.utils import fancy_print

HELP_RESPONSE = ("Do you need help using the Fusion Bot to analyze sprites?\n"
            "You can use it by **mentioning the bot** (using @) **while replying to a sprite**!\n"
            "You can contact Doodledoo if you need help with anything related to the fusion bot. "
            "Let me know if you've got suggestions or ideas too!\n\n"
            "And if you want to start Tutorial Mode, with more info about Fusion Bot, "
            "press the Tutorial Mode button down below.")
SIMILAR_TITLE = "**Similar pairs of colors:**"
ERROR_TITLE = "**An error has occurred processing your command:**"
ERROR_ADDENUM = ("\n\nIf you believe this is incorrect, notify the error either to Doodledoo or here:\n"
                 "https://github.com/Doodleboo/bot-fusion-analyzer/issues")
NO_ATTACHMENT = "No suitable attachment was found."
WRONG_ATTACHMENT = "Couldn't parse the attachment as an image."
NO_SIM_PAIRS = "No similar pairs have been found."
COLOR_COUNT_ERROR = "The image had too many colors."
CULLED_PAIRS_FOOTER = "This list does not include all pairs, as there were too many."
TIMEOUT = 10
ALL_COLOR_LIMIT = 256
PAIR_LIST_LIMIT = 20


async def help_action(interaction: discord.Interaction):
    log_command(interaction, "/help")
    prompt_view = PromptButtonsView(interaction.user)
    await interaction.response.send_message(content=HELP_RESPONSE, view=prompt_view)
    prompt_view.message = await interaction.original_response()


async def similar_action(interaction: discord.Interaction, attachment: discord.Attachment):
    log_command(interaction, "/similar")
    if attachment is None:
        await error_embed(interaction, NO_ATTACHMENT)
        return

    raw_data = requests.get(attachment.url, stream = True, timeout = TIMEOUT).raw
    try:
        image = image_open(raw_data).convert("RGBA")
    except UnidentifiedImageError:
        await error_embed(interaction, WRONG_ATTACHMENT)
        return

    try:
        sorted_color_dict = get_sorted_color_dict(image)
    except ValueError:
        await error_embed(interaction, COLOR_COUNT_ERROR)
        return

    if not sorted_color_dict:
        no_pair_embed = Embed(title = SIMILAR_TITLE, description = NO_SIM_PAIRS)
        await interaction.response.send_message(embed = no_pair_embed)
        return

    pair_list = []
    for color_pair in sorted_color_dict:
        rgb_pair = get_rgb_pair(color_pair)
        pair_list.append(rgb_pair)

    too_many_pairs = len(pair_list) > PAIR_LIST_LIMIT
    if too_many_pairs:
        pair_list = pair_list[0:PAIR_LIST_LIMIT]

    formatted_list = format_list(pair_list)
    similar_embed  = Embed(title = SIMILAR_TITLE,description = formatted_list)
    if too_many_pairs:
        similar_embed.set_footer(text = CULLED_PAIRS_FOOTER)
    await interaction.response.send_message(embed = similar_embed)




def get_sorted_color_dict(image) -> frozenset[frozenset[tuple]]:
    all_colors = image.getcolors(ALL_COLOR_LIMIT)
    if not all_colors:  # Color count higher than 256
        raise ValueError
    useful_colors = sprite_analysis.remove_useless_colors(all_colors)
    rgb_color_list = sprite_analysis.get_rgb_color_list(useful_colors)

    similar_color_dict = sprite_analysis.get_similar_color_dict(rgb_color_list)
    sorted_color_dict = sprite_analysis.sort_color_dict(similar_color_dict)

    return sorted_color_dict


def get_rgb_pair(color_pair: frozenset[tuple]) -> tuple[str, str]:
    pair_list = list(color_pair)
    first_tuple = pair_list[0]
    second_tuple = pair_list[1]
    first_color = sRGBColor(first_tuple[0], first_tuple[1], first_tuple[2], True)
    second_color = sRGBColor(second_tuple[0], second_tuple[1], second_tuple[2], True)
    return first_color.get_rgb_hex(), second_color.get_rgb_hex()


def format_list(pair_list: list[tuple[str, str]]):
    formatted_list = ""
    for pair in pair_list:
        temp_str = "- **" + pair[0] + "** and **" + pair[1] + "**\n"
        formatted_list = formatted_list + temp_str
    return  formatted_list


async def error_embed(interaction: discord.Interaction, message: str):
    error_description =  message + ERROR_ADDENUM
    new_error_embed = Embed(title = ERROR_TITLE, description = error_description)
    await interaction.response.send_message(embed = new_error_embed)

def log_command(interaction: Interaction, command: str):
    channel_name = get_channel_name_from_interaction(interaction)
    fancy_print("Command >", interaction.user.name, channel_name, command)


def get_channel_name_from_interaction(interaction: Interaction):
    try:
        channel = interaction.channel
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