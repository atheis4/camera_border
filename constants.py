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
    "white": Colors.WHITE,
    "yellow": Colors.YELLOW,
}


def process_color_args(primary_color=None, secondary_color=None, profile=None):
    if not primary_color or not secondary_color:
        return PROFILE_TO_PALETTE[profile]
    return COLOR_STR_TO_COLOR[primary_color], COLOR_STR_TO_COLOR[secondary_color]


ASPECT_RATIO_TO_DIMENSIONS = {
    AspectRatioEnum.ONE_BY_ONE: (1120, 1120), 
    AspectRatioEnum.FOUR_BY_THREE: (1120, 840), 
    AspectRatioEnum.SIXTEEN_BY_NINE: (1120, 700),
}

WIDTH = 1120
HEIGHT = 700
INTERVAL = 20
LAYER_OFFSET = 70
GRADIENT_OFFSET = 80
INTERIOR_OFFSET = 90
LAYER_WIDTH = WIDTH - LAYER_OFFSET * 2
LAYER_HEIGHT = HEIGHT - LAYER_OFFSET * 2
GRADIENT_WIDTH = WIDTH - GRADIENT_OFFSET * 2
GRADIENT_HEIGHT = HEIGHT - GRADIENT_OFFSET * 2

INTERIOR_ORIGIN = (INTERIOR_OFFSET, INTERIOR_OFFSET)
ORIGIN = (0, 0)


class Corners:
    TOP_LEFT = (0, 0)
    TOP_RIGHT = (WIDTH, 0)
    BOTTOM_RIGHT = (WIDTH, HEIGHT)
    BOTTOM_LEFT = (0, HEIGHT)

    @staticmethod
    def get_top_right(width):
        return (width, 0)

    @staticmethod
    def get_bottom_right(width, height):
        return (width, height)

    @staticmethod
    def get_top_left():
        return (0, 0)

    @staticmethod
    def get_bottom_left(height):
        return (0, height)
