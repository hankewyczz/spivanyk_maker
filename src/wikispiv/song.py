from typing import Optional, Tuple, List, Union
from bs4 import BeautifulSoup, ResultSet
import requests


ROOT = "https://www.wikispiv.com"
WIKI = f"{ROOT}/wiki"
API_URL = f"{ROOT}/api.php?format=json"

VALID_FILE_CHARS = "бвгґджзклмнпрстфхцчшщйаеєиіїоуюяьБВГҐДЖЗКЛМНПРСТФХЦЧШЩЙАЕЄИІЇОУЮЯЬ_"


def song_filename(title: str) -> str:
    '''
    Gets the standard song filename
    :param title: The title of the song
    :return: The filename of the song with this name
    '''
    return f"{snake_case(title)}.cho"


def snake_case(string: str) -> str:
    '''
    Converts the given string into snake case
    :param string: The string to convert
    :return: The snake-case version of the string
    '''
    string = string.lower().replace(' ', '_')
    return ''.join(char for char in string if char in VALID_FILE_CHARS)


def songtitle_search(title: str) -> Union[str, None]:
    '''
    Finds the title most closely matching the given title
    :param title: The title for which we want to search
    :return: Either the closest matching title, or None if no titles match closely enough
    '''
    title = title.replace("_", " ")
    response = requests.get(f"{API_URL}&action=query&list=search&srsearch={title}").json()
    results = response["query"]["search"]

    if len(results) > 0:
        return results[0]["title"]

    return None

def get_main_title(title: str) -> str:
    '''
    Gets the root page - ie. the page to which this page redirects to.
    :param title: The EXACT title of the page we want to query
    :return: the title of the root page
    '''
    response = requests.get(f"{API_URL}&action=query&titles={title}&redirects").json()
    # Get the resulting page from this query. This is the root page - ie. follow all redirects until there are no more
    #   If a page has no redirects, the root page is itself
    main_pages = response["query"]["pages"].values()
    main_page = list(main_pages)[0]

    return main_page["title"]

def get_backlinks(title: str) -> List[str]:
    '''
    Find every page which redirects to this page
    :param title: The EXACT title of the page, for which we want to find the backlinks
    :return: The titles of every page which redirects to this one, in alphabetical order
    '''
    response = requests.get(f"{API_URL}&action=query&list=backlinks&bltitle={title}").json()
    return sorted([link["title"] for link in response["query"]["backlinks"]])


class Song:
    def __init__(self, title: str):
        self.title = title
        # Get the alternate titles of the song
        self.alt_titles = get_backlinks(self.title)
        # Query the Wiki page - get the credits and contents of the song
        self.credits, self.raw_contents = self.download_from_wiki()

    def download_from_wiki(self) -> Tuple[Optional[List[str]], ResultSet]:
        '''
        Downloads the Wiki page of the given song, and parses its contents
        :return: A tuple containing the credits and song contents, respectively
        '''
        r = requests.get(f"{WIKI}/{self.title}?action=render")

        if not r.ok:
            raise ValueError(f"Could not retrieve song {self.title} from WikiSpiv (error: {r.status_code}")

        soup = BeautifulSoup(r.text, 'html.parser')

        song_credits = soup.find_all('div', class_='credits')

        if len(song_credits) > 0:
            song_credits = sorted([cred.get_text() for cred in song_credits[0].find_all('div', class_='credit')])
        else:
            song_credits = None

        song_contents = soup.find_all('div', class_='spiv')
        song_contents = song_contents[0]  # We don't bother checking here - if it fails, its a fatal error

        return song_credits, song_contents

    def to_chordpro(self) -> str:
        '''
        Converts this Song object to ChordPro format
        :return: The ChordPro formatted string of this Song
        '''
        out = [f"{{title: {self.title}}}"]
        out.extend((f"{{meta: alt_title {alt}}}" for alt in self.alt_titles))
        out.extend((f"{{subtitle: {credit}}}" for credit in self.credits))
        out.append('\n')
        out.append(lyrics_to_chordpro(self.raw_contents))

        return '\n'.join(out)


def lyrics_to_chordpro(content: ResultSet) -> str:
    out = []
    for line in content.find_all('div'):
        line_lst = []
        if "indented" in line['class']:
            line_lst.append("\t")

        for span in line.find_all('span'):
            if span['class'] == "linediv":
                span = span.contents[0]

            if "indented" in span['class']:
                line_lst.append("\t")

            if "data-chord" in span.attrs:
                chord = f"[{span['data-chord']}]" if span['data-chord'] else ""
                line_lst.append(f"{chord}{span.string}")
            elif "bang" in span['class']:
                line_lst.append(f"<bold>{span.string}</bold>")
            else:
                line_lst.append(span.string)

        out.append(''.join(line_lst))
    return '\n'.join(out)
