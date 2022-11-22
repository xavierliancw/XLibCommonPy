from pathlib import Path
from shutil import rmtree
from sys import executable
from typing import Any

# Operations here are tied to the file system, and uuid1 basically prevents collisions
# with respect to the host
from uuid import uuid1


class TMPWorkingDir:
    """Normal usage is just to initialize via with-as syntax, and then comma-separate
    another with-as context (using the directory path variable) for a temporary file to
    use. Once the context closes, all files in the directory are deleted.

    It's statistically guaranteed that created working directories are unique per
    instance. As such, you don't have to worry about other processes accidentally
    deleting your working directory."""

    @property
    def dirpath(self) -> Path:
        return self._DIRPATH_CURRENT

    def __init__(self, dirpath_parent: Path = Path().absolute()) -> None:
        """This does not create the working directory. You may use a with-statement to
        do that, or simply call the specific method.

        Arguments:
        dirpath_parent -- the parent directory for which the working directory to be
            managed will be created within (default directory is just a folder next to
            the Python script)
        """
        self._DIRPATH_CURRENT = dirpath_parent.absolute().joinpath(
            "_tmp_" + Path(executable).stem + "_" + str(uuid1())
        )

    def __enter__(self) -> "TMPWorkingDir":
        self.create_workingdir()
        return self

    def __exit__(self, *args: Any) -> None:
        self.delete_workingdir()

    def create_workingdir(self) -> Path:
        self._DIRPATH_CURRENT.absolute().mkdir(exist_ok=True, parents=True)
        return self._DIRPATH_CURRENT

    def delete_workingdir(self):
        try:
            rmtree(str(self._DIRPATH_CURRENT.resolve()))
        except FileNotFoundError:
            pass  # It's ok if it's not there; just means it's already been cleaned up


if __name__ == "__main__":
    pass
