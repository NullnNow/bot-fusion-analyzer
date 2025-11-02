import bot.misc.utils as utils
from bot.misc.enums import Severity, IdType
from .analysis import Analysis
from .issues import (CustomBase, DifferentSprite, EggSprite, UnknownSprite, MissingFilename,
                     MissingSprite, OutOfDex, FileName, PokemonNames, TripleFusionSprite)


class ContentContext:
    id_type: IdType
    def __init__(self, analysis: Analysis):

        self.filename_fusion_id = analysis.fusion_filename.dex_ids
        self.id_type = analysis.fusion_filename.id_type
        self.is_custom_base = self.id_type.is_custom_base()
        self.is_egg_sprite = self.id_type.is_egg()

        self.content_fusion_ids_list = utils.extract_fusion_ids_from_content(analysis.message, self.id_type)

        if self.content_fusion_ids_list:
            self.content_fusion_id = self.content_fusion_ids_list[0]
        else:
            self.content_fusion_id = None


    def has_both_fusion_ids(self):
        return (self.filename_fusion_id is not None) and (self.content_fusion_id is not None)

    def handle_only_filename_id(self, analysis: Analysis):
        analysis.fusion_id = self.filename_fusion_id
        self.handle_dex_verification(analysis, self.filename_fusion_id)

    def handle_with_both_ids(self, analysis: Analysis):
        if self.filename_fusion_id != self.content_fusion_id:
            if self.filename_fusion_id not in self.content_fusion_ids_list:
                self.handle_mismatched_ids(analysis)
            else:
                self.content_fusion_id = self.filename_fusion_id
                analysis.fusion_id = self.filename_fusion_id
        else:
            analysis.fusion_id = self.filename_fusion_id
        self.handle_dex_verification(analysis, self.filename_fusion_id)

    def handle_mismatched_ids(self, analysis: Analysis):
        analysis.severity = Severity.refused
        issue = DifferentSprite(self.filename_fusion_id, self.content_fusion_id)
        analysis.issues.add(issue)
        self.handle_dex_verification(analysis, self.content_fusion_id)

    def handle_dex_verification(self, analysis: Analysis, fusion_id: str):
        if self.is_invalid_id(fusion_id):
            analysis.severity = Severity.refused
            analysis.issues.add(OutOfDex(fusion_id))

        elif self.is_custom_base or self.is_egg_sprite:
            handle_pokemon_name(analysis, fusion_id, self.is_egg_sprite)
        elif self.id_type.is_triple_fusion():
            analysis.issues.add(TripleFusionSprite())
        else:
            # Regular fusions
            handle_pokemon_names(analysis, fusion_id)

    def is_invalid_id(self, dex_id):
        return (self.is_invalid_fusion_dex_id(dex_id)
                or self.is_invalid_custom_base_or_egg_dex_id(dex_id))

    def is_invalid_custom_base_or_egg_dex_id(self, dex_id: str) -> bool:
        # Works for new egg format too
        return (self.is_custom_base or self.is_egg_sprite) and utils.is_invalid_base_id(dex_id)

    def is_invalid_fusion_dex_id(self, fusion_id: str) -> bool:
        # Works for triple fusions too
        return (not (self.is_custom_base or self.is_egg_sprite)) and utils.is_invalid_fusion_id(fusion_id)


def main(analysis: Analysis):
    if (analysis.specific_attachment is not None)\
            or analysis.has_attachment()\
            or analysis.has_zigzag_embed():
        handle_some_content(analysis)
        return

    handle_no_content(analysis)


def handle_some_content(analysis: Analysis):
    content_context = ContentContext(analysis)
    analysis.attachment_url = analysis.get_attachment_url()
    if content_context.has_both_fusion_ids():
        content_context.handle_with_both_ids(analysis)
    elif content_context.filename_fusion_id is not None:
        content_context.handle_only_filename_id(analysis)
    elif content_context.content_fusion_id is not None:
        handle_no_filename_id(analysis)
    else:
        handle_unknown_id(analysis)


def handle_no_filename_id(analysis: Analysis):
    analysis.severity = Severity.refused
    analysis.issues.add(MissingFilename())
    filename = analysis.get_filename()
    analysis.issues.add(FileName(filename))


def handle_no_content(analysis: Analysis):
    analysis.severity = Severity.ignored
    analysis.issues.add(MissingSprite())


def handle_unknown_id(analysis: Analysis):
    analysis.severity = Severity.ignored
    analysis.issues.add(UnknownSprite())
    filename = analysis.get_filename()
    analysis.issues.add(FileName(filename))


def handle_pokemon_names(analysis: Analysis, fusion_id: str):
    head, body = fusion_id.split(".")
    name_map = utils.id_to_name_map()
    head_name = name_map.get(head)
    body_name = name_map.get(body)
    analysis.issues.add(PokemonNames(head_name, body_name))


def handle_pokemon_name(analysis: Analysis, base_id: str, egg_sprite: bool = False):
    name_map = utils.id_to_name_map()
    pokemon_name = name_map.get(base_id)
    if egg_sprite:
        analysis.issues.add(EggSprite(pokemon_name))
    else:
        analysis.issues.add(CustomBase(pokemon_name))

