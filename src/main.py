#!/usr/bin/env python3
import json
from pyuca import Collator
from song.song import *
from render import render_pdf


def load_content_and_config(config_file: str):
    """ Using the given JSON config file, update our configs and return the songs list """
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
    content = load_content_and_config(config_file)

    sections = []
    
    for section_name, songs, should_sort in content:
        print(f'** Processing section {section_name}')
        songs = [Song(song.strip()) for song in songs]
        songs = [s for s in songs if s is not None]

        # Укр. sorting doesn't work as expected if using default sort funcs
        #   In particular - Ї & є are out of order by unicode key
        if should_sort:
            songs.sort(key=lambda s: Collator().sort_key(s.title))

        sections.append((section_name, songs, should_sort))

    print("Rendering...")
    render_pdf(sections, os.path.join(Config.ROOT_DIR, outfile))


main("../configs/lsh-spivanyk.json", 'output/2024-01-lsh.pdf')
