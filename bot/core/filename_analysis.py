import re

from bot.misc.enums import IdType
import bot.misc.utils as utils

LETTER_AND_PNG_PATTERN = rf'{utils.LETTER}\.png$'

FILENAME_FUSION_ID = utils.NUMBER_PATTERN_FUSION_ID + LETTER_AND_PNG_PATTERN
FILENAME_CUSTOM_ID = utils.NUMBER_PATTERN_CUSTOM_ID + LETTER_AND_PNG_PATTERN
FILENAME_TRIPLE_ID = utils.NUMBER_PATTERN_TRIPLE_ID + LETTER_AND_PNG_PATTERN
FILENAME_EGG_ID    = utils.NUMBER_PATTERN_EGG_ID    + LETTER_AND_PNG_PATTERN

REGULAR_PATTERN_FUSION_ID = rf'^{FILENAME_FUSION_ID}'
SPOILER_PATTERN_FUSION_ID = rf'^SPOILER_{FILENAME_FUSION_ID}'

REGULAR_PATTERN_CUSTOM_ID = rf'^{FILENAME_CUSTOM_ID}'
SPOILER_PATTERN_CUSTOM_ID = rf'^SPOILER_{FILENAME_CUSTOM_ID}'

REGULAR_PATTERN_TRIPLE_ID = rf'^{FILENAME_TRIPLE_ID}'
SPOILER_PATTERN_TRIPLE_ID = rf'^SPOILER_{FILENAME_TRIPLE_ID}'

REGULAR_PATTERN_EGG_ID = rf'^{FILENAME_EGG_ID}'
SPOILER_PATTERN_EGG_ID = rf'^SPOILER_{FILENAME_EGG_ID}'

class FusionFilename:
    full_filename: str|None
    id_type: IdType
    dex_ids: str|None
    letter: str|None

    def __init__(self,  filename: str, id_type: IdType):
        self.full_filename = remove_spoiler(filename)
        self.id_type = id_type
        if self.id_type.is_unknown():
            self.dex_ids = None
            self.letter = None
            return
        self.dex_ids = utils.get_clean_dex_ids(self.full_filename, id_type)
        self.letter = grab_letter(self.full_filename, self.dex_ids)

    def id_and_letter(self) -> str|None:
        if self.id_type.is_unknown() or self.full_filename is None:
            return None
        return self.full_filename.replace(".png", "")


def remove_spoiler(filename: str) -> str|None:
    if filename is None:
        return None
    return filename.replace("SPOILER_", "")


def grab_letter(filename: str, dex_ids: str) -> str|None:
    # If we reach this point, the filename is standard and any letter will only be the correct one
    remove_rest = (filename.replace("_egg", "")
                   .replace(".png", "")
                   .replace(dex_ids, ""))
    return remove_rest


def get_fusion_filename(filename: str) -> FusionFilename:

    # Search for fusion pattern
    result = re.match(REGULAR_PATTERN_FUSION_ID, filename)
    if result is not None:
        return FusionFilename(filename, IdType.fusion)

    result = re.match(SPOILER_PATTERN_FUSION_ID, filename)
    if result is not None:
        return FusionFilename(filename, IdType.fusion)

    # Search for custom base or egg pattern
    result = re.match(REGULAR_PATTERN_CUSTOM_ID, filename)
    if result is not None:
        return FusionFilename(filename, IdType.custom_base)

    result = re.match(SPOILER_PATTERN_CUSTOM_ID, filename)
    if result is not None:
        return FusionFilename(filename, IdType.custom_base)

    # Search for triple fusion pattern
    result = re.match(REGULAR_PATTERN_TRIPLE_ID, filename)
    if result is not None:
        return FusionFilename(filename, IdType.triple)

    result = re.match(SPOILER_PATTERN_TRIPLE_ID, filename)
    if result is not None:
        return FusionFilename(filename, IdType.triple)

    # Search for new egg pattern
    result = re.match(REGULAR_PATTERN_EGG_ID, filename)
    if result is not None:
        return FusionFilename(filename, IdType.egg)

    result = re.match(SPOILER_PATTERN_EGG_ID, filename)
    if result is not None:
        return FusionFilename(filename, IdType.egg)
    else:
        return FusionFilename("", IdType.unknown)


def get_filename_from_zigzag_image_url(url: str):
    url_parts = url.split(".png")  # Getting everything before the ? and url parameters
    url_parts = url_parts[0].split("/")  # Grabbing only the filename: 1.1a_by_doodledoo
    dex_id = url_parts[-1].split("_")[0]  # Filtering the credit to keep only the dex id
    return dex_id + ".png"
