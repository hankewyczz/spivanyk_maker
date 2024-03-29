import collections
import os
from re import compile
from typing import Tuple


class Font:
    def __init__(self, family: str, style: str, size: int, color: Tuple[int, int, int] = (0, 0, 0)):
        self.family = family
        self.style = style
        self.size = size
        self.color = color

class Config:
    # These values are dependent on other values, so we assign these after all other values are set
    USABLE_PAGE_WIDTH = None
    USABLE_PAGE_HEIGHT = None
    CHORD_HEIGHT = None


    ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    # WikiSpiv URL endpoints
    WIKI_ROOT_URL = "https://www.wikispiv.com"  # The root WikiSpiv domain
    WIKI_SONG_URL = f"{WIKI_ROOT_URL}/wiki"  # The root wiki location (ie. the level at which songs are)
    WIKI_API_URL = f"{WIKI_ROOT_URL}/api.php?format=json"  # The API endpoint

    # FPDF constants
    PDF_UNIT: str = "pt"  # The unit used for measurements - pt, mm, cm, in
    PDF_WIDTH: float = 5.5 * 72  # The width of the page (including margins)
    PDF_HEIGHT: float = 8.5 * 72  # The height of the page (including margins)
    # PDF margins
    PDF_MARGIN_TOP: float = 30
    PDF_MARGIN_LEFT: float = 28
    PDF_MARGIN_RIGHT: float = 28
    PDF_MARGIN_BOTTOM: float = 28
    PDF_INDENT = 20  # The size of a paragraph indent
    MIN_COLUMN_MARGIN = 15  # The minimum margin between columns
    MAX_COLUMN_MARGIN = 30  # The maximum margin between columns
    MIN_SONG_HEIGHT = 70  # The minimum height for each column
    MIN_IMAGE_HEIGHT = 150  # THe minimum height for an image at the bottom of the page
    # If we don't have at least this much space, we evenly spread the songs out to use up that space.
    #   No point in leaving that space unused if it's smaller than this
    SONG_MARGIN = 20  # Horizontal margin between songs
    SONG_TITLE_MARGIN = 10 # Margin between the song info and the words
    LINE_HEIGHT = 1

    # Chords
    CHORD_WIDTH = 50
    CHORD_STRING_HEIGHT = 100  # The height of the strings
    CHORD_MARGIN_HORIZONTAL = 20
    CHORD_MARGIN_VERTICAL = 20
    CHORD_CIRCLE_DIAM = 8
    MAX_FRETS = 4

    # Font variables

    BODY_FONT = {
        "family": "Open Sans",
        "style": "",
        "size": 10,
        "color": (0, 0, 0) 
	}
    TITLE_FONT = {
        "family": "Poiret One",
        "style": "",
        "size": 20,
        "color": (0, 0, 0) 
	}
    ALT_TITLE_FONT = {
        "family": "Poiret One",
        "style": "",
        "size": 14,
        "color": (0, 0, 0) 
	}
    SUBTITLE_FONT = {
        "family": "Open Sans",
        "style": "I",
        "size": 8,
        "color": (0, 0, 0) 
	}
    CHORD_FONT = {
        "family": "Open Sans",
        "style": "B",
        "size": 8,
        "color": (25, 25, 25)
	}
    INDEX_TITLE_FONT = {
        "family": "Open Sans",
        "style": "B",
        "size": 10,
        "color": (0, 0, 0) 
	}
    INDEX_SONG_FONT = {
        "family": "Open Sans",
        "style": "",
        "size": 9,
        "color": (0, 0, 0) 
	}
    INDEX_SONG_PADDING = 3

    # Assorted regex constants
    # Regex matching a valid filename
    FILE_RE = compile("[А-ЯҐЄІЇа-яґєії\\w]")


    # ChordPro Regex
    def regex_meta(command: str):
        return compile(f'^{{(?:meta:)?\\s*(?P<command>{command}):?\\s*(?P<args>.*)}}')


    RE_COMMENT = compile('^#(.*)')
    RE_TITLE = regex_meta("title")
    RE_SUBTITLE = regex_meta("subtitle")
    RE_ALT_TITLE = regex_meta("alt_title")
    RE_SONG_NUMBER = regex_meta("song_number")
    RE_CATEGORY = regex_meta("category")
    RE_META = regex_meta(".*")
    RE_CHORD = compile('\\[\\(?(.*?)\\)?]')
    RE_LYRICS_CHORDS = compile('.*\\[.*].*')
    RE_BOLD = compile('(?:<(?:bold|b)>)(.*)(?:<\/(?:b|bold)>)')
    RE_ITALIC = compile('(?:<i>)(.*)(?:</i>)')

    
    INDEX_CATEGORIES = []
    """ These are the only categories that we'll show in the index. Default is [] """

    KNOWN_CHORDS = {
        "C": {"base": 1, "frets": [-1, 3, 2, 0, 1, 0]},
        "Cm": {"base": 3, "frets": [-1, 1, 3, 3, 2, 1]},
        "Caug": {"base": 1, "frets": [-1, -1, 2, 1, 1, 0]},
        "Cdim": {"base": 3, "frets": [-1, 1, 2, 3, 2, -1]},
        "Cdim7": {"base": 1, "frets": [-1, -1, 1, 2, 1, 2]},
        "C7": {"base": 1, "frets": [0, 3, 2, 3, 1, 0]},
        "Cmaj7": {"base": 1, "frets": [-1, 3, 2, 0, 0, 0]},
        "Cm7": {"base": 3, "frets": [-1, 1, 3, 1, 2, 1]},
        "Csus4": {"base": 1, "frets": [-1, -1, 3, 0, 1, 3]},
        "Csus": {"copy": "Csus4"},
        "C4": {"copy": "Csus4"},
        "C0": {"copy": "Cdim"},
        "C⁰": {"copy": "Cdim"},
        "Cmb5": {"copy": "Cdim"},
        "Cm7b5": {"copy": "Cdim7"},
        "Cm7(b5)": {"copy": "Cdim7"},
        "Ch": {"copy": "Cdim7"},
        "Cø": {"copy": "Cdim7"},
        "C+": {"copy": "Caug"},
        "Cmin": {"copy": "Cm"},
        "C(maj7)": {"copy": "Cmaj7"},
        "C6": {"base": 1, "frets": [-1, 3, 2, 2, 1, 0]},
        "C9": {"base": 8, "frets": [1, 3, 1, 2, 1, 3]},
        "Cadd9": {"base": 1, "frets": [-1, 3, 2, 0, 3, 0]},
        "C(add9)": {"copy": "Cadd9"},
        "Csus9": {"base": 7, "frets": [-1, -1, 4, 1, 2, 4]},
        "C(sus9)": {"copy": "Csus9"},
        "C9(11)": {"base": 1, "frets": [-1, 3, 3, 3, 3, -1]},
        "C11": {"base": 3, "frets": [-1, 1, 3, 1, 4, 1]},
        "Csus2": {"base": 1, "frets": [-1, 3, 0, 0, 1, -1]},
        "C#": {"base": 1, "frets": [-1, -1, 3, 1, 2, 1]},
        "C#m": {"base": 1, "frets": [-1, -1, 2, 1, 2, 0]},
        "C#aug": {"base": 1, "frets": [-1, -1, 3, 2, 2, 1]},
        "C#dim": {"base": 4, "frets": [-1, 1, 2, 3, 4, -1]},
        "C#dim7": {"base": 1, "frets": [-1, -1, 2, 3, 2, 3]},
        "C#7": {"base": 1, "frets": [-1, -1, 3, 4, 2, 4]},
        "C#maj7": {"base": 1, "frets": [-1, 4, 3, 1, 1, 1]},
        "C#m7": {"base": 1, "frets": [-1, -1, 2, 4, 2, 4]},
        "C#sus4": {"base": 4, "frets": [-1, -1, 3, 3, 4, 1]},
        "C#sus": {"copy": "C#sus4"},
        "C#4": {"copy": "C#sus4"},
        "C#0": {"copy": "C#dim"},
        "C#⁰": {"copy": "C#dim"},
        "C#mb5": {"copy": "C#dim"},
        "C#m7b5": {"copy": "C#dim7"},
        "C#m7(b5)": {"copy": "C#dim7"},
        "C#h": {"copy": "C#dim7"},
        "C#ø": {"copy": "C#dim7"},
        "C#+": {"copy": "C#aug"},
        "C#min": {"copy": "C#m"},
        "C#(maj7)": {"copy": "C#maj7"},
        "C#add9": {"base": 4, "frets": [-1, 1, 3, 3, 1, 1]},
        "C#(add9)": {"copy": "C#add9"},
        "Db": {"copy": "C#"},
        "Dbm": {"copy": "C#m"},
        "Dbaug": {"copy": "C#aug"},
        "Dbdim": {"copy": "C#dim"},
        "Dbdim7": {"copy": "C#dim7"},
        "Db7": {"copy": "C#7"},
        "Dbmaj7": {"copy": "C#maj7"},
        "Dbm7": {"copy": "C#m7"},
        "Dbsus4": {"copy": "C#sus4"},
        "Dbsus": {"copy": "Dbsus4"},
        "Db4": {"copy": "Dbsus4"},
        "Db0": {"copy": "Dbdim"},
        "Db⁰": {"copy": "Dbdim"},
        "Dbmb5": {"copy": "Dbdim"},
        "Dbm7b5": {"copy": "Dbdim7"},
        "Dbm7(b5)": {"copy": "Dbdim7"},
        "Dbh": {"copy": "Dbdim7"},
        "Dbø": {"copy": "Dbdim7"},
        "Db+": {"copy": "Dbaug"},
        "Dbmin": {"copy": "Dbm"},
        "Db(maj7)": {"copy": "Dbmaj7"},
        "D": {"base": 1, "frets": [-1, -1, 0, 2, 3, 2]},
        "Dm": {"base": 1, "frets": [-1, -1, 0, 2, 3, 1]},
        "Daug": {"base": 1, "frets": [-1, -1, 0, 3, 3, 2]},
        "Ddim": {"base": 1, "frets": [-1, -1, 0, 1, 3, 1]},
        "Ddim7": {"base": 1, "frets": [-1, -1, 0, 1, 0, 1]},
        "D7": {"base": 1, "frets": [-1, -1, 0, 2, 1, 2]},
        "Dmaj7": {"base": 1, "frets": [-1, -1, 0, 2, 2, 2]},
        "Dm7": {"base": 1, "frets": [-1, -1, 0, 2, 1, 1]},
        "Dsus4": {"base": 1, "frets": [-1, -1, 0, 2, 3, 3]},
        "Dsus": {"copy": "Dsus4"},
        "D4": {"copy": "Dsus4"},
        "D0": {"copy": "Ddim"},
        "D⁰": {"copy": "Ddim"},
        "Dmb5": {"copy": "Ddim"},
        "Dm7b5": {"copy": "Ddim7"},
        "Dm7(b5)": {"copy": "Ddim7"},
        "Dh": {"copy": "Ddim7"},
        "Dø": {"copy": "Ddim7"},
        "D+": {"copy": "Daug"},
        "Dmin": {"copy": "Dm"},
        "D(maj7)": {"copy": "Dmaj7"},
        "D6": {"base": 1, "frets": [-1, 0, 0, 2, 0, 2]},
        "D9": {"base": 10, "frets": [1, 3, 1, 2, 1, 3]},
        "Dm9": {"base": 1, "frets": [-1, -1, 3, 2, 1, 0]},
        "Dadd9": {"base": 1, "frets": [0, 0, 0, 2, 3, 2]},
        "D(add9)": {"copy": "Dadd9"},
        "D11": {"base": 1, "frets": [3, 0, 0, 2, 1, 0]},
        "Dsus2": {"base": 1, "frets": [0, 0, 0, 2, 3, 0]},
        "D#": {"base": 3, "frets": [-1, -1, 3, 1, 2, 1]},
        "D#m": {"base": 1, "frets": [-1, -1, 4, 3, 4, 2]},
        "D#aug": {"base": 1, "frets": [-1, -1, 1, 0, 0, 4]},
        "D#dim": {"base": 1, "frets": [-1, -1, 1, 2, 4, 2]},
        "D#dim7": {"base": 1, "frets": [-1, -1, 1, 2, 1, 2]},
        "D#7": {"base": 1, "frets": [-1, -1, 1, 3, 2, 3]},
        "D#maj7": {"base": 1, "frets": [-1, -1, 1, 3, 3, 3]},
        "D#m7": {"base": 1, "frets": [-1, -1, 1, 3, 2, 2]},
        "D#sus4": {"base": 1, "frets": [-1, -1, 1, 3, 4, 4]},
        "D#sus": {"copy": "D#sus4"},
        "D#4": {"copy": "D#sus4"},
        "D#0": {"copy": "D#dim"},
        "D#⁰": {"copy": "D#dim"},
        "D#mb5": {"copy": "D#dim"},
        "D#m7b5": {"copy": "D#dim7"},
        "D#m7(b5)": {"copy": "D#dim7"},
        "D#h": {"copy": "D#dim7"},
        "D#ø": {"copy": "D#dim7"},
        "D#+": {"copy": "D#aug"},
        "D#min": {"copy": "D#m"},
        "D#(maj7)": {"copy": "D#maj7"},
        "Eb": {"copy": "D#"},
        "Ebm": {"copy": "D#m"},
        "Ebaug": {"copy": "D#aug"},
        "Ebdim": {"copy": "D#dim"},
        "Ebdim7": {"copy": "D#dim7"},
        "Eb7": {"copy": "D#7"},
        "Ebmaj7": {"copy": "D#maj7"},
        "Ebm7": {"copy": "D#m7"},
        "Ebsus4": {"copy": "D#sus4"},
        "Ebsus": {"copy": "Ebsus4"},
        "Eb4": {"copy": "Ebsus4"},
        "Eb0": {"copy": "Ebdim"},
        "Eb⁰": {"copy": "Ebdim"},
        "Ebmb5": {"copy": "Ebdim"},
        "Ebm7b5": {"copy": "Ebdim7"},
        "Ebm7(b5)": {"copy": "Ebdim7"},
        "Ebh": {"copy": "Ebdim7"},
        "Ebø": {"copy": "Ebdim7"},
        "Eb+": {"copy": "Ebaug"},
        "Ebmin": {"copy": "Ebm"},
        "Eb(maj7)": {"copy": "Ebmaj7"},
        "Ebadd9": {"base": 1, "frets": [-1, 1, 1, 3, 4, 1]},
        "Eb(add9)": {"copy": "Ebadd9"},
        "E": {"base": 1, "frets": [0, 2, 2, 1, 0, 0]},
        "Em": {"base": 1, "frets": [0, 2, 2, 0, 0, 0]},
        "Eaug": {"base": 1, "frets": [-1, -1, 2, 1, 1, 0]},
        "Edim": {"base": 1, "frets": [0, 1, 2, 0, -1, -1]},
        "Edim7": {"base": 1, "frets": [-1, -1, 2, 3, 2, 3]},
        "E7": {"base": 1, "frets": [0, 2, 2, 1, 3, 0]},
        "Emaj7": {"base": 1, "frets": [0, 2, 1, 1, 0, -1]},
        "Em7": {"base": 1, "frets": [0, 2, 2, 0, 3, 0]},
        "Esus4": {"base": 1, "frets": [0, 2, 2, 2, 0, 0]},
        "Esus": {"copy": "Esus4"},
        "E4": {"copy": "Esus4"},
        "E0": {"copy": "Edim"},
        "E⁰": {"copy": "Edim"},
        "Emb5": {"copy": "Edim"},
        "Em7b5": {"copy": "Edim7"},
        "Em7(b5)": {"copy": "Edim7"},
        "Eh": {"copy": "Edim7"},
        "Eø": {"copy": "Edim7"},
        "E+": {"copy": "Eaug"},
        "Emin": {"copy": "Em"},
        "E(maj7)": {"copy": "Emaj7"},
        "E6": {"base": 9, "frets": [-1, -1, 3, 3, 3, 3]},
        "Em6": {"base": 1, "frets": [0, 2, 2, 0, 2, 0]},
        "E9": {"base": 1, "frets": [1, 3, 1, 2, 1, 3]},
        "E11": {"base": 1, "frets": [1, 1, 1, 1, 2, 2]},
        "F": {"base": 1, "frets": [1, 3, 3, 2, 1, 1]},
        "Fm": {"base": 1, "frets": [1, 3, 3, 1, 1, 1]},
        "Faug": {"base": 1, "frets": [-1, -1, 3, 2, 2, 1]},
        "Fdim": {"base": 1, "frets": [-1, -1, 3, 1, 0, 1]},
        "Fdim7": {"base": 1, "frets": [-1, -1, 0, 1, 0, 1]},
        "F7": {"base": 1, "frets": [1, 3, 1, 2, 1, 1]},
        "Fmaj7": {"base": 1, "frets": [-1, 3, 3, 2, 1, 0]},
        "Fm7": {"base": 1, "frets": [1, 3, 1, 1, 1, 1]},
        "Fsus4": {"base": 1, "frets": [-1, -1, 3, 3, 1, 1]},
        "Fsus": {"copy": "Fsus4"},
        "F4": {"copy": "Fsus4"},
        "F0": {"copy": "Fdim"},
        "F⁰": {"copy": "Fdim"},
        "Fmb5": {"copy": "Fdim"},
        "Fm7b5": {"copy": "Fdim7"},
        "Fm7(b5)": {"copy": "Fdim7"},
        "Fh": {"copy": "Fdim7"},
        "Fø": {"copy": "Fdim7"},
        "F+": {"copy": "Faug"},
        "Fmin": {"copy": "Fm"},
        "F(maj7)": {"copy": "Fmaj7"},
        "F6": {"base": 1, "frets": [-1, 3, 3, 2, 3, -1]},
        "Fm6": {"base": 1, "frets": [-1, -1, 0, 1, 1, 1]},
        "F9": {"base": 1, "frets": [2, 4, 2, 3, 2, 4]},
        "Fadd9": {"base": 1, "frets": [3, 0, 3, 2, 1, 1]},
        "F(add9)": {"copy": "Fadd9"},
        "F11": {"base": 1, "frets": [1, 3, 1, 3, 1, 1]},
        "F#": {"base": 1, "frets": [2, 4, 4, 3, 2, 2]},
        "F#m": {"base": 1, "frets": [2, 4, 4, 2, 2, 2]},
        "F#aug": {"base": 1, "frets": [-1, -1, 4, 3, 3, 2]},
        "F#dim": {"base": 1, "frets": [-1, -1, 4, 2, 1, 2]},
        "F#dim7": {"base": 1, "frets": [-1, -1, 1, 2, 1, 2]},
        "F#7": {"base": 1, "frets": [-1, -1, 4, 3, 2, 0]},
        "F#maj7": {"base": 1, "frets": [-1, -1, 4, 3, 2, 1]},
        "F#m7": {"base": 1, "frets": [2, 0, 2, 2, 2, 0]},
        "F#sus4": {"base": 1, "frets": [-1, -1, 4, 4, 2, 2]},
        "F#sus": {"copy": "F#sus4"},
        "F#4": {"copy": "F#sus4"},
        "F#0": {"copy": "F#dim"},
        "F#⁰": {"copy": "F#dim"},
        "F#mb5": {"copy": "F#dim"},
        "F#m7b5": {"copy": "F#dim7"},
        "F#m7(b5)": {"copy": "F#dim7"},
        "F#h": {"copy": "F#dim7"},
        "F#ø": {"copy": "F#dim7"},
        "F#+": {"copy": "F#aug"},
        "F#min": {"copy": "F#m"},
        "F#(maj7)": {"copy": "F#maj7"},
        "F#m6": {"base": 1, "frets": [-1, -1, 1, 2, 2, 2]},
        "F#9": {"base": 1, "frets": [-1, 1, 2, 1, 2, 2]},
        "F#11": {"base": 1, "frets": [2, 4, 2, 4, 2, 2]},
        "Gb": {"copy": "F#"},
        "Gbm": {"copy": "F#m"},
        "Gbaug": {"copy": "F#aug"},
        "Gbdim": {"copy": "F#dim"},
        "Gbdim7": {"copy": "F#dim7"},
        "Gb7": {"copy": "F#7"},
        "Gbmaj7": {"copy": "F#maj7"},
        "Gbm7": {"copy": "F#m7"},
        "Gbsus4": {"copy": "F#sus4"},
        "Gbsus": {"copy": "Gbsus4"},
        "Gb4": {"copy": "Gbsus4"},
        "Gb0": {"copy": "Gbdim"},
        "Gb⁰": {"copy": "Gbdim"},
        "Gbmb5": {"copy": "Gbdim"},
        "Gbm7b5": {"copy": "Gbdim7"},
        "Gbm7(b5)": {"copy": "Gbdim7"},
        "Gbh": {"copy": "Gbdim7"},
        "Gbø": {"copy": "Gbdim7"},
        "Gb+": {"copy": "Gbaug"},
        "Gbmin": {"copy": "Gbm"},
        "Gb(maj7)": {"copy": "Gbmaj7"},
        "Gbm6": {"copy": "F#m6"},
        "Gb9": {"copy": "F#9"},
        "G": {"base": 1, "frets": [3, 2, 0, 0, 0, 3]},
        "Gm": {"base": 3, "frets": [1, 3, 3, 1, 1, 1]},
        "Gaug": {"base": 1, "frets": [-1, -1, 1, 0, 0, 4]},
        "Gdim": {"base": 3, "frets": [1, 2, 3, 1, -1, -1]},
        "Gdim7": {"base": 1, "frets": [-1, -1, 2, 3, 2, 3]},
        "G7": {"base": 1, "frets": [3, 2, 0, 0, 0, 1]},
        "Gmaj7": {"base": 2, "frets": [-1, -1, 4, 3, 2, 1]},
        "Gm7": {"base": 3, "frets": [1, 3, 1, 1, 1, 1]},
        "Gsus4": {"base": 1, "frets": [-1, -1, 0, 0, 1, 1]},
        "Gsus": {"copy": "Gsus4"},
        "G4": {"copy": "Gsus4"},
        "G0": {"copy": "Gdim"},
        "G⁰": {"copy": "Gdim"},
        "Gmb5": {"copy": "Gdim"},
        "Gm7b5": {"copy": "Gdim7"},
        "Gm7(b5)": {"copy": "Gdim7"},
        "Gh": {"copy": "Gdim7"},
        "Gø": {"copy": "Gdim7"},
        "G+": {"copy": "Gaug"},
        "Gmin": {"copy": "Gm"},
        "G(maj7)": {"copy": "Gmaj7"},
        "G6": {"base": 1, "frets": [3, -1, 0, 0, 0, 0]},
        "Gm6": {"base": 1, "frets": [-1, -1, 2, 3, 3, 3]},
        "G9": {"base": 1, "frets": [3, -1, 0, 2, 0, 1]},
        "Gadd9": {"base": 3, "frets": [1, 3, -1, 2, 1, 3]},
        "G(add9)": {"copy": "Gadd9"},
        "G9(11)": {"base": 3, "frets": [1, 3, 1, 3, 1, 3]},
        "G11": {"base": 1, "frets": [3, -1, 0, 2, 1, 1]},
        "G#": {"base": 4, "frets": [1, 3, 3, 2, 1, 1]},
        "G#m": {"base": 4, "frets": [1, 3, 3, 1, 1, 1]},
        "G#aug": {"base": 1, "frets": [-1, -1, 2, 1, 1, 0]},
        "G#dim": {"base": 4, "frets": [1, 2, 3, 1, -1, -1]},
        "G#dim7": {"base": 1, "frets": [-1, -1, 0, 1, 0, 1]},
        "G#7": {"base": 1, "frets": [-1, -1, 1, 1, 1, 2]},
        "G#maj7": {"base": 1, "frets": [-1, -1, 1, 1, 1, 3]},
        "G#m7": {"base": 4, "frets": [-1, -1, 1, 1, 1, 1]},
        "G#sus4": {"base": 1, "frets": [-1, -1, 1, 1, 2, 4]},
        "G#sus": {"copy": "G#sus4"},
        "G#4": {"copy": "G#sus4"},
        "G#0": {"copy": "G#dim"},
        "G#⁰": {"copy": "G#dim"},
        "G#mb5": {"copy": "G#dim"},
        "G#m7b5": {"copy": "G#dim7"},
        "G#m7(b5)": {"copy": "G#dim7"},
        "G#h": {"copy": "G#dim7"},
        "G#ø": {"copy": "G#dim7"},
        "G#+": {"copy": "G#aug"},
        "G#min": {"copy": "G#m"},
        "G#(maj7)": {"copy": "G#maj7"},
        "G#m6": {"base": 1, "frets": [-1, -1, 1, 1, 0, 1]},
        "Ab": {"copy": "G#"},
        "Abm": {"copy": "G#m"},
        "Abaug": {"copy": "G#aug"},
        "Abdim": {"copy": "G#dim"},
        "Abdim7": {"copy": "G#dim7"},
        "Ab7": {"copy": "G#7"},
        "Abmaj7": {"copy": "G#maj7"},
        "Abm7": {"copy": "G#m7"},
        "Absus4": {"copy": "G#sus4"},
        "Absus": {"copy": "Absus4"},
        "Ab4": {"copy": "Absus4"},
        "Ab0": {"copy": "Abdim"},
        "Ab⁰": {"copy": "Abdim"},
        "Abmb5": {"copy": "Abdim"},
        "Abm7b5": {"copy": "Abdim7"},
        "Abm7(b5)": {"copy": "Abdim7"},
        "Abh": {"copy": "Abdim7"},
        "Abø": {"copy": "Abdim7"},
        "Ab+": {"copy": "Abaug"},
        "Abmin": {"copy": "Abm"},
        "Ab(maj7)": {"copy": "Abmaj7"},
        "Abm6": {"copy": "G#m6"},
        "Ab11": {"base": 4, "frets": [1, 3, 1, 3, 1, 1]},
        "A": {"base": 1, "frets": [-1, 0, 2, 2, 2, 0]},
        "Am": {"base": 1, "frets": [-1, 0, 2, 2, 1, 0]},
        "Aaug": {"base": 1, "frets": [-1, 0, 3, 2, 2, 1]},
        "Adim": {"base": 1, "frets": [-1, 0, 1, 2, 1, -1]},
        "Adim7": {"base": 1, "frets": [-1, -1, 1, 2, 1, 2]},
        "A7": {"base": 1, "frets": [-1, 0, 2, 0, 2, 0]},
        "Amaj7": {"base": 1, "frets": [-1, 0, 2, 1, 2, 0]},
        "Am7": {"base": 1, "frets": [-1, 0, 2, 2, 1, 3]},
        "Asus4": {"base": 1, "frets": [-1, -1, 2, 2, 3, 0]},
        "Asus": {"copy": "Asus4"},
        "A4": {"copy": "Asus4"},
        "A0": {"copy": "Adim"},
        "A⁰": {"copy": "Adim"},
        "Amb5": {"copy": "Adim"},
        "Am7b5": {"copy": "Adim7"},
        "Am7(b5)": {"copy": "Adim7"},
        "Ah": {"copy": "Adim7"},
        "Aø": {"copy": "Adim7"},
        "A+": {"copy": "Aaug"},
        "Amin": {"copy": "Am"},
        "Am/F": {"base": 1, "frets": [1, 0, 2, 2, 1, 0]},
        "A(maj7)": {"copy": "Amaj7"},
        "A6": {"base": 1, "frets": [-1, -1, 2, 2, 2, 2]},
        "Am6": {"base": 1, "frets": [-1, 0, 2, 2, 1, 2]},
        "A9": {"base": 1, "frets": [-1, 0, 2, 1, 0, 0]},
        "Am9": {"base": 5, "frets": [-1, 0, 1, 1, 1, 3]},
        "A11": {"base": 1, "frets": [-1, 4, 2, 4, 3, 3]},
        "Asus2": {"base": 1, "frets": [0, 0, 2, 2, 0, 0]},
        "A#": {"base": 1, "frets": [-1, 1, 3, 3, 3, 1]},
        "A#m": {"base": 1, "frets": [-1, 1, 3, 3, 2, 1]},
        "A#aug": {"base": 1, "frets": [-1, -1, 0, 3, 3, 2]},
        "A#dim": {"base": 1, "frets": [-1, 1, 2, 3, 2, 0]},
        "A#dim7": {"base": 1, "frets": [-1, -1, 2, 3, 2, 3]},
        "A#7": {"base": 3, "frets": [-1, -1, 1, 1, 1, 2]},
        "A#maj7": {"base": 1, "frets": [-1, 1, 3, 2, 3, -1]},
        "A#m7": {"base": 1, "frets": [-1, 1, 3, 1, 2, 1]},
        "A#sus4": {"base": 1, "frets": [-1, -1, 3, 3, 4, 1]},
        "A#sus": {"copy": "A#sus4"},
        "A#4": {"copy": "A#sus4"},
        "A#0": {"copy": "A#dim"},
        "A#⁰": {"copy": "A#dim"},
        "A#mb5": {"copy": "A#dim"},
        "A#m7b5": {"copy": "A#dim7"},
        "A#m7(b5)": {"copy": "A#dim7"},
        "A#h": {"copy": "A#dim7"},
        "A#ø": {"copy": "A#dim7"},
        "A#+": {"copy": "A#aug"},
        "A#min": {"copy": "A#m"},
        "A#(maj7)": {"copy": "A#maj7"},
        "Bb": {"copy": "A#"},
        "Bbm": {"copy": "A#m"},
        "Bbaug": {"copy": "A#aug"},
        "Bbdim": {"copy": "A#dim"},
        "Bbdim7": {"copy": "A#dim7"},
        "Bb7": {"copy": "A#7"},
        "Bbmaj7": {"copy": "A#maj7"},
        "Bbm7": {"copy": "A#m7"},
        "Bbsus4": {"copy": "A#sus4"},
        "Bbsus": {"copy": "Bbsus4"},
        "Bb4": {"copy": "Bbsus4"},
        "Bb0": {"copy": "Bbdim"},
        "Bb⁰": {"copy": "Bbdim"},
        "Bbmb5": {"copy": "Bbdim"},
        "Bbm7b5": {"copy": "Bbdim7"},
        "Bbm7(b5)": {"copy": "Bbdim7"},
        "Bbh": {"copy": "Bbdim7"},
        "Bbø": {"copy": "Bbdim7"},
        "Bb+": {"copy": "Bbaug"},
        "Bbmin": {"copy": "Bbm"},
        "Bb(maj7)": {"copy": "Bbmaj7"},
        "Bb6": {"base": 1, "frets": [-1, -1, 3, 3, 3, 3]},
        "Bb9": {"base": 6, "frets": [1, 3, 1, 2, 1, 3]},
        "Bbm9": {"base": 6, "frets": [-1, -1, -1, 1, 1, 3]},
        "Bb11": {"base": 6, "frets": [1, 3, 1, 3, 4, 1]},
        "B": {"base": 1, "frets": [-1, 2, 4, 4, 4, 2]},
        "Bm": {"base": 1, "frets": [-1, 2, 4, 4, 3, 2]},
        "Baug": {"base": 1, "frets": [-1, -1, 1, 0, 0, 4]},
        "Bdim": {"base": 1, "frets": [-1, 2, 3, 4, 3, -1]},
        "Bdim7": {"base": 1, "frets": [-1, -1, 0, 1, 0, 1]},
        "B7": {"base": 1, "frets": [-1, 2, 1, 2, 0, 2]},
        "Bmaj7": {"base": 1, "frets": [-1, 2, 4, 3, 4, -1]},
        "Bm7": {"base": 2, "frets": [-1, 1, 3, 1, 2, 1]},
        "Bsus4": {"base": 2, "frets": [-1, -1, 3, 3, 4, 1]},
        "Bsus": {"copy": "Bsus4"},
        "B4": {"copy": "Bsus4"},
        "B0": {"copy": "Bdim"},
        "B⁰": {"copy": "Bdim"},
        "Bmb5": {"copy": "Bdim"},
        "Bm7b5": {"copy": "Bdim7"},
        "Bm7(b5)": {"copy": "Bdim7"},
        "Bh": {"copy": "Bdim7"},
        "Bø": {"copy": "Bdim7"},
        "B+": {"copy": "Baug"},
        "Bmin": {"copy": "Bm"},
        "B(maj7)": {"copy": "Bmaj7"},
        "Bm6": {"base": 1, "frets": [-1, -1, 4, 4, 3, 4]},
        "B9": {"base": 7, "frets": [1, 3, 1, 2, 1, 3]},
        "B11": {"base": 7, "frets": [1, 3, 3, 2, 0, 0]},
        "Bsus2": {"base": 1, "frets": [-1, 2, 4, 4, 2, 2]},
        "NC": {"base": 1, "frets": [-1, -1, -1, -1, -1, -1]},
        "N.C.": {"copy": "NC"}, }
    
    def updateDict(dict, data):
        if isinstance(data, collections.abc.Mapping):
            for k, v in data.items():
                if isinstance(v, collections.abc.Mapping):
                    dict[k] = Config.updateDict(dict.get(k, {}), v)
                else:
                    dict[k] = v
            return dict
        return data
