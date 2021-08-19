import os

from song import *
from pathlib import Path

SONG_DIR = os.path.normpath("../../songs")


def check_song(title: str):
    # Try to standardize the title
    title = songtitle_search(title)

    if not title:
        raise ValueError(f"Song with title {title} could not be found")

    # Next, we ensure we're using the main title of the song
    title = get_main_title(title)
    filepath = os.path.join(SONG_DIR, song_filename(title))

    wikispiv_song = Song(title)

    if Path(filepath).exists():
        # Compare it to the WikiSpiv version
        pass
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(wikispiv_song.to_chordpro())


check_song("коли у путь")
"""
If the song exists locally:
compare it to the WikiSpiv version


If it doesn't exist locally, save it








"""