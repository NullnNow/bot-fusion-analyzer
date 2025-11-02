import json
import os
import re

from discord import Attachment
from discord.asset import Asset
from discord.member import Member
from discord.message import Message
from discord.user import User, ClientUser

from .enums import IdType

MAX_DEX_ID = 572
AUTOGEN_MAX_ID = 501
NECROZMA_DEX_ID = 450

DEX_ID = r'[1-9]\d{0,2}'
LETTER = r'[a-z]{0,1}'

# 123.456
NUMBER_PATTERN_FUSION_ID = rf'({DEX_ID})\.({DEX_ID})'
# 123
NUMBER_PATTERN_CUSTOM_ID = rf'({DEX_ID})'
# 123.456.789
NUMBER_PATTERN_TRIPLE_ID = rf'({DEX_ID})\.({DEX_ID})\.({DEX_ID})'
# 123_egg
NUMBER_PATTERN_EGG_ID = rf'({DEX_ID}_egg)'

# (123.456a)
TEXT_PATTERN_FUSION_ID = rf'\(({DEX_ID})\.({DEX_ID}){LETTER}\)'
# (123a)
TEXT_PATTERN_CUSTOM_ID = rf'\(({DEX_ID}){LETTER}\)'
# (123.456.789a)
TEXT_PATTERN_TRIPLE_ID = rf'\(({DEX_ID})\.({DEX_ID})\.({DEX_ID}){LETTER}\)'


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
NAMES_JSON_FILE = os.path.join(CURRENT_DIR, "..", "..", "data", "PokemonNames.json")


def is_missing_autogen(fusion_id: str):
    split_fusion_id = fusion_id.split(".")
    head_id = int(split_fusion_id[0])
    body_id = int(split_fusion_id[1])
    # Special case: Necrozma bodies are just Ultra Necrozma again
    if body_id == NECROZMA_DEX_ID:
        return True
    return head_id > AUTOGEN_MAX_ID or body_id > AUTOGEN_MAX_ID


def is_invalid_fusion_id(fusion_id: str):
    if "." in fusion_id:
        fusion_id_list = fusion_id.split(".")
    else:
        fusion_id_list = [fusion_id]
    for fusion_id in fusion_id_list:
        id_int = int(fusion_id)
        if id_int > MAX_DEX_ID:
            return True
    return False


def is_invalid_base_id(base_id: str):
    pokemon_id = int(base_id)
    return pokemon_id > MAX_DEX_ID


def get_display_avatar(user: User | Member | ClientUser) -> Asset:
    return user.display_avatar.with_format("png").with_size(256)


def is_chat_gpt_in_filename(filename: str) -> bool:
    result = re.match("ChatGPT", filename)
    return result is not None


def extract_fusion_ids_from_content(message: Message, id_type: IdType):
    content = message.content
    id_list = []
    if id_type.is_custom_base() or id_type.is_egg():
        # Eggs use the same id type as custom bases in the gallery message
        search_pattern = TEXT_PATTERN_CUSTOM_ID
    elif id_type.is_triple_fusion():
        search_pattern = TEXT_PATTERN_TRIPLE_ID
    else:   # Search for fusion content IDs if the filename is unknown too
        search_pattern = TEXT_PATTERN_FUSION_ID

    iterator = re.finditer(search_pattern, content)
    for result in iterator:
        clean_id = get_clean_dex_ids(result[0], id_type)
        id_list.append(clean_id)

    return id_list


def get_clean_dex_ids(text: str, id_type: IdType) -> str | None:
    if id_type.is_custom_base() or id_type.is_egg():
        # With eggs, we also use the base pattern to grab only the number without the "_egg"
        search_pattern = NUMBER_PATTERN_CUSTOM_ID
    elif id_type == IdType.triple:
        search_pattern = NUMBER_PATTERN_TRIPLE_ID
    else:
        search_pattern = NUMBER_PATTERN_FUSION_ID
    result = re.search(search_pattern, text)
    if result:
        return result.group()
    return None


def id_to_name_map():  # Thanks Greystorm for the util and file
    """Returns dictionary mapping id numbers to display names"""
    with open(NAMES_JSON_FILE) as f:
        data = json.loads(f.read())
        return {element["id"]: element["display_name"] for element in data["pokemon"]}


BLUE_TEXT    = '\033[94m'
MAGENTA_TEXT = '\033[35m'
COLOR_END    = '\033[0m'


def fancy_print(decorator: str, author: str, channel: str, text: str):
    if len(text) > 100:
        text = text[:100]
    print(f"{BLUE_TEXT}{decorator}{COLOR_END} [{author}] "
          f"{MAGENTA_TEXT}{{{channel}}}{COLOR_END} {text}")


def attachment_not_an_image(attachment: Attachment) -> bool:
    attachment_type = attachment.content_type
    if attachment_type is None:
        return True
    return not attachment_type.startswith("image")
