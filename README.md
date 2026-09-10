# RealSenseD405

Standalone Intel RealSense D405 RGB-D acquisition package. It owns the
librealsense pipeline and exposes immutable, depth-to-color-aligned sensor
frames without depending on a pose-estimation or tracking application.

The default stream configuration preserves the verified setup:

- RGB8 color at 848 x 480, 30 FPS
- Z16 depth at 848 x 480, 30 FPS
- depth aligned to color
- raw depth and float32 depth in meters
- aligned intrinsic matrix, depth scale, and frame timestamps
- single-slot latest-frame acquisition

## Install

From a Python environment that can access the D405:

```bash
cd /home/kkb/Workspace/MULTI_OBJECT_TRACKING
python3 -m pip install -e ../RealSenseD405
```

Install the optional OpenCV tools with `-e ../RealSenseD405[tools]` when
OpenCV is not already available.

On Linux, the device-specific udev rule can be installed once with:

```bash
./scripts/install_realsense_udev_rules.sh
```

This is a host configuration operation and may prompt for `sudo`; it is not
performed by Python package installation.

## Tools

The tools can be inspected without opening a camera:

```bash
python3 -m realsense_d405.tools.inspect_camera --help
python3 -m realsense_d405.tools.capture_rgbd --help
python3 -m realsense_d405.tools.record_rgbd --help
```

They open the D405 only after command-line parsing. Their default output is
written beneath the current directory's `recordings/` folder unless an
explicit `--output-dir` is supplied.

This package intentionally contains no FoundationPose, segmentation,
tracking, task-symmetry, pipe-model, T-LESS, or application visualization
code.
