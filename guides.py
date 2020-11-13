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


def display_gradient_guidelines(drawing):
    for x1, x2 in constants.X_GRADIENT_COORDS:
        drawing.line(
            [
                (x1 + constants.GRADIENT_OFFSET, constants.GRADIENT_OFFSET),
                (
                    x2 + constants.GRADIENT_OFFSET,
                    constants.GRADIENT_HEIGHT + constants.GRADIENT_OFFSET,
                ),
            ],
            fill=constants.Colors.WHITE,
            width=1,
        )
    for y1, y2 in constants.Y_GRADIENT_COORDS:
        drawing.line(
            [
                (constants.GRADIENT_OFFSET, y1 + constants.GRADIENT_OFFSET),
                (
                    constants.GRADIENT_WIDTH + constants.GRADIENT_OFFSET,
                    y2 + constants.GRADIENT_OFFSET,
                ),
            ],
            fill=constants.Colors.WHITE,
            width=1,
        )


def display_layer_boundary(drawing):
    drawing.line(
        [
            add_layer_offset(constants.ORIGIN),
            add_layer_offset((constants.LAYER_WIDTH, 0)),
        ],
        fill=constants.Colors.WHITE,
        width=1,
    )
    drawing.line(
        [add_layer_offset((0, 0)), add_layer_offset((0, constants.LAYER_HEIGHT))],
        fill=constants.Colors.WHITE,
        width=1,
    )
    drawing.line(
        [
            add_layer_offset((constants.LAYER_WIDTH, 0)),
            add_layer_offset((constants.LAYER_WIDTH, constants.LAYER_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=1,
    )
    drawing.line(
        [
            add_layer_offset((0, constants.LAYER_HEIGHT)),
            add_layer_offset((constants.LAYER_WIDTH, constants.LAYER_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=1,
    )


def display_gradient_boundary(drawing):
    drawing.line(
        [
            add_gradient_offset(constants.ORIGIN),
            add_gradient_offset((constants.GRADIENT_WIDTH, 0)),
        ],
        fill=constants.Colors.WHITE,
        width=1,
    )
    drawing.line(
        [
            add_gradient_offset(constants.ORIGIN),
            add_gradient_offset((0, constants.GRADIENT_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=1,
    )
    drawing.line(
        [
            add_gradient_offset((constants.GRADIENT_WIDTH, 0)),
            add_gradient_offset((constants.GRADIENT_WIDTH, constants.GRADIENT_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=1,
    )
    drawing.line(
        [
            add_gradient_offset((0, constants.GRADIENT_HEIGHT)),
            add_gradient_offset((constants.GRADIENT_WIDTH, constants.GRADIENT_HEIGHT)),
        ],
        fill=constants.Colors.WHITE,
        width=1,
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
        width=1,
    )
    drawing.line(
        [
            add_layer_and_gradient_offset(constants.ORIGIN),
            add_layer_and_gradient_offset(
                (0, constants.GRADIENT_HEIGHT - constants.GRADIENT_LAYER_OFFSET * 2)
            ),
        ],
        fill=constants.Colors.WHITE,
        width=1,
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
        width=1,
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
        width=1,
    )