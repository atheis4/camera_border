#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFilter
import math

import constants


class Coordinates:
    CENTER = (constants.GRADIENT_WIDTH / 2, constants.GRADIENT_HEIGHT / 2)

    def __init__(self, width, height, degrees):
        self.width = width
        self.height = height
        self.degrees = degrees
        self.coords = None

    @classmethod
    def create_new(cls, width, height, degrees):
        coords = cls(width, height, degrees)
        coords.gen_coordinates()
        return coords

    def gen_coordinates(self):
        start = (0, constants.GRADIENT_HEIGHT / 2)
        end = self.invert_point(start)
        radius = self.pythagorean(self.CENTER[0], self.CENTER[1])
        coords = []
        theta = self.degrees + 180
        while theta <= 360:
            x, y = self.CENTER
            dx = self.get_change_in_x(x, radius, theta)
            dy = self.get_change_in_y(y, radius, theta)
            # process start/end point to fix to gradient
            start = self.adjust_to_rectangle((dx, dy), theta)
            start = Layer.add_gradient_offset(start)
            end = self.invert_point(start)

            coords.append((start, end))
            theta += self.degrees

        self.coords = coords

    def adjust_to_rectangle(self, point, theta):
        x, y = point
        if theta == 360:
            # horizontal
            x = 0 if x < 0 else constants.GRADIENT_WIDTH
            return x, constants.GRADIENT_HEIGHT / 2
        elif theta == 270:
            # vertical
            y = 0 if y < 0 else constants.GRADIENT_HEIGHT
            return constants.GRADIENT_WIDTH / 2, y
        else:
            m = self.get_slope_from_angle(theta)
            return self.trim_point(point, m)

    @staticmethod
    def trim_point(point, slope):
        x1, y1 = point
        if y1 < 0:
            # y must be fixed to zero.
            y2 = 0
            return (y2 - y1) / slope + x1, y2
        else:
            # x must be fixed to 0 or constants.GRADIENT_WIDTH
            x2 = 0 if x1 < constants.GRADIENT_WIDTH else constants.GRADIENT_WIDTH
            return x2, slope * (x2 - x1) + y1

    @staticmethod
    def get_change_in_x(x, radius, theta):
        return x + radius * math.cos(math.radians(theta))

    @staticmethod
    def get_change_in_y(y, radius, theta):
        return y + radius * math.sin(math.radians(theta))

    @staticmethod
    def get_slope_from_angle(theta):
        return math.tan(math.radians(theta))

    @staticmethod
    def invert_point(point):
        x, y = point
        return constants.WIDTH - x, constants.HEIGHT - y

    @staticmethod
    def pythagorean(a, b):
        return math.sqrt(pow(a, 2) + pow(b, 2))


class Gradient:
    def __init__(self, start, end, primary_color, secondary_color):
        self.start = start
        self.end = end
        self.primary_color = primary_color
        self.secondary_color = secondary_color

        self.slope = None
        self.slope_type = constants.SlopeEnum.DEFAULT
        self.perpendicular_slope = None
        self.interval = None
        self.interval_dim = None
        self.color_map = None

    @classmethod
    def create_new(cls, start, end, primary_color, secondary_color):
        gradient = cls(start, end, primary_color, secondary_color)
        gradient.gen_slope()
        gradient.gen_interval()
        gradient.gen_color_map()
        return gradient

    def gen_slope(self):
        x1, y1 = self.start
        x2, y2 = self.end
        try:
            m = (y2 - y1) / (x2 - x1)
        except ZeroDivisionError:
            self.slope_type = constants.SlopeEnum.VERTICAL
            return
        try:
            m1 = -1 / m
        except ZeroDivisionError:
            self.slope_type = constants.SlopeEnum.HORIZONTAL
            return
        self.slope = m
        self.perpendicular_slope = m1
        self.slope_type = constants.SlopeEnum.DEFAULT

    def gen_interval(self):
        dx = abs(self.end[0] - self.start[0])
        dy = abs(self.end[1] - self.start[1])
        self.interval = round(max(dx, dy))
        self.interval_dim = (
            constants.IntervalEnum.HORIZONTAL
            if dx > dy
            else constants.IntervalEnum.VERTICAL
        )

    def gen_color_map(self):
        self.color_map = self.interpolate(
            self.interval, self.primary_color, self.secondary_color
        )

    @staticmethod
    def interpolate(interval, primary_color, secondary_color):
        color_delta = [
            (right - left) / interval
            for left, right in zip(primary_color, secondary_color)
        ]
        for i in range(interval + 1):
            yield [
                round(color + delta * i)
                for color, delta in zip(primary_color, color_delta)
            ]


