# Directory variables
from os.path import normpath, join
from re import compile
from typing import Union

ROOT_DIR: str = normpath("../../")
FONTS_DIR = join(ROOT_DIR, 'assets/fonts')
SONGS_DIR = join(ROOT_DIR, 'songs')

# PDF setup variables
PDF_UNIT: str = "pt"  # pt, mm, cm, in
PDF_WIDTH: Union[float, int] = 396  # The width of the page in PDF_UNIT
PDF_HEIGHT: Union[float, int] = 612  # The height of the page in PDF_UNIT
# Margins
PDF_MARGIN_TOP: float = 30
PDF_MARGIN_LEFT: float = 28
PDF_MARGIN_RIGHT: float = 28
PDF_MARGIN_BOTTOM: float = 28
PDF_INDENT = 20
COLUMN_MARGIN = 15
SONG_MARGIN = 50    # Margin between songs

PAGE_WIDTH = PDF_WIDTH - (PDF_MARGIN_RIGHT + PDF_MARGIN_LEFT)
PAGE_HEIGHT = PDF_HEIGHT - (PDF_MARGIN_BOTTOM + PDF_MARGIN_TOP)

# Font variables
BODY_FONT = "Open Sans"
BODY_FONT_STYLE = ""
BODY_FONT_SIZE = 10

TITLE_FONT = "Poiret One"
TITLE_FONT_SIZE = 20

ALT_TITLE_FONT = TITLE_FONT
ALT_TITLE_FONT_SIZE = 14

SUBTITLE_FONT = BODY_FONT
SUBTITLE_FONT_STYLE = "I"
SUBTITLE_FONT_SIZE = 8

CHORD_FONT = BODY_FONT
CHORD_FONT_STYLE = "U"
CHORD_FONT_SIZE = 10


# ChordPro Regex
def regex_meta(command: str):
    return compile(f'^{{(?:meta:)?\\s*(?P<command>{command}):?\\s*(?P<args>.*)}}')


RE_COMMENT = compile('^#(.*)')
RE_TITLE = regex_meta("title")
RE_SUBTITLE = regex_meta("subtitle")
RE_ALT_TITLE = regex_meta("alt_title")
RE_META = regex_meta(".*")
RE_LYRICS_CHORDS = compile('.*\\[.*].*')
RE_BOLD = compile('(?:<bold>)(.*)(?:</bold>)')