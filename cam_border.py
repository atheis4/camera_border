import math
import os
from PIL import Image, ImageDraw, ImageFilter

import constants


class Coordinates:
    """
    Responsible for generating the coordinate tuples along
    the rectangle, as defined by the dimensions object.
    """

    def __init__(self, dimensions, degrees):
        self.dimensions = dimensions
        self.degrees = degrees
        self.coords = None

    @classmethod
    def create_new(cls, dimensions, degrees):
        coords = cls(dimensions, degrees)
        coords.gen_coordinates()
        return coords

    def gen_coordinates(self):
        """
        Iterate around a circle and generate the points on a
        rectangle for the gradient start and end points.
        """
        start = (0, self.dimensions.gradient_height / 2)
        end = self.dimensions.invert_point(start)
        radius = self.pythagorean(self.dimensions.gradient_center)
        coords = []
        theta = self.degrees + 180
        while theta <= 360:
            x, y = self.dimensions.gradient_center
            dx = self.get_change_in_x(x, radius, theta)
            dy = self.get_change_in_y(y, radius, theta)
            # process start/end point to fix to gradient
            start = self.adjust_to_rectangle((dx, dy), theta)
            start = Layer.add_gradient_offset(start)
            end = self.dimensions.invert_point(start)

            coords.append((start, end))
            theta += self.degrees

        self.coords = coords

    def adjust_to_rectangle(self, point, theta):
        x, y = point
        if theta == 360:
            # horizontal
            x = 0 if x < 0 else self.dimensions.gradient_width
            return x, self.dimensions.gradient_height / 2
        elif theta == 270:
            # vertical
            y = 0 if y < 0 else self.dimensions.gradient_height
            return self.dimensions.gradient_width / 2, y
        else:
            m = self.get_slope_from_angle(theta)
            return self.trim_point(point, m)

    def trim_point(self, point, slope):
        x1, y1 = point
        if y1 < 0:
            # y must be fixed to zero.
            y2 = 0
            return (y2 - y1) / slope + x1, y2
        else:
            # x must be fixed to 0 or self.dimensions.gradient_width
            x2 = (
                0
                if x1 < self.dimensions.gradient_width
                else self.dimensions.gradient_width
            )
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
    def pythagorean(point):
        a, b = point
        return math.sqrt(pow(a, 2) + pow(b, 2))


class Dimensions:
    """
    Responsible for keeping track of the the various dimensions 
    of the camera border--including overall width/height, layer
    width/height, and gradient width/height.
    """

    INTERVAL = 20
    LAYER_OFFSET = 70
    GRADIENT_OFFSET = 80
    INTERIOR_OFFSET = 90
    ORIGIN = (0, 0)
    INTERIOR_ORIGIN = (INTERIOR_OFFSET, INTERIOR_OFFSET)

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.top_left = self.ORIGIN
        self.top_right = (width, 0)
        self.bottom_left = (0, height)
        self.bottom_right = (width, height)

        self.gradient_width = None
        self.gradient_height = None
        self.gradient_center = None
        self.layer_width = None
        self.layer_height = None

    @classmethod
    def create_new(cls, width, height):
        dimensions = cls(width, height)
        dimensions.gen_gradient_dim()
        dimensions.gen_layer_dim()
        return dimensions

    def gen_gradient_dim(self):
        self.gradient_width = self.width - self.GRADIENT_OFFSET * 2
        self.gradient_height = self.height - self.GRADIENT_OFFSET * 2
        self.gradient_center = (self.gradient_width / 2, self.gradient_height / 2)

    def gen_layer_dim(self):
        self.layer_width = self.width - self.LAYER_OFFSET * 2
        self.layer_height = self.height - self.LAYER_OFFSET * 2

    def invert_point(self, point):
        x, y = point
        return self.width - x, self.height - y


