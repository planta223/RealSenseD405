"""Record an aligned D405 RGB-D sequence without application logic."""

import argparse
import csv
from pathlib import Path
import time
from typing import Any, Optional, Sequence

import numpy as np

from realsense_d405 import D405Camera, D405Config


def _load_cv2() -> Any:
    try:
        import cv2
    except ImportError as error:
        raise ImportError(
            "OpenCV is required for RGB-D recording; install RealSenseD405[tools]."
        ) from error
    return cv2


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "recordings" / "sequence",
    )
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--width", type=int, default=848)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--serial")
    args = parser.parse_args(argv)
    if args.duration <= 0:
        parser.error("--duration must be positive")
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    cv2 = _load_cv2()
    rgb_dir = args.output_dir / "rgb"
    depth_dir = args.output_dir / "depth"
    rgb_dir.mkdir(parents=True, exist_ok=True)
    depth_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    camera = D405Camera(D405Config(args.width, args.height, args.fps, args.serial))
    try:
        camera.start()
        deadline = time.monotonic() + args.duration
        first_frame = None
        while time.monotonic() < deadline:
            frame = camera.get_next_frame()
            if first_frame is None:
                first_frame = frame
            name = f"{frame.source_frame_id:06d}.png"
            cv2.imwrite(
                str(rgb_dir / name),
                cv2.cvtColor(frame.rgb, cv2.COLOR_RGB2BGR),
            )
            cv2.imwrite(str(depth_dir / name), frame.depth_raw)
            rows.append(
                (
                    frame.source_frame_id,
                    name,
                    frame.device_timestamp_ms,
                    frame.host_wall_time_s,
                )
            )
    finally:
        camera.stop()

    if first_frame is None:
        raise RuntimeError("No D405 frames were recorded.")
    depth_scale = camera.depth_scale
    if depth_scale is None:
        raise RuntimeError("D405 depth scale is unavailable.")
    np.savetxt(args.output_dir / "K.txt", first_frame.K, fmt="%.8f")
    (args.output_dir / "depth_scale.txt").write_text(
        f"{depth_scale:.12g}\n",
        encoding="utf-8",
    )
    with (args.output_dir / "frames.csv").open(
        "w",
        newline="",
        encoding="utf-8",
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ("frame_id", "rgb_file", "device_timestamp_ms", "host_wall_time_s")
        )
        writer.writerows(rows)
    print(f"Recorded {len(rows)} frame(s) under {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