class Layer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = None
        self.drawing = None

    @classmethod
    def create_new(cls, width=constants.WIDTH, height=constants.HEIGHT):
        image = cls(width, height)
        image.gen_pil_image()
        image.gen_drawing()
        return image

    def gen_pil_image(self):
        self.image = Image.new("RGBA", (self.width, self.height), color=0)

    def save(self, filename):
        with open(filename, "wb") as f:
            self.image.save(f)

    def gen_drawing(self):
        self.drawing = ImageDraw.Draw(self.image)

    def apply_gradient(self, gradient):
        self.fill_edges(gradient)
        self.fill_gradient(gradient)

    def fill_gradient(self, gradient):
        # vertical/horizontal
        if gradient.slope_type != constants.SlopeEnum.DEFAULT:
            self.fill_linear_gradient(gradient)
        else:
            self.fill_gradient_impl(gradient)

    def fill_edges(self, gradient):
        if gradient.slope_type != constants.SlopeEnum.DEFAULT:
            self.fill_linear_edges(gradient)
        else:
            self.fill_polygon_edges(gradient)

    def fill_linear_edges(self, gradient):
        rectangle_map = {
            constants.SlopeEnum.HORIZONTAL: self.fill_vertical_rectangles,
            constants.SlopeEnum.VERTICAL: self.fill_horizontal_rectangles,
        }
        rectangle_map[gradient.slope_type](gradient)

    def fill_vertical_rectangles(self, gradient):
        x, _ = gradient.start
        if x > constants.WIDTH / 2:
            left_color = gradient.secondary_color
            right_color = gradient.primary_color
        else:
            left_color = gradient.primary_color
            right_color = gradient.secondary_color
        # left
        self.drawing.polygon(
            [
                constants.Corners.TOP_LEFT,
                (constants.GRADIENT_OFFSET, 0),
                (constants.GRADIENT_OFFSET, constants.HEIGHT),
                constants.Corners.BOTTOM_LEFT,
            ],
            fill=left_color,
        )
        # right
        self.drawing.polygon(
            [
                constants.Corners.TOP_RIGHT,
                (constants.GRADIENT_WIDTH + constants.GRADIENT_OFFSET, 0),
                (
                    constants.GRADIENT_WIDTH + constants.GRADIENT_OFFSET,
                    constants.HEIGHT,
                ),
                constants.Corners.BOTTOM_RIGHT,
            ],
            fill=right_color,
        )

    def fill_horizontal_rectangles(self, gradient):
        _, y = gradient.start
        if y < constants.HEIGHT / 2:
            top_color = gradient.primary_color
            bottom_color = gradient.secondary_color
        else:
            top_color = gradient.secondary_color
            bottom_color = gradient.primary_color
        # top
        self.drawing.polygon(
            [
                constants.Corners.TOP_RIGHT,
                constants.Corners.TOP_LEFT,
                (0, constants.GRADIENT_OFFSET),
                (constants.WIDTH, constants.GRADIENT_OFFSET),
            ],
            fill=top_color,
        )
        # bottom
        self.drawing.polygon(
            [
                constants.Corners.BOTTOM_RIGHT,
                constants.Corners.BOTTOM_LEFT,
                (
                    0,
                    constants.GRADIENT_HEIGHT + constants.GRADIENT_OFFSET,
                ),
                (
                    constants.WIDTH,
                    constants.GRADIENT_HEIGHT + constants.GRADIENT_OFFSET,
                ),
            ],
            fill=bottom_color,
        )

    def fill_linear_gradient(self, gradient):
        x, y = gradient.start
        for i, color in enumerate(gradient.color_map):
            if gradient.interval_dim == constants.IntervalEnum.HORIZONTAL:
                x_coord = (
                    0 + i
                    if x < constants.GRADIENT_WIDTH / 2
                    else constants.GRADIENT_WIDTH - i
                )
                coordinates = [
                    (x_coord + constants.GRADIENT_OFFSET, 0),
                    (x_coord + constants.GRADIENT_OFFSET, constants.HEIGHT),
                ]
            else:
                y_coord = (
                    0 + i
                    if y < constants.GRADIENT_HEIGHT / 2
                    else constants.GRADIENT_HEIGHT - i
                )
                coordinates = [
                    (0, y_coord + constants.GRADIENT_OFFSET),
                    (constants.WIDTH, y_coord + constants.GRADIENT_OFFSET),
                ]
            self.drawing.line(
                coordinates,
                fill=tuple(color),
                width=1,
            )

    def fill_gradient_impl(self, gradient):
        start = gradient.start
        m = gradient.slope
        m1 = gradient.perpendicular_slope
        original_quadrant = self.get_quadrant(start)
        for i, color in enumerate(gradient.color_map, 1):
            # maybe need to update point...
            current_point = self.get_next_gradient_coords(
                m, start, i, gradient.interval_dim
            )
            first_intercept, second_intercept = self.get_intercepts(
                m1, current_point, original_quadrant
            )
            self.drawing.line(
                [first_intercept, second_intercept],
                fill=tuple(color),
                width=math.ceil(abs(m)) + 1,
            )

    def fill_polygon_edges(self, gradient):
        """
        Identifies the three points that make up the corner polygons of solid
        color for the gradient.
        """
        start, _ = gradient.start, gradient.end
        slope = gradient.perpendicular_slope
        quadrant = self.get_quadrant(start)

        first_intercept, second_intercept = self.get_intercepts(slope, start, quadrant)
        corner = self.get_corner_from_quadrant(quadrant)
        self.drawing.polygon(
            [corner, first_intercept, second_intercept],
            fill=gradient.primary_color,
        )
        # invert the polygon for the ending point - secondary color
        oppo_corner = Coordinates.invert_point(corner)
        oppo_first_intercept = Coordinates.invert_point(first_intercept)
        oppo_second_intercept = Coordinates.invert_point(second_intercept)
        self.drawing.polygon(
            [oppo_corner, oppo_first_intercept, oppo_second_intercept],
            fill=gradient.secondary_color,
        )

    def trim(self):
        self.trim_interior()
        self.trim_edges()

    def trim_interior(self):
        interior = Image.new(
            "RGBA",
            (constants.GRADIENT_WIDTH - 80, constants.GRADIENT_HEIGHT - 80),
            color=0,
        )
        self.image.paste(interior, box=constants.INTERIOR_ORIGIN)

    def trim_edges(self):
        horizontal_edges = Image.new(
            "RGBA",
            (constants.WIDTH, constants.LAYER_OFFSET),
            color=0,
        )
        self.image.paste(horizontal_edges)
        self.image.paste(
            horizontal_edges,
            box=(0, constants.LAYER_OFFSET + constants.LAYER_HEIGHT),
        )
        vertical_edges = Image.new(
            "RGBA",
            (constants.LAYER_OFFSET, constants.HEIGHT),
            color=0,
        )
        self.image.paste(vertical_edges)
        self.image.paste(
            vertical_edges,
            box=(constants.LAYER_OFFSET + constants.LAYER_WIDTH, 0),
        )

    def blur(self, radius):
        self.image = self.image.filter(ImageFilter.GaussianBlur(radius))

    @staticmethod
    def get_next_gradient_coords(m, start, interval, interval_dim):
        x1, y1 = start
        if interval_dim == constants.IntervalEnum.HORIZONTAL:
            x2 = x1 + interval
            return x2, abs(m * (x2 - x1) + y1)
        else:
            y2 = y1 + interval
            return abs((y2 - y1) / m + x1), y2

    # @staticmethod
    # def get_intercepts(m, point, quadrant):
    #     pass

    @staticmethod
    def get_intercepts(m, point, quadrant):
        x, y = point
        x2 = 0 if quadrant == constants.QuadrantEnum.FIRST else constants.WIDTH
        first_intercept = x2, m * (x2 - x) + y
        second_intercept = x + (-1 * y / m), 0
        return first_intercept, second_intercept

    @staticmethod
    def get_intercepts_for_gradient(m, point):
        x, y = point
        first_intercept = 0, m * (0 - x) + y
        second_intercept = x + (-1 * y / m), 0
        return first_intercept, second_intercept

    @staticmethod
    def get_quadrant(point):
        x, y = point
        if x < constants.WIDTH / 2:
            return (
                constants.QuadrantEnum.FIRST
                if y < constants.HEIGHT / 2
                else constants.QuadrantEnum.THIRD
            )
        else:
            return (
                constants.QuadrantEnum.SECOND
                if y < constants.HEIGHT / 2
                else constants.QuadrantEnum.FOURTH
            )

    @staticmethod
    def get_corner_from_quadrant(quadrant):
        return {
            constants.QuadrantEnum.FIRST: constants.Corners.TOP_LEFT,
            constants.QuadrantEnum.SECOND: constants.Corners.TOP_RIGHT,
            constants.QuadrantEnum.THIRD: constants.Corners.BOTTOM_LEFT,
            constants.QuadrantEnum.FOURTH: constants.Corners.BOTTOM_RIGHT,
        }[quadrant]

    @staticmethod
    def add_gradient_offset(point):
        x, y = point
        return x + constants.GRADIENT_OFFSET, y + constants.GRADIENT_OFFSET

    @staticmethod
    def add_layer_offset(point):
        x, y = point
        return x + constants.LAYER_OFFSET, y + constants.LAYER_OFFSET


