import re
import os

import requests
from consts import Config
from song.wikispiv import WikiSpivSong
from song.local_song import LocalSong


class Song:
    SONG_DIR: str = os.path.normpath(os.path.join(Config.ROOT_DIR, 'assets/songs'))

    def __init__(self, song_title: str):
        self.title = song_title

        # This takes precedence over anything. The song might not exist in WikiSpiv, it might be named differently;
        #   doesn't matter. Local store is main source.
        if LocalSong.exists(song_title):
            self.filepath = LocalSong.standardize_filepath(song_title)
        else:
            # Maybe Centore used a different naming; check what other alt. titles exist, and check if there's a file
            #   for the "main" title
            standardized_title = WikiSpivSong.standardize_song_name(song_title)
            if LocalSong.exists(standardized_title):
                self.filepath = LocalSong.standardize_filepath(standardized_title)
            else:
                print(f"Couldn't find {song_title} locally; checking WikiSpiv")
                ws = WikiSpivSong(song_title)
                ws.download_song()
                self.filepath = ws.filepath
            
        self.alt_titles = []
        self.meta = []
        self.lyrics = []
        self.categories = []

        self.get_info_from_file()
    
    def get_info_from_file(self):
        """ Grabs information from the file about titles, meta-content, and lyrics.
        Overrides the title - the file is always the source of truth, not wikispiv """
        
        with open(self.filepath, encoding="utf-8") as f:
            for line in f:
                if Config.RE_COMMENT.match(line):
                    pass

                elif Config.RE_TITLE.match(line):
                    self.meta.append(line)
                    # THe file takes precedence
                    self.title = Config.RE_TITLE.match(line).group('args')

                elif Config.RE_ALT_TITLE.match(line):
                    self.meta.append(line)
                    alt_title = Config.RE_ALT_TITLE.match(line).group('args')
                    self.alt_titles.append(alt_title)

                elif Config.RE_SUBTITLE.match(line):
                    self.meta.append(line)

                elif Config.RE_CATEGORY.match(line):
                    category = Config.RE_CATEGORY.match(line).group('args')
                    if category in Config.INDEX_CATEGORIES:
                        self.categories.append(category)

                # Check if it's an unsupported command (ie. one I didn't implement because I don't use it)
                elif Config.RE_META.match(line):
                    print(f"Matched an unsupported command, skipping: {line}")
                # A normal line
                else:
                    self.lyrics.append(line)

        # Lyrics _almost_ always have a dummy line up top
        if self.lyrics[0].strip() == '':
            self.lyrics = self.lyrics[1:]

    

    def get_chords(self):
        with open(self.filepath, encoding='utf-8') as f:
            return set([x.group(1) for x in re.finditer(Config.RE_CHORD, f.read())])


        
