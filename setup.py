from setuptools import setup

setup(
    name="SERPENT",
    packages=[],
    entry_points={
        "console_scripts": [
            "serpent = snake.CLI:main",
            "gui_serpent = snake.GUI:main",
        ]
    },
    version=open("snake/version.txt", "r").readline()
)