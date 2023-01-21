from setuptools import setup

setup(
    name="SERPENT",
    packages=[],
    entry_points={
        "console_scripts": [
            "serpent = src.CLI:main",
            # Windows only
            "gui_serpent = src.GUI:main",
        ]
    },
    version=open("src/version.txt", "r").readline()
)