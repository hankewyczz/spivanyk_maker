from song import *
from pathlib import Path



def check_song(raw_title: str) -> Song:
    # Try to standardize the title
    title = songtitle_search(raw_title)

    if not title:
        raise ValueError(f"Song with title {title} could not be found")

    # Next, we ensure we're using the main title of the song
    title = get_main_title(title)

    song_obj = Song(title)

    if not Path(song_obj.filepath).exists():
        with open(song_obj.filepath, 'w', encoding='utf-8') as f:
            f.write(song_obj.to_chordpro())
        # TODO - ask the user if they want to download
        print(f"Downloaded '{title}' from WikiSpiv")
    else:
        print(f"Using existing {song_obj.filepath} for {raw_title}")

    return song_obj


check_song("Час прощання")