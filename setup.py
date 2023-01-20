from setuptools import setup

setup(
    name="SERPENT",
    packages=[],
    entry_points={
        "console_scripts": [
            "SERPENT = src.CLI:main",
            # Windows only
            "GUI_SERPENT = src.GUI:main",
        ]
    },
    version=open("src/version.txt", "r").readline()
)