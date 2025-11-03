from bot.misc.enums import Description, Severity, IdType


class Issue:
    description: Description
    severity: Severity

    def __str__(self) -> str:
        return self.description.value


class Issues:
    issue_list: list[Issue]

    def __init__(self):
        self.issue_list = []

    def __str__(self) -> str:
        result = ""
        for issue in self.issue_list:
            result += f"- **{issue}**\n"
        return result

    def add(self, issue: Issue):
        self.issue_list.append(issue)

    def has_issue(self, issue_type) -> bool:
        return any(isinstance(issue, issue_type) for issue in self.issue_list)



class DifferentSprite(Issue):
    description = Description.different_fusion_id
    severity = Severity.refused

    def __init__(self, filename_fusion_id: str, content_fusion_id: str) -> None:
        self.filename_fusion_id = filename_fusion_id
        self.content_fusion_id = content_fusion_id

    def __str__(self) -> str:
        return f"{self.description.value} ({self.filename_fusion_id}) ({self.content_fusion_id})"


class MissingFilename(Issue):
    description = Description.missing_filename
    severity = Severity.refused


class MissingSprite(Issue):
    description = Description.missing_file
    severity = Severity.ignored


class MissingMessageId(Issue):
    description = Description.missing_message_id
    severity = Severity.refused


class DifferentFilenameIds(Issue):
    description = Description.different_filenames
    severity = Severity.refused


class PokemonNames(Issue):
    severity = Severity.accepted

    def __init__(self, head_id: str, body_id: str) -> None:
        self.head_name = head_id
        self.body_name = body_id

    def __str__(self) -> str:
        return f"{self.head_name}/{self.body_name}"


class CustomBase(Issue):
    description = Description.custom
    severity = Severity.accepted

    def __init__(self, base_name: str = "Unknown") -> None:
        self.base_name = base_name

    def __str__(self) -> str:
        return f"{self.base_name} {self.description.value}"


class EggSprite(Issue):
    description = Description.egg
    severity = Severity.accepted

    def __init__(self, egg_name: str = "Unknown") -> None:
        self.egg_name = egg_name

    def __str__(self) -> str:
        return f"{self.egg_name} {self.description.value}"


class TripleFusionSprite(Issue):
    description = Description.triple
    severity = Severity.accepted


class UnknownSprite(Issue):
    description = Description.unknown_sprite
    severity = Severity.ignored


class OutOfDex(Issue):
    description = Description.invalid_fusion_id
    severity = Severity.refused

    def __init__(self, fusion_id: str) -> None:
        self.fusion_id = fusion_id

    def __str__(self) -> str:
        return f"{self.description.value} ({self.fusion_id})"


class IncorrectGallery(Issue):
    description = Description.incorrect_gallery
    severity = Severity.refused

    def __init__(self, id_type: IdType, gallery: str):
        self.id_type = id_type.value
        self.gallery = gallery

    def __str__(self) -> str:
        return f"{self.description.value}: {self.id_type} in {self.gallery}"


class WrongLetter(Issue):
    description = Description.wrong_letter

    def __init__(self, correct_letter: str):
        self.correct_letter = correct_letter

    def __str__(self) -> str:
        return f"{self.description.value}: should be {self.correct_letter}"


class NotPng(Issue):
    description = Description.not_png
    severity = Severity.refused

    def __init__(self, file_format: str) -> None:
        self.file_format = file_format

    def __str__(self) -> str:
        return f"{self.description.value}: {self.file_format}"


class InvalidSize(Issue):
    description = Description.invalid_size
    severity = Severity.refused

    def __init__(self, size: tuple) -> None:
        self.size = size

    def __str__(self) -> str:
        return f"{self.description.value} {self.size}"


class FileName(Issue):
    description = Description.file_name
    severity = Severity.accepted

    def __init__(self, filename: str) -> None:
        self.filename = filename

    def __str__(self) -> str:
        return f"{self.description.value}: {self.filename}"


class ColorAmount(Issue):
    description = Description.colour_amount
    severity = Severity.accepted

    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.description.value}: {self.amount}"


class ColorExcessRefused(Issue):
    description = Description.colour_excess
    severity = Severity.refused

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (max: {self.maximum})"


class ColorExcessControversial(Issue):
    description = Description.colour_excess
    severity = Severity.controversial

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (over {self.maximum})"


class ColorOverExcess(Issue):
    description = Description.colour_excess
    severity = Severity.refused

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (+{self.maximum})"


class SimilarityExcessControversial(Issue):
    description = Description.high_similarity
    severity = Severity.refused

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (over {self.maximum})"


class SimilarityExcessRefused(Issue):
    description = Description.refused_similarity
    severity = Severity.controversial

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.description.value} (limit: {self.maximum})"


class MissingTransparency(Issue):
    description = Description.no_transparency
    severity = Severity.refused


class AsepriteUser(Issue):
    description = Description.aseprite_user
    severity = Severity.accepted

    def __init__(self, ratio: float) -> None:
        self.ratio = int(ratio)

    def __str__(self) -> str:
        return f"{self.description.value} (r{self.ratio})"


class GraphicsGaleUser(Issue):
    description = Description.graphics_gale_user
    severity = Severity.accepted


class SemiTransparency(Issue):
    description = Description.semi_transparent
    severity = Severity.controversial


class IntentionalTransparency(Issue):
    description = Description.intentional_transp
    severity = Severity.accepted


class SimilarityAmount(Issue):
    description = Description.similarity_amount
    severity = Severity.controversial

    def __init__(self, amount: int) -> None:
        self.amount = amount

    def __str__(self) -> str:
        return f"{self.description.value}: {self.amount}"


class HalfPixels(Issue):
    description = Description.half_pixels
    severity = Severity.refused


class MisplacedGrid(Issue):
    description = Description.misplaced_grid
    severity = Severity.controversial