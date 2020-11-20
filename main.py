import argparse
import os

from cam_border import CameraBorder
import constants


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=str,
        default=os.environ["CAMERA_BORDER_DIR"],
    )
    parser.add_argument("--primary_color", type=str, default=None)
    parser.add_argument("--secondary_color", type=str, default=None)
    parser.add_argument("--profile", type=str, default="cm")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    primary_color, secondary_color = constants.process_color_args(
        primary_color=args.primary_color,
        secondary_color=args.secondary_color,
        profile=args.profile,
    )
    camera_border = CameraBorder.create_new(
        constants.AspectRatioEnum.SIXTEEN_BY_NINE,
        primary_color=primary_color,
        secondary_color=secondary_color,
        output_dir=args.output_dir,
    )