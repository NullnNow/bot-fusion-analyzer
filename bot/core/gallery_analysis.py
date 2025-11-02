from bot.core.analysis import Analysis
from bot.core.filename_analysis import FusionFilename
from bot.core.issues import MissingMessageId, UnknownSprite, DifferentFilenameIds, DifferentSprite
from bot.misc import utils
from bot.misc.enums import Severity


async def main(analysis_list: list[Analysis]):
    """Does some checks from content_analysis with harsher restrictions and some entirely different checks"""
    if (not analysis_list) or (len(analysis_list) == 0):
        return
    # Move NANI and ping behavior to gallery specific methods in analyzer
    same_id_checks(analysis_list)
    await correct_gallery_checks()
    await pokemon_name_checks()
    await filename_letter_checks()


def same_id_checks(analysis_list: list[Analysis]):
    first_analysis = analysis_list[0]
    first_filename = first_analysis.fusion_filename
    content_ids = utils.extract_fusion_ids_from_content(first_analysis.message, first_filename.id_type)
    if not content_ids:
        first_analysis.issues.add(MissingMessageId())
        return
    if first_filename.dex_ids not in content_ids:
        first_analysis.issues.add(DifferentSprite(first_filename.dex_ids, content_ids[0]))
        return
    for analysis in analysis_list:
        compare_with_first_filename(analysis, first_filename)


def compare_with_first_filename(analysis: Analysis, first_filename: FusionFilename):
    if analysis.fusion_filename.id_type.is_unknown():
        analysis.issues.add(UnknownSprite())
        analysis.severity = Severity.ignored
        return
    if analysis.fusion_filename.dex_ids != first_filename.dex_ids:
        analysis.issues.add(DifferentFilenameIds())


async def correct_gallery_checks():
    # Correct gallery checks
        # If it's sprite gallery, ensure it's only a fusion or triple fusion
        # If it's assets gallery, ensure it's only a base or egg
    pass


async def pokemon_name_checks():
    # If all the filenames match, text checker (beta version that only mentions it in the analysis)
        # Either grab the full names of each Pokémon or a minimal version that allows for misspellings
        # Ensure both names exist in the gallery message. If they don't, have a new easily searchable issue
        # After a trial period it can be determined if the name checker is too strict, how often do misspellings
        # happen, how flexible it is, and if it actually enforces cases where the names don't match
    # Add the PokemonNames issue here too
    pass


async def filename_letter_checks():
    # Month search:
        # Search for previous gallery post within the same month by that user
        # If one matches the current message, ensure that none of its images have the same filename as any of
        # the current images. Issue if it does.
        # If there are n images in a previous matching post, take it into account for the next part
    # Ensure that the new sprites have letters that start at N previous images and continue the pattern for M
    # 1 nothing, 2a, 3b, 4c, 5d, number being N + M
    # Since the order cannot be guaranteed, have a boolean array of M size that goes from letter N to N+M
    # If any attachment has a letter higher than N + M, put an issue on that analysis
    # At the end, if any letter is unfilled, put an issue in the first analysis
    pass