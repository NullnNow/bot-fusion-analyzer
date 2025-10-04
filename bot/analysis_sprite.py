import requests
from analysis import Analysis
from utils import is_intentional_transparency
from enums import Severity
from exceptions import TransparencyException
from issues import (AsepriteUser, ColorAmount, ColorExcessControversial,
                    ColorExcessRefused, ColorOverExcess, GraphicsGaleUser,
                    HalfPixels, InvalidSize, MissingTransparency,
                    SimilarityAmount, SemiTransparency, CustomBase,
                    SimilarityExcessControversial, SimilarityExcessRefused,
                    MisplacedGrid, EggSprite, NotPng, IntentionalTransparency)

# Pillow
from PIL.Image import open as image_open
from PIL.Image import Image, new
from PIL.PyAccess import PyAccess

# Fuck colormath
import numpy


def patch_asscalar(a):
    return a.item()


setattr(numpy, "asscalar", patch_asscalar)

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000, delta_e_cmc

colorType = int | tuple

TIMEOUT = 10

MAX_SIZE = 288
EGG_SIZE = 160

ALL_COLOR_LIMIT = 256
REFUSED_COLOR_LIMIT = 64
CONTROVERSIAL_COLOR_LIMIT = 32
CUSTOM_BASE_REFUSED_COLOR_LIMIT = 32
CUSTOM_BASE_CONTROV_COLOR_LIMIT = 20

DIFFERENCE_COLOR_LIMIT = 32
DELTA_COLOR_LIMIT = 10

CONTROVERSIAL_SIMILARITY_LIMIT = 10
REFUSED_SIMILARITY_LIMIT = 20
CUSTOM_BASE_CONTROV_SIM_LIMIT = 6
CUSTOM_BASE_REFUSED_SIM_LIMIT = 15

STEP = 3
EGG_STEP = 2
ASEPRITE_RATIO = 2

PINK = (255, 0, 255, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)


