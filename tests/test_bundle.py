from pathlib import Path
from typing import Set
from unittest import TestCase
from unittest.mock import patch

from src.xlib_commonpy import bundle
from src.xlib_commonpy.bundle import Bundle
from src.xlib_commonpy.tmpworkingdir import TMPWorkingDir


class TestBundle(TestCase):
    def test_dirpath(self):
        # The parent folder is "tests" and not "src" because the correct behavior of
        # this is to have the bundle in the same directory of the entry point. When unit
        # tests are executing, the entry point is this script. When developers who are
        # using this library are debugging their code, it should be in their source
        # folder. The effect of this is such that developers don't have to put their
        # bundled stuff in the "site-packages" folder when they have this library
        # installed through pip.
        expected = Path().absolute().joinpath("tests").joinpath("dev_bundle")
        uut = Bundle.dirpath()

        # Developer bundle access
        self.assertEqual(uut, expected)

        # Production bundle access
        with patch.object(bundle, bundle.sys.__name__) as sys_mock:
            # See https://stackoverflow.com/a/65327808/8462094
            setattr(sys_mock, "frozen", True)
            setattr(sys_mock, "_MEIPASS", expected)
            uut = Bundle.dirpath()
            self.assertEqual(uut, expected)

    def test_listdir(self):
        with (
            TMPWorkingDir() as tmpdir,
            patch.object(Bundle, Bundle.dirpath.__name__) as mock_bundlepath,
            open(tmpdir.dirpath.joinpath("file1.txt"), "w+") as fout1,
        ):
            innerdir = tmpdir.dirpath.joinpath("innerdir")
            innerdir.mkdir(parents=True)
            expected: Set[Path] = set()
            expected.add(Path(fout1.name))
            expected.add(innerdir)
            mock_bundlepath.side_effect = lambda: tmpdir.dirpath

            self.assertSetEqual(set(Bundle.list_dir()), expected)