if __name__ == "__main__":
    coords = Coordinates.create_new(
        width=constants.GRADIENT_WIDTH,
        height=constants.GRADIENT_HEIGHT,
        degrees=12,
    )

    # x1 = 2240
    # y1 = 2480
    # x2 = 2240
    # y2 = 0

    # start, end = (x1, y2), (x2, y1)
    # start, end = (320, 991.8914015935571), (4160, 1808.108598406443)
    start, end = (3726.4924741088666, 320), (753.5075258911334, 2480)
    # start, end = (3212.436367841666, 320), (1267.5636321583338, 2480)

    layer = Layer.create_new(constants.WIDTH, constants.HEIGHT)
    gradient = Gradient.create_new(
        start, end, constants.Colors.CYAN, constants.Colors.YELLOW
    )
    layer.apply_gradient(gradient)
    layer.trim()

    for coord in coords.coords:
        start, end = coord
        layer.drawing.line(
            [start, end],
            fill=constants.Colors.YELLOW,
            width=5,
        )

    layer.image.show()

    # primary_to_secondary = []
    # secondary_to_primary = []

    # counter = 0
    # for coord in coords.coords:
    #     start, end = coord
    #     # create layer
    #     first_layer = Layer.create_new(constants.WIDTH, constants.HEIGHT)
    #     first_gradient = Gradient.create_new(
    #         start, end, constants.Colors.CYAN, constants.Colors.YELLOW
    #     )
    #     # apply, trim, append both sets of layers
    #     first_layer.apply_gradient(first_gradient)
    #     first_layer.trim()

    #     for coord_guide in coords.coords:
    #         start_guide, end_guide = coord_guide
    #         first_layer.drawing.line(
    #             [start_guide, end_guide],
    #             fill=constants.Colors.YELLOW,
    #             width=5,
    #         )

    #     primary_to_secondary.append(first_layer.image)
    #     first_layer.image.save(f'1_cyan_to_yellow/{counter}_{start}_{end}.png')

    #     second_layer = Layer.create_new(constants.WIDTH, constants.HEIGHT)
    #     second_gradient = Gradient.create_new(
    #         start, end, constants.Colors.YELLOW, constants.Colors.CYAN
    #     )
    #     second_layer.apply_gradient(second_gradient)
    #     second_layer.trim()

    #     for coord_guide in coords.coords:
    #         start_guide, end_guide = coord_guide
    #         second_layer.drawing.line(
    #             [start_guide, end_guide],
    #             fill=constants.Colors.YELLOW,
    #             width=5,
    #         )

    #     secondary_to_primary.append(second_layer.image)
    #     second_layer.image.save(f'2_yellow_to_cyan/{counter}_{start}_{end}.png')
    #     counter += 1

    # primary_to_secondary.extend(secondary_to_primary)
    # # save as gif
    # primary_to_secondary[0].save(
    #     "camera_border_cyan_to_yellow.gif",
    #     save_all=True,
    #     append_images=primary_to_secondary[1:],
    # )
