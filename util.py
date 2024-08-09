import requests
from pathlib import Path


def download(url: str, path: str|Path) -> None:
    """Download a URL's content to a file."""
    response = requests.get(url)
    with str_to_path(path).open('wb') as file:
        file.write(response.content)


def downloaded(path: str|Path, url: str) -> Path:
    """Return a file's path, downloading it from a url if it doesn't exist."""
    path = str_to_path(path)
    if not path.exists():
        download(url, str_to_path(path))
        assert path.exists()
    return path


def str_to_path(str_path: str|Path) -> Path:
    """Convert a string path to a Path."""
    if isinstance(str_path, str):
        return Path(str_path)
    elif isinstance(str_path, Path):
        return str_path
    else:
        raise TypeError(f"Invalid type: {type(str_path)}")
