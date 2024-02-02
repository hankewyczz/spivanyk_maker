import os
from pathlib import Path

from consts import Config
from utils import Utils


"""
A representation of a song saved locally in the SONG_DIR, on disk.
"""
class LocalSong:
    SONG_DIR: str = os.path.normpath(os.path.join(Config.ROOT_DIR, 'assets/songs'))

    def __init__(self, filepath):
        self.filepath = filepath

    @classmethod
    def _standardize_filename(cls, song_title: str) -> str:
        """ Given a song title, creates a standardized filename """
        return f"{Utils.snake_case(song_title)}.cho"

    @classmethod
    def standardize_filepath(cls, song_title):
        return os.path.join(LocalSong.SONG_DIR, LocalSong._standardize_filename(song_title))
    
    @classmethod
    def exists(cls, song_title):
        filepath = LocalSong.standardize_filepath(song_title)
        return Path(filepath).exists()