class SpriteContext():
    def __init__(self, analysis: Analysis):
        if analysis.attachment_url is None:
            raise RuntimeError()

        raw_data = requests.get(analysis.attachment_url, stream=True, timeout=TIMEOUT).raw
        self.image = image_open(raw_data)
        self.pixels = get_pixels(self.image)

        self.useful_amount: int = 0
        self.useless_amount: int = 0

        self.useful_colors: list = []
        self.similar_color_dict: dict = {}

        # To both cover:
        # replied custom bases detected in analysis_content
        # and custom bases from assets gallery

        if analysis.type.is_assets_gallery() or analysis.issues.has_issue(CustomBase):
            self.refused_color_lim = CUSTOM_BASE_REFUSED_COLOR_LIMIT
            self.controv_color_lim = CUSTOM_BASE_CONTROV_COLOR_LIMIT
            self.refused_sim_lim = CUSTOM_BASE_REFUSED_SIM_LIMIT
            self.controv_sim_lim = CUSTOM_BASE_CONTROV_SIM_LIMIT
        else:
            self.refused_color_lim = REFUSED_COLOR_LIMIT
            self.controv_color_lim = CONTROVERSIAL_COLOR_LIMIT
            self.refused_sim_lim = REFUSED_SIMILARITY_LIMIT
            self.controv_sim_lim = CONTROVERSIAL_SIMILARITY_LIMIT

        self.egg_sprite = analysis.issues.has_issue(EggSprite)
        if self.egg_sprite:
            self.max_size = EGG_SIZE
            self.step =  EGG_STEP
        else:
            self.max_size = MAX_SIZE
            self.step = STEP

        self.valid_size = (self.max_size, self.max_size)

    def handle_sprite_format(self, analysis:Analysis):
        # Ensures that the image is actually a png
        file_format = self.image.format
        if file_format != "PNG":
            analysis.severity = Severity.refused
            analysis.issues.add(NotPng(file_format))

    def turn_image_into_rgb(self):
        # Avoids having to deal with indexed palette quirks
        if self.image.mode != "RGBA":
            self.image = self.image.convert(mode="RGBA")

    def handle_sprite_size(self, analysis: Analysis):
        image_size = self.image.size
        if image_size == self.valid_size:
            analysis.ai_suspicion -= 4
            return

        analysis.size_issue = True
        analysis.severity = Severity.refused
        analysis.issues.add(InvalidSize(image_size))
        if image_size == (1024, 1024):
            analysis.ai_suspicion += 8
        elif image_size == (96, 96):
            analysis.ai_suspicion -= 2

    def handle_sprite_colors(self, analysis: Analysis):
        all_colors = self.image.getcolors(ALL_COLOR_LIMIT)
        if is_color_excess(all_colors):
            analysis.severity = Severity.refused
            analysis.issues.add(ColorOverExcess(ALL_COLOR_LIMIT))
            analysis.ai_suspicion += 6
        else:
            self.handle_color_count(analysis, all_colors)
            self.handle_color_limit(analysis)
            if self.useful_amount <= self.refused_color_lim:
                self.handle_color_similarity(analysis)
            self.handle_aseprite(analysis)
            self.handle_graphics_gale(analysis)
            analysis.ai_suspicion -= 2

    def handle_color_count(self, analysis: Analysis, all_colors: list):
        try:
            self.useful_colors = remove_useless_colors(all_colors)
            self.handle_color_amount(analysis, all_colors)
        except TransparencyException:
            analysis.severity = Severity.refused
            analysis.issues.add(MissingTransparency())
            analysis.ai_suspicion += 4

    def handle_color_amount(self, analysis: Analysis, all_colors):
        all_amount = len(all_colors)
        self.useful_amount = len(self.useful_colors)
        self.useless_amount = all_amount - self.useful_amount
        analysis.issues.add(ColorAmount(self.useful_amount))

    def handle_color_similarity(self, analysis: Analysis):
        similarity_amount = self.get_similarity_amount()
        analysis.issues.add(SimilarityAmount(similarity_amount))
        if similarity_amount > self.refused_sim_lim:
            analysis.severity = Severity.refused
            analysis.issues.add(SimilarityExcessRefused(self.refused_sim_lim))
        elif (similarity_amount > self.controv_sim_lim) and (analysis.severity is not Severity.refused):
            analysis.severity = Severity.controversial
            analysis.issues.add(SimilarityExcessControversial(self.controv_sim_lim))

    def handle_color_limit(self, analysis: Analysis):
        if self.useful_amount > self.refused_color_lim:
            analysis.issues.add(ColorExcessRefused(self.refused_color_lim))
            analysis.severity = Severity.refused
        elif self.useful_amount > self.controv_color_lim:
            analysis.issues.add(ColorExcessControversial(self.controv_color_lim))
            if analysis.severity is not Severity.refused:
                analysis.severity = Severity.controversial

    def handle_aseprite(self, analysis: Analysis):
        if self.useful_amount != 0:
            aseprite_ratio = self.useless_amount / self.useful_amount
            if aseprite_ratio > ASEPRITE_RATIO:
                analysis.issues.add(AsepriteUser(aseprite_ratio))

    def handle_graphics_gale(self, analysis: Analysis):
        is_graphics_gale = "GLDPNG" in self.image.info.get("Software", "")
        if is_graphics_gale:
            analysis.issues.add(GraphicsGaleUser())

    def handle_sprite_transparency(self, analysis: Analysis):
        if analysis.size_issue:
            return

        try:
            transparency_amount, image = self.highlight_transparency()
        except TransparencyException:
            return

        if transparency_amount == 0:
            return

        if is_intentional_transparency(analysis.message):
            analysis.issues.add(IntentionalTransparency())
            return
        analysis.transparency_issue = True
        analysis.transparency_image = image
        if analysis.severity is not Severity.refused:
            analysis.severity = Severity.controversial
        analysis.issues.add(SemiTransparency())


    def get_similarity_amount(self):
        try:
            rgb_color_list = get_rgb_color_list(self.useful_colors)
            self.similar_color_dict = get_similar_color_dict(rgb_color_list)
            self.similar_color_dict = sort_color_dict(self.similar_color_dict)
            similarity_amount = len(self.similar_color_dict)
        except ValueError:
            similarity_amount = -1
        return similarity_amount

    def handle_sprite_half_pixels(self, analysis: Analysis):
        if analysis.size_issue:
            return

        half_pixels_amount, image = self.highlight_half_pixels(strict_grid=True)
        if half_pixels_amount == 0:
            return

        # If the strict search returns half pixels, double check to check
        # if they are real, or it's just that the grid doesn't align
        lax_half_pixels_amount = self.highlight_half_pixels(strict_grid=False)[0]
        if lax_half_pixels_amount > 0:
            analysis.half_pixels_issue = True
            analysis.half_pixels_image = image
            analysis.severity = Severity.refused
            analysis.issues.add(HalfPixels())
        else:
            analysis.issues.add(MisplacedGrid())


    def highlight_transparency(self) -> tuple[int, Image]:
        """# TransparencyException"""
        local_image = new("RGBA", (self.max_size, self.max_size))
        local_pixels = get_pixels(local_image)
        first_pixel = self.pixels[0, 0]
        transparency_amount = 0
        is_there_transparency = False
        if is_indexed(first_pixel):
            return transparency_amount, local_image
        for i in range(0, self.max_size):
            for j in range(0, self.max_size):
                color = self.pixels[i, j]
                alpha = get_alpha(color)
                if is_half_transparent(alpha):
                    local_pixels[i, j] = PINK
                    transparency_amount += 1
                elif not is_transparent(alpha):
                    local_pixels[i, j] = BLACK
                else:
                    local_pixels[i, j] = WHITE
                    is_there_transparency = True
        if not is_there_transparency:
            raise TransparencyException
        return transparency_amount, local_image

    def highlight_half_pixels(self, strict_grid:bool = False) -> tuple[int, Image]:
        local_image = new("RGBA", (self.max_size, self.max_size))
        local_pixels = get_pixels(local_image)
        if strict_grid:
            (delta_i, delta_j) = (0,0)
        else:
            (delta_i, delta_j) = find_first_pixel(self.pixels, self.max_size)
        max_i = self.max_size - (self.step - delta_i)
        max_j = self.max_size - (self.step - delta_j)
        half_pixels_amount = 0
        for i in range(delta_i, max_i, self.step):
            for j in range(delta_j, max_j, self.step):
                color_set = get_color_set(i, j, self.pixels, self.step)
                color = get_color_from_set(color_set)
                recolor_pixels(i, j, local_pixels, color, self.step)
                if color == RED:
                    half_pixels_amount += (self.step * self.step)
        return half_pixels_amount, local_image


