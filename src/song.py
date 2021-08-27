import re
from typing import List, Union
from bs4 import BeautifulSoup, ResultSet
import requests
from src.consts import *


def song_filename(title: str) -> str:
    """
    Given a song title, creates a standard filename
    :param title: The title of the song
    :return: The standardized filename of this song
    """
    return f"{snake_case(title)}.cho"


def snake_case(string: str) -> str:
    """
    Converts the given string into snake case.
        THIS IS A ONE-WAY FUNCTION. Converting back from snake case is not foolproof.
    :param string: The string to convert
    :return: The snake-case version of the string
    """
    string = string.lower().replace(' ', '_')
    string = ''.join(char for char in string if FILE_RE.match(char))
    # Ensure that we don't have any double underscores as a result
    while '__' in string:
        string = string.replace('__', '_')
    return string


def songtitle_search(title: str) -> Union[str, None]:
    """
    Finds the title most closely matching the given title
    :param title: The title for which we want to search
    :return: Either the closest matching title, or None if no titles match closely enough
    """
    title = title.replace("_", " ")
    url = f"{WIKI_API_URL}&action=query&list=search&srsearch={title}&srwhat="
    # We try the most specific search type first
    response = requests.get(f"{url}nearmatch").json()
    results = response["query"]["search"]

    if len(results) == 0:
        response = requests.get(f"{url}title").json()
        results = response["query"]["search"]

    return results[0]["title"] if results else None


def get_main_title(title: str) -> str:
    """
    Gets the root page - ie. the page to which this page redirects to.
    :param title: The EXACT title of the page we want to query
    :return: the title of the root page
    """
    response = requests.get(f"{WIKI_API_URL}&action=query&titles={title}&redirects").json()
    # Get the resulting page from this query. This is the root page - ie. follow all redirects until there are no more
    #   If a page has no redirects, the root page is itself
    main_pages = response["query"]["pages"].values()
    main_page = list(main_pages)[0]

    return main_page["title"]


def get_backlinks(title: str) -> List[str]:
    """
    Find every page which redirects to this page
    :param title: The EXACT title of the page, for which we want to find the backlinks
    :return: The titles of every page which redirects to this one, in alphabetical order
    """

    response = requests.get(f"{WIKI_API_URL}&action=query&generator=redirects&titles={title}").json()
    if "query" not in response or "pages" not in response["query"]:
        return []

    return sorted(page["title"] for _, page in response["query"]["pages"].items())


class Song:
    def __init__(self, title: str):
        self.title = title
        self.main_title = get_main_title(title)
        # Get the alternate titles of the song
        self.alt_titles = get_backlinks(self.main_title)
        # The filepath FROM THE PROJECT ROOT
        self.filename = song_filename(title)

    def download_from_wiki(self) -> [List[str], ResultSet]:
        """
        Downloads the Wiki page of the given song, and parses its contents
        :return: A tuple containing the credits and song contents, respectively
        """
        r = requests.get(f"{WIKI_SONG_URL}/{self.main_title}?action=render")

        if not r.ok:
            raise ValueError(f"Could not retrieve song {self.main_title} from WikiSpiv (error: {r.status_code})")

        soup = BeautifulSoup(r.text, 'html.parser')

        song_credits = sorted([cred.get_text() for cred in soup.find_all('div', class_='credit')])
        song_credits = [cred for cred in song_credits if cred]
        song_contents = soup.find_all('div', class_='spiv')[0]

        return song_credits, song_contents

    def to_chordpro(self) -> str:
        """
        Converts this Song object to ChordPro format
        :return: The ChordPro formatted string of this Song
        """
        # Query the Wiki page - get the credits and contents of the song
        raw_credits, raw_contents = self.download_from_wiki()
        out = ["## Saved from WIKISPIV.com", f"{{title: {self.title}}}"]
        out.extend((f"{{meta: alt_title {alt}}}" for alt in self.alt_titles))
        out.extend((f"{{subtitle: {credit}}}" for credit in raw_credits))
        out.append('\n')
        out.append(lyrics_to_chordpro(raw_contents))

        return '\n'.join(out)

    def get_chords(self):
        with open(os.path.join(ROOT_DIR, 'songs', self.filename), encoding='utf-8') as f:
            return set([x.group(1) for x in re.finditer(RE_CHORD, f.read())])


def lyrics_to_chordpro(content: ResultSet) -> str:
    """
    Converts WikiSpiv lyrics to ChordPro format
    @param content: The content of the WikiSpiv-formatted song
    @return: A string containing the ChordPro formatted lyrics
    """
    out = []
    for line in content.find_all('div'):
        line_lst = ["\t"] if "indented" in line['class'] else []

        for span in line.find_all('span'):
            # If it's a linediv, we don't care - we care about the div inside
            if span['class'] == "linediv":
                span = span.contents[0]

            if "indented" in span['class']:
                line_lst.append("\t")
            if "data-chord" in span.attrs:
                chord = f"[{span['data-chord']}]" if span['data-chord'] else ""
                line_lst.append(f"{chord}{span.string}")
            elif "bang" in span['class']:
                line_lst.append(f"<bold>{span.string}</bold>")
            elif "chord" in span['class']:
                line_lst.append(' '.join(f"[{chord}]" for chord in span.string.split()))
            else:
                line_lst.append(span.string)

        out.append(''.join(line_lst))
    return '\n'.join(out)
