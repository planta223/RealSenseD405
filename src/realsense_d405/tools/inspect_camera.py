"""Inspect one aligned D405 frame, intrinsics, and stream metadata."""

import argparse
from typing import Optional, Sequence

from realsense_d405 import D405Camera, D405Config


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=848)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--serial")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    camera = D405Camera(D405Config(args.width, args.height, args.fps, args.serial))
    try:
        camera.start()
        frame = camera.get_next_frame()
        print(f"Device: {camera.device_name} ({camera.device_serial})")
        print(f"Color: {camera.color_stream_info}")
        print(f"Depth: {camera.depth_stream_info}")
        print(f"Depth scale: {camera.depth_scale} m/unit")
        print(
            f"Frame: {frame.source_frame_id}, rgb={frame.rgb.shape}, "
            f"depth={frame.depth_raw.shape}"
        )
        print("K:")
        print(frame.K)
    finally:
        camera.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
