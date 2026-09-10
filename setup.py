"""Compatibility shim for editable installs with older pip/setuptools."""

from setuptools import find_packages, setup


setup(
    name="realsense-d405",
    version="0.1.0",
    description="Standalone Intel RealSense D405 RGB-D acquisition package",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.8",
    install_requires=["numpy>=1.20", "pyrealsense2>=2.50"],
    extras_require={"tools": ["opencv-python>=4.5"], "test": ["pytest>=7"]},
    entry_points={
        "console_scripts": [
            "d405-capture=realsense_d405.tools.capture_rgbd:main",
            "d405-inspect=realsense_d405.tools.inspect_camera:main",
            "d405-record=realsense_d405.tools.record_rgbd:main",
        ]
    },
)
