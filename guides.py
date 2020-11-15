import math

import constants


def add_gradient_offset(point):
    return point[0] + constants.GRADIENT_OFFSET, point[1] + constants.GRADIENT_OFFSET


def add_layer_offset(point):
    return point[0] + constants.LAYER_OFFSET, point[1] + constants.LAYER_OFFSET


def add_layer_and_gradient_offset(point):
    point = add_gradient_offset(point)
    return (
        point[0] + constants.GRADIENT_LAYER_OFFSET,
        point[1] + constants.GRADIENT_LAYER_OFFSET,
    )


def display_layer_boundary(drawing):
    drawing.line(
        [
            add_layer_offset(constants.ORIGIN),
            add_layer_offset((constants.LAYER_WIDTH, 0)),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )
    drawing.line(
        [add_layer_offset((0, 0)), add_layer_offset((0, constants.LAYER_HEIGHT))],
        fill=constants.Colors.WHITE,
        width=5,
    )
    drawing.line(
        [
            add_layer_offset((constants.LAYER_WIDTH, 0)),
            add_layer_offset((constants.LAYER_WIDTH, constants.LAYER_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )
    drawing.line(
        [
            add_layer_offset((0, constants.LAYER_HEIGHT)),
            add_layer_offset((constants.LAYER_WIDTH, constants.LAYER_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )


def display_gradient_boundary(drawing):
    drawing.line(
        [
            add_gradient_offset(constants.ORIGIN),
            add_gradient_offset((constants.GRADIENT_WIDTH, 0)),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )
    drawing.line(
        [
            add_gradient_offset(constants.ORIGIN),
            add_gradient_offset((0, constants.GRADIENT_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )
    drawing.line(
        [
            add_gradient_offset((constants.GRADIENT_WIDTH, 0)),
            add_gradient_offset((constants.GRADIENT_WIDTH, constants.GRADIENT_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )
    drawing.line(
        [
            add_gradient_offset((0, constants.GRADIENT_HEIGHT)),
            add_gradient_offset((constants.GRADIENT_WIDTH, constants.GRADIENT_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )


def display_inner_boundary(drawing):
    drawing.line(
        [
            add_layer_and_gradient_offset(constants.ORIGIN),
            add_layer_and_gradient_offset(
                (constants.GRADIENT_WIDTH - constants.GRADIENT_LAYER_OFFSET * 2, 0)
            ),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )
    drawing.line(
        [
            add_layer_and_gradient_offset(constants.ORIGIN),
            add_layer_and_gradient_offset(
                (0, constants.GRADIENT_HEIGHT - constants.GRADIENT_LAYER_OFFSET * 2)
            ),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )
    drawing.line(
        [
            add_layer_and_gradient_offset(
                (constants.GRADIENT_WIDTH - constants.GRADIENT_LAYER_OFFSET * 2, 0)
            ),
            add_layer_and_gradient_offset(
                (
                    constants.GRADIENT_WIDTH - constants.GRADIENT_LAYER_OFFSET * 2,
                    constants.GRADIENT_HEIGHT - constants.GRADIENT_LAYER_OFFSET * 2,
                )
            ),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )
    drawing.line(
        [
            add_layer_and_gradient_offset(
                (0, constants.GRADIENT_HEIGHT - constants.GRADIENT_LAYER_OFFSET * 2)
            ),
            add_layer_and_gradient_offset(
                (
                    constants.GRADIENT_WIDTH - constants.GRADIENT_LAYER_OFFSET * 2,
                    constants.GRADIENT_HEIGHT - constants.GRADIENT_LAYER_OFFSET * 2,
                )
            ),
        ],
        fill=constants.Colors.WHITE,
        width=5,
    )


def display_circular_lines(drawing):
    x = 0
    y = constants.GRADIENT_HEIGHT / 2
    switch = False
    start = x, y
    coords = [start]
    curr_x, curr_y = x, y
    for d in range(0, 180, 3):
        rad = math.radians(d)
        r = math.sqrt(pow(1920, 2) + pow(1080, 2))
        dy = curr_y + r * math.sin(d)
        dx = curr_x + r * math.cos(d)
        drawing.line(
            [(dx + 320, dy + 320), (constants.GRADIENT_WIDTH / 2 + 320, constants.GRADIENT_HEIGHT / 2 + 320)],
            fill=constants.Colors.WHITE,
            width=5
        )
        curr_x, curr_y = dx, dy
