from setuptools import setup

setup(
    packages=[],
    entry_points={
        "console_scripts": [
            "serpent = src._00_CLI:main",
            # Windows only
            "gui_serpent = src._00_GUI:main",
        ]
    }
)