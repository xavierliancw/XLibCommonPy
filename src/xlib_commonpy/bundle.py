import sys
from pathlib import Path
from typing import List


class Bundle:
    """Manages access to this application's bundle directory.
    The bundle directory is where dependencies get bundled. For example, let's say you
    package your Python program into a binary, and your binary uses a shell script
    developed by someone else. You can stick that shell script into the bundle
    directory (of which you specify to be bundled when generating your binary). As such,
    your Python code can then use that shell script without worrying about where it's
    located on whatever machine you're running your binary/code on.

    LEGAL DISCLAIMER (I'm not a lawyer, so this is not official legal advice): Be wary
    when bundling stuff with your binaries. Copyright laws and such could land you in
    legal hot water."""

    @staticmethod
    def dirpath() -> Path:
        """Path to this application's bundle directory.
        Taken from https://stackoverflow.com/a/65327808/8462094"""
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            # Gets path to bundle when this program has been built
            return Path(sys._MEIPASS)  # type: ignore
        # Path to bundle when debugging
        return Path(__file__).parent.parent.joinpath("dev_bundle")

    @staticmethod
    def list_dir() -> List[Path]:
        if not Bundle.dirpath().exists():
            return []
        return list(Bundle.dirpath().iterdir())
