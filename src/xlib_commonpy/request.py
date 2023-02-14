from http.client import HTTPResponse
from os import PathLike
from pathlib import Path
from shutil import copyfileobj
from typing import Optional
from urllib import request
from uuid import uuid4


def _try_retrieving_filename_for_(
    file_download_response: HTTPResponse,
) -> Optional[str]:
    """Response header information is implemented via email.message.Message according to
    https://docs.python.org/3/library/http.client.html#httpmessage-objects.
    https://docs.python.org/3/library/email.compat32-message.html indicates that the
    filename can be found in the Content-Disposition header. Unfortunately servers do
    not always include this header. That's why this function may return None sometimes.
    """
    return file_download_response.info().get_filename()


def download_file_from_(url: str, dest_dir: PathLike[str]) -> Path:
    dpath_dest = Path(dest_dir)
    if not dpath_dest.exists():
        raise FileNotFoundError(dpath_dest)
    if dpath_dest.is_file():
        raise NotADirectoryError(dpath_dest)
    # Technique taken from https://docs.python.org/3/howto/urllib2.html#fetching-urls
    with request.urlopen(url) as response:
        filename = (  # When the server doesn't give a file name, just give it one
            _try_retrieving_filename_for_(file_download_response=response)
            or f"{uuid4()}.download"
        )
        fpath_dest = dpath_dest.joinpath(filename)
        with open(fpath_dest, "x") as fin:  # Use "x" to raise exception if file exists
            copyfileobj(response, fin)
    return fpath_dest
