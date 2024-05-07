import os
from cx_Freeze import setup, Executable


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "sqlalchemy", "sqlalchemy.dialects.sqlite"],
    "optimize": 1,
    "excludes": [],
    "include_files": [
        (os.path.join(os.getcwd(), "src/jobs"), "jobs/"),
        (os.path.join(os.getcwd(), "src/candidates"), "candidates/"),
        (os.path.join(os.getcwd(), "src/db"), "db/"),
        (os.path.join(os.getcwd(), "src/app/static"), "app/static/"),
    ]
}

# Base set to "Win32GUI" if you're building a GUI application and you want to hide the console.
base = "Win32GUI"

icon_path = os.path.join(os.getcwd(), "src\\app\\static", "ai.png")

setup(
    name="StriveBot",
    version="0.1",
    description="StriveBot",
    long_description="A bot for automating job applications on Striive.",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon=icon_path, target_name="StriveBot")]
)
