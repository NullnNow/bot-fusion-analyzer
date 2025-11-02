from enum import Enum, auto

import discord


class Description(str, Enum):
    missing_file        = "Missing sprite"
    missing_filename    = "Missing filename"
    missing_message_id  = "Missing fusion ID in gallery message"
    different_filenames = "Different fusions in the same gallery message"
    different_fusion_id = "Different IDs"
    colour_excess       = "Color excess"
    semi_transparent    = "Semi transparent pixels"
    intentional_transp  = "Intentional transparency"
    half_pixels         = "Half pixels detected"
    colour_amount       = "Colors"
    file_name           = "Filename"
    invalid_fusion_id   = "Invalid fusion ID"
    incorrect_gallery   = "Incorrect gallery"
    not_png             = "Invalid image format"
    invalid_size        = "Invalid size"
    custom              = "custom base"
    egg                 = "egg sprite"
    triple              = "Triple fusion"
    unknown_sprite      = "Unknown filename"
    no_transparency     = "Missing transparency"
    aseprite_user       = "Aseprite"
    graphics_gale_user  = "GraphicsGale"
    similarity_amount   = "Similarity"
    high_similarity     = "High number of similar color pairs"
    refused_similarity  = "Over maximum limit of similar color pairs"
    misplaced_grid      = "Not aligned in the grid (it's fine)"


class Severity(Enum):
    accepted        = "Valid"
    ignored         = "Unknown"
    controversial   = "Controversial"
    refused         = "Invalid"

    def is_warn_severity(self):
        return self != Severity.accepted


class DiscordColour(Enum):
    green   = discord.Colour(0x2ecc71)
    orange  = discord.Colour(0xe67e22)
    red     = discord.Colour(0xe74c3c)
    gray    = discord.Colour(0xcdcdcd)
    pink    = discord.Colour(0xff00ff)


class AnalysisType(Enum):
    sprite_gallery  = auto()
    assets_gallery  = auto()
    ping_reply      = auto()
    zigzag_fusion   = auto()
    zigzag_base     = auto()
    auto_spritework = auto()

    def is_gallery(self):
        return self.is_sprite_gallery() or self.is_assets_gallery()

    def is_assets_gallery(self):
        return (self == AnalysisType.assets_gallery) or (self == AnalysisType.zigzag_base)

    def is_sprite_gallery(self):
        return (self == AnalysisType.sprite_gallery) or (self == AnalysisType.zigzag_fusion)

    def is_reply(self):
        return (self == AnalysisType.ping_reply) or (self == AnalysisType.auto_spritework)

    def is_zigzag_galpost(self):
        return (self == AnalysisType.zigzag_fusion) or (self == AnalysisType.zigzag_base)

    def is_automatic_spritework_analysis(self):
        return self == AnalysisType.auto_spritework


class IdType(Enum):
    fusion      = "Fusion"
    custom_base = "Custom base"
    egg         = "Egg sprite"
    triple      = "Triple fusion"
    unknown     = "Unknown"

    def is_fusion(self):
        return self == IdType.fusion

    def is_custom_base(self):
        return self == IdType.custom_base

    def is_egg(self):
        return self == IdType.egg

    def is_triple_fusion(self):
        return self == IdType.triple

    def is_unknown(self):
        return self == IdType.unknown
