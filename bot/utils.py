import json
import os
import re

from discord.message import Message
from discord.asset import Asset
from discord.user import User, ClientUser
from discord.member import Member

from bot.enums import IdType

MAX_DEX_ID = 573
AUTOGEN_MAX_ID = 501
NECROZMA_DEX_ID = 450


LETTER_AND_PNG_PATTERN = r'[a-z]{0,1}\.png$'

# 123.456
NUMBER_PATTERN_FUSION_ID = r'([1-9]\d{0,2})\.([1-9]\d{0,2})'
# 123
NUMBER_PATTERN_CUSTOM_ID = r'([1-9]\d{0,2})'
# 123.456.789
NUMBER_PATTERN_TRIPLE_ID = r'([1-9]\d{0,2})\.([1-9]\d{0,2})\.([1-9]\d{0,2})'
# 123_egg
NUMBER_PATTERN_EGG_ID = r'([1-9]\d{0,2}_egg)'

# (123.456a)
TEXT_PATTERN_FUSION_ID = r'\(([1-9]\d{0,2})\.([1-9]\d{0,2})[a-z]{0,1}\)'
# (123a)
TEXT_PATTERN_CUSTOM_ID = r'\(([1-9]\d{0,2})[a-z]{0,1}\)'
# (123.456.789a)
TEXT_PATTERN_TRIPLE_ID = r'\(([1-9]\d{0,2})\.([1-9]\d{0,2})\.([1-9]\d{0,2})[a-z]{0,1}\)'

FILENAME_FUSION_ID = NUMBER_PATTERN_FUSION_ID + LETTER_AND_PNG_PATTERN
FILENAME_CUSTOM_ID = NUMBER_PATTERN_CUSTOM_ID + LETTER_AND_PNG_PATTERN
FILENAME_TRIPLE_ID = NUMBER_PATTERN_TRIPLE_ID + LETTER_AND_PNG_PATTERN
FILENAME_EGG_ID    = NUMBER_PATTERN_EGG_ID    + LETTER_AND_PNG_PATTERN

REGULAR_PATTERN_FUSION_ID = rf'^{FILENAME_FUSION_ID}'
SPOILER_PATTERN_FUSION_ID = rf'^SPOILER_{FILENAME_FUSION_ID}'

REGULAR_PATTERN_CUSTOM_ID = rf'^{FILENAME_CUSTOM_ID}'
SPOILER_PATTERN_CUSTOM_ID = rf'^SPOILER_{FILENAME_CUSTOM_ID}'

REGULAR_PATTERN_TRIPLE_ID = rf'^{FILENAME_TRIPLE_ID}'
SPOILER_PATTERN_TRIPLE_ID = rf'^SPOILER_{FILENAME_TRIPLE_ID}'

REGULAR_PATTERN_EGG_ID = rf'^{FILENAME_EGG_ID}'
SPOILER_PATTERN_EGG_ID = rf'^SPOILER_{FILENAME_EGG_ID}'


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
NAMES_JSON_FILE = os.path.join(CURRENT_DIR, "..", "data", "PokemonNames.json")


def get_filename_from_image_url(url: str):
    url_parts = url.split(".png")  # Getting everything before the ? and url parameters
    url_parts = url_parts[0].split("/")  # Grabbing only the filename: 1.1_by_doodledoo
    dex_id = url_parts[-1].split("_")[0]  # Filtering the credit to keep only the dex id
    return dex_id + ".png"


def is_missing_autogen(fusion_id: str):
    split_fusion_id = fusion_id.split(".")
    head_id = int(split_fusion_id[0])
    body_id = int(split_fusion_id[1])
    # Special case: Necrozma bodies are just Ultra Necrozma again
    if body_id == NECROZMA_DEX_ID:
        return True
    return head_id > AUTOGEN_MAX_ID or body_id > AUTOGEN_MAX_ID


def is_invalid_fusion_id(fusion_id: str):
    fusion_id_list = fusion_id.split(".")
    for id in fusion_id_list:
        id_int = int(id)
        if id_int > MAX_DEX_ID:
            return True
    return False


def is_invalid_base_id(base_id: str):
    pokemon_id = int(base_id)
    return pokemon_id > MAX_DEX_ID


def get_display_avatar(user: User | Member | ClientUser) -> Asset:
    return user.display_avatar.with_format("png").with_size(256)


def get_fusion_id_from_filename(filename: str) -> (str, IdType):

    # Search for fusion pattern
    result = re.match(REGULAR_PATTERN_FUSION_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.fusion), IdType.fusion

    result = re.match(SPOILER_PATTERN_FUSION_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.fusion), IdType.fusion

    # Search for custom base or egg pattern
    result = re.match(REGULAR_PATTERN_CUSTOM_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.custom_base), IdType.custom_base

    result = re.match(SPOILER_PATTERN_CUSTOM_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.custom_base), IdType.custom_base

    # Search for triple fusion pattern
    result = re.match(REGULAR_PATTERN_TRIPLE_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.triple), IdType.triple

    result = re.match(SPOILER_PATTERN_TRIPLE_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.triple), IdType.triple

    # Search for new egg pattern
    result = re.match(REGULAR_PATTERN_EGG_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.egg), IdType.egg

    result = re.match(SPOILER_PATTERN_EGG_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.egg), IdType.egg
    else:
        return None, IdType.unknown


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
    elif id_type.is_fusion():
        search_pattern = TEXT_PATTERN_FUSION_ID
    else:
        return id_list

    iterator = re.finditer(search_pattern, content)
    for result in iterator:
        clean_id = get_clean_id_from_result(result[0], id_type)
        id_list.append(clean_id)

    return id_list


def get_clean_id_from_result(text: str, id_type: IdType):
    fusion_id = None
    if id_type.is_custom_base() or id_type.is_egg():
        # With eggs, we also use the base pattern to grab only the number without the "_egg"
        search_pattern = NUMBER_PATTERN_CUSTOM_ID
    elif id_type == IdType.triple:
        search_pattern = NUMBER_PATTERN_TRIPLE_ID
    else:
        search_pattern = NUMBER_PATTERN_FUSION_ID
    result = re.search(search_pattern, text)
    if result:
        fusion_id = result[0]
    return fusion_id


def id_to_name_map():  # Thanks Greystorm for the util and file
    """Returns dictionary mapping id numbers to display names"""
    with open(NAMES_JSON_FILE) as f:
        data = json.loads(f.read())
        return {element["id"]: element["display_name"] for element in data["pokemon"]}


def is_intentional_transparency(message: Message) -> bool:
    content = message.content
    if not content:
        return False
    result = re.search(r'(?i)\b(intentional|intended)\s+transparency\b', content)
    return result is not None


BLUE_TEXT    = '\033[94m'
MAGENTA_TEXT = '\033[35m'
COLOR_END    = '\033[0m'


def fancy_print(decorator: str, author: str, channel: str, text: str):
    if len(text) > 100:
        text = text[:100]
    print(f"{BLUE_TEXT}{decorator}{COLOR_END} [{author}] "
          f"{MAGENTA_TEXT}{{{channel}}}{COLOR_END} {text}")