class Gradient:
    """
    Constructs a single gradient from a start and end point using primary and 
    secondary color.
    """

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
    """
    Represents a single frame of the camera border. It applies the 
    gradient object to a PIL image and trims it to our specified dimensions.
    """

    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.image = None
        self.drawing = None

    @classmethod
    def create_new(cls, dimensions):
        image = cls(dimensions)
        image.gen_pil_image()
        image.gen_drawing()
        return image

    def gen_pil_image(self):
        self.image = Image.new(
            "RGBA",
            (self.dimensions.width, self.dimensions.height),
            color=(0, 0, 0, 0),
        )

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
        if x > self.dimensions.width / 2:
            left_color = gradient.secondary_color
            right_color = gradient.primary_color
        else:
            left_color = gradient.primary_color
            right_color = gradient.secondary_color
        # left
        self.drawing.polygon(
            [
                self.dimensions.top_left,
                (self.dimensions.GRADIENT_OFFSET, 0),
                (self.dimensions.GRADIENT_OFFSET, self.dimensions.height),
                self.dimensions.bottom_left,
            ],
            fill=left_color,
        )
        # right
        self.drawing.polygon(
            [
                self.dimensions.top_right,
                (self.dimensions.gradient_width + self.dimensions.GRADIENT_OFFSET, 0),
                (
                    self.dimensions.gradient_width + self.dimensions.GRADIENT_OFFSET,
                    self.dimensions.height,
                ),
                self.dimensions.bottom_right,
            ],
            fill=right_color,
        )

    def fill_horizontal_rectangles(self, gradient):
        _, y = gradient.start
        if y < self.dimensions.height / 2:
            top_color = gradient.primary_color
            bottom_color = gradient.secondary_color
        else:
            top_color = gradient.secondary_color
            bottom_color = gradient.primary_color
        # top
        self.drawing.polygon(
            [
                self.dimensions.top_right,
                self.dimensions.top_left,
                (0, self.dimensions.GRADIENT_OFFSET),
                (self.dimensions.width, self.dimensions.GRADIENT_OFFSET),
            ],
            fill=top_color,
        )
        # bottom
        self.drawing.polygon(
            [
                self.dimensions.bottom_right,
                self.dimensions.bottom_left,
                (
                    0,
                    self.dimensions.gradient_height + self.dimensions.GRADIENT_OFFSET,
                ),
                (
                    self.dimensions.width,
                    self.dimensions.gradient_height + self.dimensions.GRADIENT_OFFSET,
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
                    if x < self.dimensions.gradient_width / 2
                    else self.dimensions.gradient_width - i
                )
                coordinates = [
                    (x_coord + self.dimensions.GRADIENT_OFFSET, 0),
                    (x_coord + self.dimensions.GRADIENT_OFFSET, self.dimensions.height),
                ]
            else:
                y_coord = (
                    0 + i
                    if y < self.dimensions.gradient_height / 2
                    else self.dimensions.gradient_height - i
                )
                coordinates = [
                    (0, y_coord + self.dimensions.GRADIENT_OFFSET),
                    (self.dimensions.width, y_coord + self.dimensions.GRADIENT_OFFSET),
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
                m, start, i, gradient.interval_dim, original_quadrant
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
        oppo_corner = self.dimensions.invert_point(corner)
        oppo_first_intercept = self.dimensions.invert_point(first_intercept)
        oppo_second_intercept = self.dimensions.invert_point(second_intercept)
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
            (
                self.dimensions.gradient_width - self.dimensions.INTERVAL,
                self.dimensions.gradient_height - self.dimensions.INTERVAL,
            ),
            color=(0, 0, 0, 0),
        )
        self.image.paste(interior, box=self.dimensions.INTERIOR_ORIGIN)

    def trim_edges(self):
        horizontal_edges = Image.new(
            "RGBA",
            (self.dimensions.width, self.dimensions.LAYER_OFFSET),
            color=(0, 0, 0, 0),
        )
        self.image.paste(horizontal_edges)
        self.image.paste(
            horizontal_edges,
            box=(0, self.dimensions.LAYER_OFFSET + self.dimensions.layer_height),
        )
        vertical_edges = Image.new(
            "RGBA",
            (self.dimensions.LAYER_OFFSET, self.dimensions.height),
            color=(0, 0, 0, 0),
        )
        self.image.paste(vertical_edges)
        self.image.paste(
            vertical_edges,
            box=(self.dimensions.LAYER_OFFSET + self.dimensions.layer_width, 0),
        )

    def blur(self, radius):
        self.image = self.image.filter(ImageFilter.GaussianBlur(radius))

    def get_intercepts(self, m, point, quadrant):
        x, y = point
        x2 = 0 if quadrant == constants.QuadrantEnum.FIRST else self.dimensions.width
        first_intercept = x2, m * (x2 - x) + y
        second_intercept = x + (-1 * y / m), 0
        return first_intercept, second_intercept

    def get_quadrant(self, point):
        x, y = point
        if x < self.dimensions.width / 2:
            return (
                constants.QuadrantEnum.FIRST
                if y < self.dimensions.height / 2
                else constants.QuadrantEnum.THIRD
            )
        else:
            return (
                constants.QuadrantEnum.SECOND
                if y < self.dimensions.height / 2
                else constants.QuadrantEnum.FOURTH
            )

    def get_corner_from_quadrant(self, quadrant):
        return {
            constants.QuadrantEnum.FIRST: self.dimensions.top_left,
            constants.QuadrantEnum.SECOND: self.dimensions.top_right,
            constants.QuadrantEnum.THIRD: self.dimensions.bottom_left,
            constants.QuadrantEnum.FOURTH: self.dimensions.bottom_right,
        }[quadrant]

    @staticmethod
    def get_next_gradient_coords(m, start, interval, interval_dim, original_quadrant):
        x1, y1 = start
        if interval_dim == constants.IntervalEnum.HORIZONTAL:
            x2 = (
                x1 + interval
                if original_quadrant == constants.QuadrantEnum.FIRST
                else x1 - interval
            )
            return x2, abs(m * (x2 - x1) + y1)
        else:
            y2 = y1 + interval
            return abs((y2 - y1) / m + x1), y2

    @staticmethod
    def add_gradient_offset(point):
        x, y = point
        return x + Dimensions.GRADIENT_OFFSET, y + Dimensions.GRADIENT_OFFSET

    @staticmethod
    def add_layer_offset(point):
        x, y = point
        return x + Dimensions.LAYER_OFFSET, y + Dimensions.LAYER_OFFSET


class CameraBorder:
    """
    Brings all the other classes together to construct a sequence of images that 
    construct the gradient around all points on the rectangular coordinates.
    """

    DEGREES = 6

    def __init__(self, dimensions, primary_color, secondary_color):
        self.dimensions = dimensions
        self.primary_color = primary_color
        self.secondary_color = secondary_color

        self.coordinates = None
        self.layers = None

    @classmethod
    def create_new(
        cls,
        aspect_ratio=None,
        primary_color=None,
        secondary_color=None,
        output_dir=None,
    ):
        width, height = constants.ASPECT_RATIO_TO_DIMENSIONS[aspect_ratio]
        dimensions = Dimensions.create_new(width, height)
        primary_color = cls.enforce_rgb(primary_color)
        secondary_color = cls.enforce_rgb(secondary_color)
        camera_border = cls(dimensions, primary_color, secondary_color)
        camera_border.gen_coordinates()
        camera_border.gen_layers()
        camera_border.save(output_dir)

    def gen_coordinates(self):
        self.coordinates = Coordinates.create_new(
            dimensions=self.dimensions,
            degrees=self.DEGREES,
        )

    def gen_layers(self):
        primary_to_secondary = []
        secondary_to_primary = []
        for coord in self.coordinates.coords:
            start, end = coord
            # create first layer
            first_layer = Layer.create_new(self.dimensions)
            first_gradient = Gradient.create_new(
                start, end, self.primary_color, self.secondary_color
            )
            # apply, trim, append first layer
            first_layer.apply_gradient(first_gradient)
            first_layer.trim()
            primary_to_secondary.append(first_layer.image)
            # create second layer
            second_layer = Layer.create_new(self.dimensions)
            second_gradient = Gradient.create_new(
                start, end, self.secondary_color, self.primary_color
            )
            # apply, trim, append second layer
            second_layer.apply_gradient(second_gradient)
            second_layer.trim()
            secondary_to_primary.append(second_layer.image)
        self.layers = []
        self.layers.extend(primary_to_secondary)
        self.layers.extend(secondary_to_primary)

    def save(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for i, layer in enumerate(self.layers):
            if i < 10:
                i = f"0{i}"
            layer.save(f"{output_dir}/{i}.png")

    @staticmethod
    def enforce_rgb(color):
        if isinstance(color, str):
            color = color[1:]
            color = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        return color

    @staticmethod
    def process_color_args(primary_color=None, secondary_color=None, profile=None):
        if not primary_color or not secondary_color:
            return constants.PROFILE_TO_PALETTE[profile]
        try:
            first_color = constants.COLOR_STR_TO_COLOR[primary_color]
        except KeyError:
            first_color = primary_color
        try:
            second_color = constants.COLOR_STR_TO_COLOR[secondary_color]
        except KeyError:
            second_color = secondary_color
        return first_color, second_color

    @staticmethod
    def process_aspect_ratio(aspect_ratio):
        return constants.ASPECT_STR_TO_ENUM[aspect_ratio]
