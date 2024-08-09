import requests as _requests
from pathlib import Path as _Path


def download(url, path):
    response = _requests.get(url)
    if isinstance(path, str):
        file_path = _Path(path)
    with path.open('wb') as file:
        file.write(response.content)
