from setuptools import setup

setup(
    name="SERPENT",
    packages=[],
    entry_points={
        "console_scripts": [
            "SERPENT = src._00_CLI:main",
            # Windows only
            "GUI_SERPENT = src._00_GUI:main",
        ]
    },
    version=open("src/version.txt", "r").readline()
)