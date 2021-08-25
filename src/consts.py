import os
from re import compile

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


# WikiSpiv URL endpoints
WIKI_ROOT_URL = "https://www.wikispiv.com"  # The root WikiSpiv domain
WIKI_SONG_URL = f"{WIKI_ROOT_URL}/wiki"     # The root wiki location (ie. the level at which songs are)
WIKI_API_URL = f"{WIKI_ROOT_URL}/api.php?format=json"   # The API endpoint


# FPDF constants
PDF_UNIT: str = "pt"  # The unit used for measurements - pt, mm, cm, in
PDF_WIDTH: float = 5.5 * 72      # The width of the page (including margins)
PDF_HEIGHT: float = 8.5 * 72     # The height of the page (including margins)
# PDF margins
PDF_MARGIN_TOP: float = 30
PDF_MARGIN_LEFT: float = 28
PDF_MARGIN_RIGHT: float = 28
PDF_MARGIN_BOTTOM: float = 28
PDF_INDENT = 20         # The size of a paragraph indent
MIN_COLUMN_MARGIN = 15  # The minimum margin between columns
MAX_COLUMN_MARGIN = 30  # The maximum margin between columns
MIN_SONG_HEIGHT = 80   # The minimum height for each column
MIN_IMAGE_HEIGHT = 150  # THe minimum height for an image at the bottom of the page
# If we don't have at least this much space, we evenly spread the songs out to use up that space.
#   No point in leaving that space unused if it's smaller than this
SONG_MARGIN = 20        # Horizontal margin between songs
# The dimensions of the usable page (ie. not counting margins)
USABLE_PAGE_WIDTH = PDF_WIDTH - (PDF_MARGIN_RIGHT + PDF_MARGIN_LEFT)
USABLE_PAGE_HEIGHT = PDF_HEIGHT - (PDF_MARGIN_BOTTOM + PDF_MARGIN_TOP)

# Font variables
BODY_FONT = "Open Sans"
BODY_FONT_STYLE = ""
BODY_FONT_SIZE = 10
BODY_COLOR = (0, 0, 0)

TITLE_FONT = "Poiret One"
TITLE_FONT_STYLE = ""
TITLE_FONT_SIZE = 20

ALT_TITLE_FONT = TITLE_FONT
ALT_TITLE_FONT_STYLE = ""
ALT_TITLE_FONT_SIZE = 14

SUBTITLE_FONT = BODY_FONT
SUBTITLE_FONT_STYLE = "I"
SUBTITLE_FONT_SIZE = 8

CHORD_FONT = BODY_FONT
CHORD_FONT_STYLE = "B"
CHORD_FONT_SIZE = 8
CHORD_COLOR = (25, 25, 25)

INDEX_TITLE_FONT = "Open Sans"
INDEX_TITLE_STYLE = "B"
INDEX_TITLE_SIZE = 10

INDEX_SONG_FONT = "Open Sans"
INDEX_SONG_STYLE = ""
INDEX_SONG_SIZE = 9
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
RE_META = regex_meta(".*")
RE_LYRICS_CHORDS = compile('.*\\[.*].*')
RE_BOLD = compile('(?:<bold>)(.*)(?:</bold>)')