"""CPU-only frame and latest-buffer tests."""

import numpy as np
import pytest

from realsense_d405 import D405Frame, LatestFrameBuffer


def make_frame(frame_id: int, raw_value: int = 1000) -> D405Frame:
    rgb = np.zeros((2, 3, 3), dtype=np.uint8)
    depth_raw = np.full((2, 3), raw_value, dtype=np.uint16)
    depth_m = depth_raw.astype(np.float32) * np.float32(0.001)
    K = np.array(
        [[100.0, 0.0, 1.0], [0.0, 100.0, 0.5], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    return D405Frame(
        source_frame_id=frame_id,
        rgb=rgb,
        depth_raw=depth_raw,
        depth_m=depth_m,
        K=K,
        device_timestamp_ms=12.5,
        timestamp_domain="hardware_clock",
        host_wall_time_s=100.0,
        host_monotonic_time_s=50.0,
    )


def test_frame_owns_immutable_arrays() -> None:
    frame = make_frame(1)

    assert frame.rgb.flags.writeable is False
    assert frame.depth_raw.flags.writeable is False
    assert frame.depth_m.flags.writeable is False
    assert frame.K.flags.writeable is False
    assert frame.depth_m.dtype == np.float32
    assert frame.width == 3
    assert frame.height == 2


def test_latest_frame_buffer_discards_older_frames() -> None:
    buffer = LatestFrameBuffer()
    first = make_frame(1)
    latest = make_frame(2)

    buffer.publish(first)
    buffer.publish(latest)

    assert buffer.wait_for_newer(0, timeout_s=0.0) is latest
    assert buffer.wait_for_newer(2, timeout_s=0.0) is None
    with pytest.raises(ValueError, match="increase strictly"):
        buffer.publish(first)
