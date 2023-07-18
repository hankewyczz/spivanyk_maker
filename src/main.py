#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Optional

from pyuca import Collator

from song import *
from render import render_pdf


def get_song(raw_title: str) -> Optional[Song]:
    """
    Try to get the song matching this title, first locally, then from WikiSpiv
    @param raw_title: The raw title for which we search
    @return: A Song object if the song could be located, None otherwise
    """
    filepath = os.path.join("../assets/songs", song_filename(raw_title))

    # Check if we have a local file matching this song title
    if not Path(filepath).exists():
        # Try to standardize the title
        title = songtitle_search(raw_title)

        # If WikiSpiv has no search results, use the raw name
        if not title:
            title = raw_title

        # Try finding the main title of the song
        title = get_main_title(title)

        song_obj = Song(title)
        filepath = os.path.join("../assets/songs", song_obj.filename)

        if not Path(filepath).exists():
            while True:
                msg = f'Song "{title}" does not exist. Try downloading from WikiSpiv? (y/n): '
                reply = str(input(msg)).lower().strip()
                if reply:
                    if reply[0] == 'y':
                        break
                    elif reply[0] == 'n':
                        return None

            # Open the file
            with open(filepath, 'w', encoding='utf-8') as f:
                try:
                    f.write(song_obj.to_chordpro())
                    print(f"Downloaded '{title}' from WikiSpiv")
                except ValueError as e:
                    print(f"Skipping song: {e}")
                    return None
    else:
        song_obj = Song(raw_title)

    return song_obj


def set_configs(config_file: str):
    """
    Using the given JSON config file, update our configs and return the songs list
    @param config_file: The filepath of the config file
    @return: A list of sections for the songbook
    """
    with open(config_file, encoding='utf-8') as f:
        conf_obj = json.load(f)


    sections = None
    for key, v in conf_obj.items():
        if key == 'sections':
            sections = v
        elif hasattr(Config, key):
            setattr(Config, key, Config.updateDict(getattr(Config, key), v))

    # Update some dependent variables
    Config.USABLE_PAGE_WIDTH = Config.PDF_WIDTH - (Config.PDF_MARGIN_RIGHT + Config.PDF_MARGIN_LEFT)
    Config.USABLE_PAGE_HEIGHT = Config.PDF_HEIGHT - (Config.PDF_MARGIN_BOTTOM + Config.PDF_MARGIN_TOP)
    Config.CHORD_HEIGHT = Config.CHORD_STRING_HEIGHT + 3  # The height of the strings + fretboard

    return sections


def main(config_file: str, outfile: str):
    sections = set_configs(config_file)

    sections_objs = []
    print("Fetching song files")
    for name, songs, sort_by_name in sections:
        print(f'** Parsing section {name}')
        song_lst = [get_song(song.strip()) for song in songs]
        song_lst: List[Song] = [x for x in song_lst if x]  # Filter None values

        if sort_by_name:
            song_lst.sort(key=lambda x: Collator().sort_key(x.main_title))
        sections_objs.append((name, song_lst, sort_by_name))

    print("Rendering PDF")
    render_pdf(sections_objs, os.path.join(Config.ROOT_DIR, outfile))


main("../configs/lsh-spivanyk.json", 'output/2023-07-lsh.pdf')