def get_similar_color_dict(rgb_color_list):
    color_dict = {}
    for color_a in rgb_color_list:
        for color_b in rgb_color_list:
            if color_a == color_b:
                continue
            color_delta = get_color_delta(color_a, color_b)
            if is_similar(color_delta):
                frozen_set = frozenset([color_a, color_b])
                color_dict[frozen_set] = color_delta
    return color_dict


def sort_color_dict(some_dict: dict):
    return dict(sorted(some_dict.items(), key=sort_element))


def sort_element(x):
    return x[1][2]


def print_color_dict(color_dict: dict):
    for key, value in color_dict.items():
        color: list = list(key)
        deltas = f"({value[0]}, {value[1]}) : {value[2]}"
        print(deltas, color)


def get_rgb_color_list(color_data_list: list) -> list[tuple[int, int, int]]:
    rgb_color_list = []
    for color_data in color_data_list:
        rgb_color = color_data[1][0:3]
        rgb_color_list.append(rgb_color)
    return rgb_color_list


# Maximum number of colors. If this number is exceeded, this method returns None.
def is_color_excess(color_list: list | None):
    return color_list is None


def is_half_transparent(alpha):
    return alpha != 0 and alpha != 255


def is_transparent(alpha: int) -> bool:
    return alpha == 0


