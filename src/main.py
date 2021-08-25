from typing import Optional, Tuple

from song import *
from pathlib import Path

from src.render.render import render_pdf


def get_song(raw_title: str) -> Optional[Song]:
    """
    Try to get the song matching this title, first locally, then from WikiSpiv
    @param raw_title: The raw title for which we search
    @return: A Song object if the song could be located, None otherwise
    """
    # Try to standardize the title
    title = songtitle_search(raw_title)

    # If we can't standardize it, use the raw name
    if not title:
        title = raw_title

    # Next, we ensure we're using the main title of the song
    title = get_main_title(title)

    song_obj = Song(title)
    filepath = os.path.join("../songs", song_obj.filename)

    if not Path(filepath).exists():
        while True:
            reply = str(input('Song does not exist. Try downloading from WikiSpiv? (y/n): ')).lower().strip()
            if reply and reply[0] == 'y':
                break
            if reply and reply[0] == 'n':
                return None
        with open(filepath, 'w', encoding='utf-8') as f:
            try:
                f.write(song_obj.to_chordpro())
            except ValueError as e:
                print(e)
                print("Skipping song")
                return None
        print(f"Downloaded '{title}' from WikiSpiv")
    return song_obj


def main():
    sections: List[Tuple[str, List[str], bool]] = [
        ("Гімни/Молотви",
         [
             "Гімн закарпатських пластунів",
             "Гімн Пласту",
             "Отче Наш",
             "Пластовий Обіт",
             "При ватрі",
             "Царю небесний"
         ],
         True
         )
    ]

    sections_objs = []
    for name, songs, sort_by_name in sections:
        song_lst = [get_song(song) for song in songs]
        song_lst: List[Song] = [x for x in song_lst if x]  # Filter None values

        sections_objs.append((name, song_lst, sort_by_name))

    render_pdf(sections_objs)


get_song("Час прощання")
