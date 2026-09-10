"""Preview aligned D405 RGB-D and save snapshots with S."""

import argparse
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np

from realsense_d405 import D405Camera, D405Config, D405Frame


def _load_cv2() -> Any:
    try:
        import cv2
    except ImportError as error:
        raise ImportError(
            "OpenCV is required for capture preview; install RealSenseD405[tools]."
        ) from error
    return cv2


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "recordings" / "captures",
    )
    parser.add_argument("--width", type=int, default=848)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--serial")
    return parser.parse_args(argv)


def save_frame(root: Path, frame: D405Frame, depth_scale: float) -> None:
    cv2 = _load_cv2()
    (root / "rgb").mkdir(parents=True, exist_ok=True)
    (root / "depth").mkdir(parents=True, exist_ok=True)
    cv2.imwrite(
        str(root / "rgb" / f"{frame.source_frame_id:06d}.png"),
        cv2.cvtColor(frame.rgb, cv2.COLOR_RGB2BGR),
    )
    cv2.imwrite(
        str(root / "depth" / f"{frame.source_frame_id:06d}.png"),
        frame.depth_raw,
    )
    np.savetxt(root / "K.txt", frame.K, fmt="%.8f")
    (root / "depth_scale.txt").write_text(
        f"{depth_scale:.12g}\n",
        encoding="utf-8",
    )
    print(f"Saved frame {frame.source_frame_id} under {root}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    cv2 = _load_cv2()
    camera = D405Camera(D405Config(args.width, args.height, args.fps, args.serial))
    try:
        camera.start()
        while True:
            frame = camera.get_next_frame()
            color = cv2.cvtColor(frame.rgb, cv2.COLOR_RGB2BGR)
            depth_vis = cv2.applyColorMap(
                cv2.convertScaleAbs(frame.depth_m, alpha=100.0),
                cv2.COLORMAP_JET,
            )
            cv2.imshow("D405 RGB", color)
            cv2.imshow("D405 aligned depth", depth_vis)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("s"):
                depth_scale = camera.depth_scale
                if depth_scale is None:
                    raise RuntimeError("D405 depth scale is unavailable.")
                save_frame(args.output_dir, frame, depth_scale)
    finally:
        camera.stop()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