def get_pixels(image: Image) -> PyAccess:
    return image.load()  # type: ignore


def remove_useless_colors(old_colors: list):
    """# TransparencyException"""
    new_colors = []
    for old_color in old_colors:
        _color_amount, color_value = old_color
        if not is_useless_color(color_value):
            new_colors.append(old_color)
    return new_colors


def is_useless_color(color: colorType):
    """# TransparencyException"""
    if is_indexed(color):
        return False
    alpha = get_alpha(color)  # type: ignore
    return is_transparent(alpha)


def get_alpha(color: tuple) -> int:
    """# TransparencyException"""
    if len(color) != 4:
        raise TransparencyException()
    _r, _g, _b, alpha = color
    return alpha


def is_indexed(color: colorType) -> bool:
    return isinstance(color, int)


def find_first_pixel(pixels: PyAccess, max_size: int):
    default_value = pixels[0, 0]
    for i in range(0, max_size):
        for j in range(0, max_size):
            if default_value != pixels[i, j]:
                return i % 3, j % 3
    return 0, 0


def get_color_set(i: int, j: int, pixels: PyAccess, step: int):
    color_set = set()
    for increment_i in range(0, step):
        for increment_j in range(0, step):
            local_i = i + increment_i
            local_j = j + increment_j
            pixel = pixels[local_i, local_j]
            # Equalize all colored fully transparent pixels
            if (isinstance(pixel, tuple)
                    and len(pixel) == 4
                    and pixel[3] == 0):
                pixel = (0, 0, 0, 0)
            color_set.add(pixel)
    return color_set


def get_color_from_set(color_set: set):
    if len(color_set) > 1:
        return RED
    return GREEN


def recolor_pixels(i: int, j: int, pixels: PyAccess, color: tuple, step: int):
    for increment_i in range(0, step):
        for increment_j in range(0, step):
            local_i = i + increment_i
            local_j = j + increment_j
            pixels[local_i, local_j] = color


def is_similar(color_delta):
    if color_delta[0] > DELTA_COLOR_LIMIT:
        return False
    if color_delta[1] > DELTA_COLOR_LIMIT:
        return False
    if color_delta[2] > DIFFERENCE_COLOR_LIMIT:
        return False
    return True


def get_max_difference(rgb_a: tuple, rgb_b: tuple):
    red_difference = abs(rgb_a[0] - rgb_b[0])
    green_difference = abs(rgb_a[1] - rgb_b[1])
    blue_difference = abs(rgb_a[2] - rgb_b[2])
    return max(red_difference, green_difference, blue_difference)


def get_color_delta(rgb_a: tuple, rgb_b: tuple):
    color_rgb_a = sRGBColor(rgb_a[0], rgb_a[1], rgb_a[2], True)
    color_rgb_b = sRGBColor(rgb_b[0], rgb_b[1], rgb_b[2], True)
    color_lab_a = convert_color(color_rgb_a, LabColor)
    color_lab_b = convert_color(color_rgb_b, LabColor)
    cie2000 = delta_e_cie2000(color_lab_a, color_lab_b)
    cmc = delta_e_cmc(color_lab_a, color_lab_b)
    max_difference = get_max_difference(rgb_a, rgb_b)
    return [int(cie2000), int(cmc), max_difference]


def main(analysis: Analysis):
    if (analysis.severity == Severity.accepted) or analysis.type.is_reply():
        handle_valid_sprite(analysis)


def handle_valid_sprite(analysis: Analysis):
    context = SpriteContext(analysis)
    context.handle_sprite_format(analysis)
    context.turn_image_into_rgb()
    context.handle_sprite_size(analysis)
    context.handle_sprite_colors(analysis)
    context.handle_sprite_transparency(analysis)
    context.handle_sprite_half_pixels(analysis)
