from pathlib import Path
from shutil import rmtree
from sys import executable
from typing import Any, List
from unittest import TestCase, mock
from uuid import UUID

from src.xlib_commonpy import tmpworkingdir
from src.xlib_commonpy.tmpworkingdir import TMPWorkingDir


class TestTMPWorkingDir(TestCase):
    _UNITTEST_TMP_DIR = (
        Path().absolute().joinpath("_tmp_unittest_" + TMPWorkingDir.__name__)
    )

    @staticmethod
    def _contents_of_(dir: Path) -> List[Path]:
        return list(dir.iterdir())

    def setUp(self) -> None:
        # Because these unit tests may potentially create create lots of directories,
        # I'll nest them within this directory
        self._UNITTEST_TMP_DIR.mkdir(parents=True, exist_ok=True)
        return super().setUp()

    def tearDown(self) -> None:
        try:
            rmtree(str(self._UNITTEST_TMP_DIR))
        except FileNotFoundError:
            pass
        return super().tearDown()

    def test_default_init_behavior(self):
        uut = TMPWorkingDir()

        # Default initialization shall target the directory of which the main executable
        # is in (i.e. Path's default location)
        self.assertEqual(uut.dirpath.parent, Path().absolute())

        # It shouldn't create the directory yet
        self.assertFalse(uut.dirpath.exists())

        # It shall not create anything extra in the parent directory
        self.assertEqual(len(self._contents_of_(dir=self._UNITTEST_TMP_DIR)), 0)

    def test_dirpath_name(self):
        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR).dirpath.name
        uut_parts = uut.split("_")

        # The dirname shall start with this to make it stand out and to indicate it's
        # supposed to be temporary when inspecting the contents of the parent directory
        self.assertTrue(uut.startswith("_tmp"))

        # The dirname shall include the executable's name so that inspection of the
        # UUT's parent directory will better-suggest it's tied to this program
        self.assertEqual(uut_parts[2], Path(executable).stem)

        # To prevent collisions, the last part of the dirname shall be a UUID v1 (v1
        # because it's tied to the host system, and since the host system manages its
        # file system, it's an appropriate version to use)
        self.assertIsNotNone(UUID(uut_parts[-1], version=1))

    def test_context_syntax(self):
        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR)

        # With/as syntax is supported
        with uut as uut_context:
            self.assertTrue(uut_context.dirpath.exists())
            self.assertTrue(uut_context.dirpath.is_dir())
        self.assertFalse(uut.dirpath.exists())

    def test_context_after_init(self):
        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR)

        # Dir shall not exist yet
        self.assertFalse(uut.dirpath.exists())

        # Context shall create the target folder
        with uut:
            self.assertTrue(uut.dirpath.exists())

            # Target folder shall be empty
            self.assertEqual(len(self._contents_of_(dir=uut.dirpath)), 0)
        # Dir shall be cleaned after a context closes
        self.assertFalse(uut.dirpath.exists())

    def test_dir_already_exists(self):
        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR)

        # Ask the UUT to create the dir
        target_dir = uut.create_workingdir()
        self.assertTrue(target_dir.exists())

        # Created dir shall be a directory and be empty
        self.assertTrue(uut.dirpath.is_dir())
        self.assertEqual(len(self._contents_of_(dir=uut.dirpath)), 0)

        # There should only be the UUT's directory in the parent directory at this point
        self.assertListEqual(
            self._contents_of_(dir=self._UNITTEST_TMP_DIR), [uut.dirpath]
        )

        # Using context after init shall simply reuse the dir
        with uut as uut_context:
            self.assertTrue(uut_context.dirpath.exists())
            self.assertEqual(len(self._contents_of_(dir=uut_context.dirpath)), 0)
            self.assertEqual(len(self._contents_of_(dir=uut.dirpath)), 0)
            self.assertListEqual(
                self._contents_of_(dir=self._UNITTEST_TMP_DIR), [uut.dirpath]
            )
        # It should still be cleaned up after contexts end
        self.assertFalse(uut.dirpath.exists())
        self.assertListEqual(self._contents_of_(dir=self._UNITTEST_TMP_DIR), [])

    def test_directory_does_not_auto_create(self):
        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR)
        self.assertFalse(uut.dirpath.exists())

    def test_same_obj_consecutive_contexts(self):
        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR)
        tmp_fname = "tmp.txt"
        tmp_fname2 = "tmp2.txt"
        tmp_fname3 = "tmp3.txt"

        # Using the "as"
        with uut as uut_context, open(
            str(uut_context.dirpath.joinpath(tmp_fname)), "w+"
        ) as fout:
            fout.write("hi")
            self.assertTrue(Path(uut_context.dirpath.joinpath(tmp_fname)).exists())
        self.assertFalse(Path(uut_context.dirpath.joinpath(tmp_fname)).exists())

        # Using the original object
        with uut as uut_context, open(
            str(uut.dirpath.joinpath(tmp_fname2)), "w+"
        ) as fout:
            fout.write("hullo")
            self.assertTrue(Path(uut_context.dirpath.joinpath(tmp_fname2)).exists())
        self.assertFalse(Path(uut_context.dirpath.joinpath(tmp_fname2)).exists())

        # No "as"
        with uut, open(str(uut.dirpath.joinpath(tmp_fname3)), "w+") as fout:
            fout.write("sup")
            self.assertTrue(Path(uut_context.dirpath.joinpath(tmp_fname3)).exists())
        self.assertFalse(Path(uut_context.dirpath.joinpath(tmp_fname3)).exists())

    def test_creating_file(self):
        tmp_fname = "tmp.txt"

        # Test combining contexts
        with TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR) as uut, open(
            str(uut.dirpath.joinpath(tmp_fname)), "w+"
        ) as tmp_fout:
            tmp_fout.write("this should get deleted after context dies")
        self.assertFalse(uut.dirpath.joinpath(tmp_fname).exists())

        # Test nested contexts
        test_file_contents = "test text file. if you see this, delete it."
        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR)
        with uut as uut_context:
            test_tmp_file = uut_context.dirpath.joinpath(tmp_fname)
            with open(str(test_tmp_file), "w+") as tmp_fout:
                tmp_fout.write(test_file_contents)
            with open(str(test_tmp_file), "r") as tmp_fin:
                self.assertEqual(tmp_fin.read(), test_file_contents)
        with self.assertRaises(FileNotFoundError):
            with open(str(uut.dirpath.joinpath(tmp_fname)), "r") as tmp_fin:
                self.assertEqual(tmp_fin.read(), test_file_contents)

    def test_delete_dir_twice(self):
        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR)
        with uut as uut_context:
            # Delete while inside context
            uut_context.delete_workingdir()

            # It should be gone
            self.assertFalse(uut.dirpath.exists())
        # End of context shouldn't raise a FileNotFoundError and should still be gone
        self.assertFalse(uut.dirpath.exists())

        # Try deleting again once it's empty
        uut.delete_workingdir()

        # No exceptions shall be raised, and it should still be gone
        self.assertFalse(uut.dirpath.exists())

    def test_delete_after_init(self):
        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR)
        self.assertFalse(uut.dirpath.exists())

        # No exceptions shall be raised even if it doesn't even exist yet
        uut.delete_workingdir()
        self.assertFalse(uut.dirpath.exists())

    @mock.patch.object(tmpworkingdir, tmpworkingdir.rmtree.__name__)
    def test_arg_for_rmtree_is_str(self, mock_rmtree: mock.MagicMock):
        """This test is necessary for backwards support for Python 3.5.2. Passing
        pathlib.Path object to builtins.open and similar stuff doesn't work."""

        def rm_tree_replacement(x: Any):
            self.assertTrue(isinstance(x, str))

        mock_rmtree.side_effect = rm_tree_replacement

        uut = TMPWorkingDir(dirpath_parent=self._UNITTEST_TMP_DIR)
        uut.delete_workingdir()
