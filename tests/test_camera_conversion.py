"""CPU-only tests for SDK-frame to D405Frame conversion."""

import numpy as np

from realsense_d405 import D405Camera, D405Config


class FakeIntrinsics:
    fx = 400.0
    fy = 410.0
    ppx = 424.0
    ppy = 240.0


class FakeVideoProfile:
    def get_intrinsics(self) -> FakeIntrinsics:
        return FakeIntrinsics()


class FakeDepthProfile:
    def as_video_stream_profile(self) -> FakeVideoProfile:
        return FakeVideoProfile()


class FakeDepthFrame:
    profile = FakeDepthProfile()

    def __init__(self, data: np.ndarray) -> None:
        self._data = data

    def get_data(self) -> np.ndarray:
        return self._data


class FakeColorFrame:
    def __init__(self, data: np.ndarray) -> None:
        self._data = data

    def get_data(self) -> np.ndarray:
        return self._data

    def get_frame_number(self) -> int:
        return 42

    def get_timestamp(self) -> float:
        return 123.5

    def get_frame_timestamp_domain(self) -> str:
        return "hardware_clock"


class FakeAlignedFrames:
    def __init__(self, rgb: np.ndarray, depth_raw: np.ndarray) -> None:
        self._color = FakeColorFrame(rgb)
        self._depth = FakeDepthFrame(depth_raw)

    def get_color_frame(self) -> FakeColorFrame:
        return self._color

    def get_depth_frame(self) -> FakeDepthFrame:
        return self._depth


def test_default_stream_configuration_is_verified_profile() -> None:
    assert D405Config() == D405Config(width=848, height=480, fps=30, serial=None)


def test_sdk_frame_conversion_preserves_depth_and_metadata() -> None:
    rgb = np.zeros((2, 3, 3), dtype=np.uint8)
    depth_raw = np.array([[0, 1, 1000], [2000, 65535, 42]], dtype=np.uint16)
    camera = D405Camera(D405Config())

    frame = camera._make_frame(
        FakeAlignedFrames(rgb, depth_raw),
        depth_scale=0.001,
        host_wall_time_s=200.0,
        host_monotonic_time_s=100.0,
    )

    assert frame is not None
    np.testing.assert_array_equal(frame.depth_raw, depth_raw)
    np.testing.assert_allclose(
        frame.depth_m,
        depth_raw.astype(np.float32) * np.float32(0.001),
    )
    np.testing.assert_allclose(
        frame.K,
        [[400.0, 0.0, 424.0], [0.0, 410.0, 240.0], [0.0, 0.0, 1.0]],
    )
    assert frame.source_frame_id == 42
    assert frame.device_timestamp_ms == 123.5
    assert frame.timestamp_domain == "hardware_clock"
    assert frame.host_wall_time_s == 200.0
    assert frame.host_monotonic_time_s == 100.0
