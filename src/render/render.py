import os
import re
from typing import Union, List
from fpdf import FPDF
from src.song import Song

# Directory variables
ROOT_DIR: str = os.path.normpath("../../")
FONTS_DIR = os.path.join(ROOT_DIR, 'assets/fonts')

# PDF setup variables
PDF_UNIT: str = "pt"  # pt, mm, cm, in
PDF_WIDTH: Union[float, int] = 396  # The width of the page in PDF_UNIT
PDF_HEIGHT: Union[float, int] = 612  # The height of the page in PDF_UNIT
# Margins
PDF_MARGIN_TOP: float = 30
PDF_MARGIN_LEFT: float = 28
PDF_MARGIN_RIGHT: float = 28
PDF_INDENT = 20 + PDF_MARGIN_LEFT
COLUMN_MARGIN = 10

PAGE_WIDTH = PDF_WIDTH - (PDF_MARGIN_RIGHT + PDF_MARGIN_LEFT)

# Font variables
BODY_FONT = "Open Sans"
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
    return re.compile(f'^{{(?:meta:)?\\s*(?P<command>{command}):?\\s*(?P<args>.*)}}')


RE_COMMENT = re.compile('^#(.*)')
RE_TITLE = regex_meta("title")
RE_SUBTITLE = regex_meta("subtitle")
RE_ALT_TITLE = regex_meta("alt_title")
RE_META = regex_meta(".*")
RE_LYRICS_CHORDS = re.compile('.*\\[.*].*')
RE_BOLD = re.compile('(?:<bold>)(.*)(?:</bold>)')


# Create the PDF object
pdf_obj = FPDF(orientation="portrait", unit=PDF_UNIT, format=(PDF_WIDTH, PDF_HEIGHT))
pdf_obj.set_margins(PDF_MARGIN_LEFT, PDF_MARGIN_TOP, PDF_MARGIN_RIGHT)

# Add all the fonts we'll be using
pdf_obj.add_font(family="Poiret One", fname=os.path.join(FONTS_DIR, 'poiret_one.ttf'), uni=True)
pdf_obj.add_font(family="Open Sans", fname=os.path.join(FONTS_DIR, 'open_sans.ttf'), uni=True)
pdf_obj.add_font(family="Open Sans", style='B', fname=os.path.join(FONTS_DIR, 'open_sans_bold.ttf'), uni=True)
pdf_obj.add_font(family="Open Sans", style='I', fname=os.path.join(FONTS_DIR, 'open_sans_italic.ttf'), uni=True)


def render_meta(pdf: FPDF, lines: List[str]):
    for line in lines:
        line = line.strip()

        # Check if it's a title
        if RE_TITLE.match(line):
            string = RE_TITLE.match(line).group('args')
            render_line(pdf, string, TITLE_FONT, TITLE_FONT_SIZE)
        # Check if it's an alternate title
        elif RE_ALT_TITLE.match(line):
            string = "(" + RE_ALT_TITLE.match(line).group('args') + ")"
            render_line(pdf, string, ALT_TITLE_FONT, ALT_TITLE_FONT_SIZE)
        # Check if this is an subtitle
        elif RE_SUBTITLE.match(line):
            string = RE_SUBTITLE.match(line).group('args')
            render_line(pdf, string, SUBTITLE_FONT, SUBTITLE_FONT_SIZE, SUBTITLE_FONT_STYLE)
        # Catch-all
        else:
            print(f"Matched an unsupported command, skipping: {line}")


def render_lyrics(pdf: FPDF, lines: List[str]):
    pdf.set_font(family=BODY_FONT, size=BODY_FONT_SIZE)
    trimmed_lines = (re.sub('\\[.*?]', '', line) for line in lines)
    max_width = max(pdf.get_string_width(line) for line in trimmed_lines)

    if max_width + COLUMN_MARGIN < (PAGE_WIDTH // 2):
        pass
    else:
        render_lyrics_one_col(pdf, lines)


def render_lyrics_one_col(pdf: FPDF, lines: List[str]):
    for line in lines:
        indented = line.startswith('\t')
        line = line.strip()

        if indented:
            pdf.set_x(PDF_INDENT)

        if RE_BOLD.match(line):
            pdf.set_font(family=BODY_FONT, style='B', size=BODY_FONT_SIZE)
            line = RE_BOLD.match(line).group(1)
        else:
            pdf.set_font(family=BODY_FONT, size=BODY_FONT_SIZE)

        # Check if this is a line with chords
        if RE_LYRICS_CHORDS.match(line):
            line_words = []
            for line_segment in re.split("(\\[.*?])", line):
                # If this is a chord, we print it
                if RE_LYRICS_CHORDS.match(line_segment):
                    chord = line_segment[1:-1]
                    width = pdf.get_string_width(chord)
                    pdf.set_font(family=CHORD_FONT, style=CHORD_FONT_STYLE, size=CHORD_FONT_SIZE)
                    pdf.cell(w=width, h=CHORD_FONT_SIZE, txt=chord)
                    pdf.set_x(pdf.get_x() - width)
                    pdf.set_font(family=BODY_FONT, size=BODY_FONT_SIZE)
                else:
                    line_words.append(line_segment)
                    pdf.set_x(pdf.get_x() + pdf.get_string_width(line_segment))

            # Linebreak + reset the location
            pdf.ln()
            pdf.set_x(PDF_INDENT if indented else PDF_MARGIN_LEFT)
            line = ''.join(line_words)

        # Print the line (or the line minus the chords)
        pdf.multi_cell(w=0, h=BODY_FONT_SIZE, txt=line)

def render_song(pdf: FPDF, song: Song):
    meta = []
    lyrics = []

    with open(os.path.join(ROOT_DIR, song.filepath), encoding="utf-8") as f:
        for line in f:
            # Figure out what type of line this is
            if RE_COMMENT.match(line):  # Check if it's a comment (if so, we ignore it)
                pass
            # Check if it's a title, alt, or subtitle
            elif RE_TITLE.match(line) or RE_ALT_TITLE.match(line) or RE_SUBTITLE.match(line):
                meta.append(line)
            # Check if it's a different command (one that isn't supported bc I don't use it)
            elif RE_META.match(line):
                print(f"Matched an unsupported command, skipping: {line}")
            # A normal line
            else:
                lyrics.append(line)

    render_meta(pdf, meta)
    render_lyrics(pdf, lyrics)


def render_line(pdf: FPDF, string: str, font, font_size, font_style=''):
    pdf.set_font(family=font, style=font_style, size=font_size)
    pdf.multi_cell(w=0, h=font_size, txt=string)
    pdf.set_font(family=BODY_FONT, size=BODY_FONT_SIZE)


# Do some writing
pdf_obj.add_page()
render_song(pdf_obj, Song("Бий Барабан"))
pdf_obj.output('tmp.pdf', 'F')
