#!/usr/bin/env python3

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
    parser.add_argument(
        "--aspect_ratio",
        type=str,
        default="16:9",
    )
    parser.add_argument("--primary_color", type=str, default=None)
    parser.add_argument("--secondary_color", type=str, default=None)
    parser.add_argument("--profile", type=str, default="cm")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    primary_color, secondary_color = CameraBorder.process_color_args(
        primary_color=args.primary_color,
        secondary_color=args.secondary_color,
        profile=args.profile,
    )
    aspect_ratio = CameraBorder.process_aspect_ratio(args.aspect_ratio)
    camera_border = CameraBorder.create_new(
        aspect_ratio=aspect_ratio,
        primary_color=primary_color,
        secondary_color=secondary_color,
        output_dir=args.output_dir,
    )