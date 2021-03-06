from enum import Enum


class AspectRatioEnum(Enum):
    ONE_BY_ONE = 1
    FOUR_BY_THREE = 2
    SIXTEEN_BY_NINE = 3


class IntervalEnum(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class QuadrantEnum(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


class SlopeEnum(Enum):
    DEFAULT = 1
    HORIZONTAL = 2
    VERTICAL = 3


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    PURPLE = (113, 27, 248)  # #711BF8


PROFILE_TO_PALETTE = {
    "cm": (Colors.CYAN, Colors.MAGENTA),
    "cy": (Colors.CYAN, Colors.YELLOW),
    "my": (Colors.MAGENTA, Colors.YELLOW),
    "imposter": (Colors.BLACK, Colors.RED),
}

COLOR_STR_TO_COLOR = {
    "black": Colors.BLACK,
    "blue": Colors.BLUE,
    "cyan": Colors.CYAN,
    "green": Colors.GREEN,
    "magenta": Colors.MAGENTA,
    "purple": Colors.PURPLE,
    "red": Colors.RED,
    "white": Colors.WHITE,
    "yellow": Colors.YELLOW,
}

ASPECT_STR_TO_ENUM = {
    "16:9": AspectRatioEnum.SIXTEEN_BY_NINE,
    "4:3": AspectRatioEnum.FOUR_BY_THREE,
    "1:1": AspectRatioEnum.ONE_BY_ONE,
}

ASPECT_RATIO_TO_DIMENSIONS = {
    AspectRatioEnum.ONE_BY_ONE: (1120, 1120), 
    AspectRatioEnum.FOUR_BY_THREE: (1120, 840), 
    AspectRatioEnum.SIXTEEN_BY_NINE: (1120, 700),
}
