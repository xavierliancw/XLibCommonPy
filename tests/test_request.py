from io import BufferedReader
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.xlib_commonpy import request
from src.xlib_commonpy.request import download_file_from_

_PATCHARGS_URLOPEN = (request.request, request.request.urlopen.__name__)
from types import MethodType


class _MOCKHTTPMessage:
    def __init__(self, filename: Optional[str]) -> None:
        self._filename = filename

    def get_filename(self) -> Optional[str]:
        return self._filename


class TestRequest(TestCase):
    @patch.object(*_PATCHARGS_URLOPEN)
    def test_downloading_file(self, mock_urlopen: MagicMock):
        expected_data = str(uuid4())
        with TemporaryDirectory() as tmpdir:
            # Mock some data a server would transfer when downloading
            mock_download_data = Path(tmpdir).joinpath("pretend.download")
            with open(mock_download_data, "w+") as fout:
                fout.write(expected_data)
            # Mock a HTTPResponse object
            mock_httpresp = MagicMock()
            with open(mock_download_data, "r") as pretend_dl_stream:
                # Mock the HTTPMessage object within the response object
                pretend_dl_stream.info = MethodType(  # type:ignore
                    lambda x: _MOCKHTTPMessage(filename=mock_download_data.name),
                    BufferedReader,
                )
                mock_httpresp.__enter__.return_value = pretend_dl_stream  # type: ignore
                mock_urlopen.return_value = mock_httpresp

                dpath_expected_destination = Path(tmpdir).joinpath("downloads")

                # FileNotFoundError shall be raised if the destination directory doesn't
                # exist
                with self.assertRaises(FileNotFoundError):
                    uut = download_file_from_(
                        url="doesn't matter", dest_dir=dpath_expected_destination
                    )

                # NotADirectoryError shall be raised if the destination directory is
                # actually a file
                dpath_expected_destination.touch()
                with self.assertRaises(NotADirectoryError):
                    uut = download_file_from_(
                        url="doesn't matter", dest_dir=dpath_expected_destination
                    )
                dpath_expected_destination.unlink()
                dpath_expected_destination.mkdir(parents=True, exist_ok=True)

                # FileExistsError shall be raised if the file already exists
                dpath_expected_destination.joinpath(mock_download_data.name).touch()
                with self.assertRaises(FileExistsError):
                    uut = download_file_from_(
                        url="doesn't matter", dest_dir=dpath_expected_destination
                    )
                dpath_expected_destination.joinpath(mock_download_data.name).unlink()

                # Exercise UUT's happy path now
                uut = download_file_from_(
                    url="doesn't matter", dest_dir=dpath_expected_destination
                )

                # Return value shall be the file that is downloaded
                self.assertEqual(
                    uut, dpath_expected_destination.joinpath(mock_download_data.name)
                )
                # The downloaded file shall exist
                self.assertTrue(uut.exists())

                # The expected data shall be in that file
                with open(uut, "r") as fin:
                    self.assertEqual(fin.read(), expected_data)

                # UUT shall generate a name for a download that doesn't provide a file
                # name
                pretend_dl_stream.seek(0)
                pretend_dl_stream.info = MethodType(  # type:ignore
                    lambda x: _MOCKHTTPMessage(filename=None),
                    BufferedReader,
                )
                uut = download_file_from_(
                    url="doesn't matter", dest_dir=dpath_expected_destination
                )
                self.assertTrue(uut.name.endswith(".download"))
                self.assertTrue(uut.exists())
                with open(uut, "r") as fin:
                    self.assertEqual(fin.read(), expected_data)
