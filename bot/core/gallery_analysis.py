from datetime import datetime

from bot.context.setup import ctx
from bot.core.analysis import Analysis
from bot.core.content_analysis import handle_dex_verification
from bot.core.filename_analysis import FusionFilename
from bot.core.issues import MissingMessageId, UnknownSprite, DifferentFilenameIds, DifferentSprite, IncorrectGallery, \
    FileName
from bot.misc import utils
from bot.misc.enums import Severity


async def main(analysis_list: list[Analysis]):
    """Does some checks from content_analysis with harsher restrictions and some entirely different checks"""
    if (not analysis_list) or (len(analysis_list) == 0):
        return
    same_id_checks(analysis_list)
    if analysis_list[0].issues.has_issue(UnknownSprite):
        return
    correct_gallery_checks(analysis_list)
    pokemon_name_checks(analysis_list)
    await filename_letter_checks(analysis_list)


def same_id_checks(analysis_list: list[Analysis]):
    first_analysis = analysis_list[0]
    first_filename = first_analysis.fusion_filename
    if first_filename.id_type.is_unknown():
        unknown_sprite(first_analysis)
        return
    content_ids = utils.extract_fusion_ids_from_content(first_analysis.message, first_filename.id_type)
    if not content_ids:
        first_analysis.issues.add(MissingMessageId())
        first_analysis.severity = Severity.refused
        return
    if first_filename.dex_ids not in content_ids:
        first_analysis.issues.add(DifferentSprite(first_filename.dex_ids, content_ids[0]))
        return
    for analysis in analysis_list:
        compare_with_first_filename(analysis, first_filename)


def unknown_sprite(analysis: Analysis):
    analysis.issues.add(UnknownSprite())
    filename = analysis.get_filename()
    analysis.issues.add(FileName(filename))
    analysis.severity = Severity.refused


def compare_with_first_filename(analysis: Analysis, first_filename: FusionFilename):
    if analysis.fusion_filename.id_type.is_unknown():
        unknown_sprite(analysis)
        return
    if analysis.fusion_filename.dex_ids != first_filename.dex_ids:
        analysis.issues.add(DifferentFilenameIds())
        analysis.severity = Severity.refused


def correct_gallery_checks(analysis_list: list[Analysis]):
    first_analysis = analysis_list[0]
    if first_analysis.type.is_sprite_gallery():
        ensure_sprite_gallery_type(first_analysis)
    else:
        ensure_assets_gallery_type(first_analysis)


def ensure_sprite_gallery_type(analysis: Analysis):
    id_type = analysis.fusion_filename.id_type
    if id_type.is_fusion() or id_type.is_triple_fusion():
        return
    analysis.issues.add(IncorrectGallery(id_type, "Sprite Gallery"))
    analysis.severity = Severity.refused


def ensure_assets_gallery_type(analysis: Analysis):
    id_type = analysis.fusion_filename.id_type
    if id_type.is_custom_base() or id_type.is_egg():
        return
    analysis.issues.add(IncorrectGallery(id_type, "Assets Gallery"))
    analysis.severity = Severity.refused


def pokemon_name_checks(analysis_list: list[Analysis]):
    for analysis in analysis_list:
        handle_dex_verification(analysis, analysis.fusion_filename.dex_ids)
    # If all the filenames match, text checker (beta version that only mentions it in the analysis)
        # Either grab the full names of each Pokémon or a minimal version that allows for misspellings
        # Ensure both names exist in the gallery message. If they don't, have a new easily searchable issue
        # After a trial period it can be determined if the name checker is too strict, how often do misspellings
        # happen, how flexible it is, and if it actually enforces cases where the names don't match


async def filename_letter_checks(analysis_list: list[Analysis]):
    await search_in_same_month(analysis_list[0])
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


async def search_in_same_month(analysis: Analysis):
    author = analysis.message.author.id
    if analysis.type.is_sprite_gallery():
        gallery_channel = ctx().pif.gallery
    else:
        gallery_channel = ctx().pif.assets

    after_date = datetime(2025, 10, 19)
    #async for message in gallery_channel.history(after=after_date):
        #print("one")