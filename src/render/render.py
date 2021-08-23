import os
import re
from typing import Union
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
PDF_MARGIN_LEFT: float = 30
PDF_MARGIN_RIGHT: float = 30
PDF_INDENT = 20 + PDF_MARGIN_LEFT

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
RE_LYRICS_CHORDS = re.compile('.*\\[.*\\].*')
RE_BOLD = re.compile('(?:<bold>)(.*)(?:<\\/bold>)')

# NOT CURRENTLY IN USE
# meta-data directives
RE_COMMAND = re.compile('{(.*)}')
RE_START_OF_CHORUS = re.compile('(?:start_of_chorus|soc)', re.IGNORECASE)
RE_END_OF_CHORUS = re.compile('(?:end_of_chorus|eoc)', re.IGNORECASE)
RE_COMMENT_PRINTED = re.compile('c(?:omment)?:(.*)', re.IGNORECASE)
RE_COMMENT_ITALIC = re.compile('(?:comment_italic|ci):(.*)', re.IGNORECASE)
RE_COMMENT_BOX = re.compile('(?:comment_box|cb):(.*)', re.IGNORECASE)
RE_START_OF_TAB = re.compile('(?:start_of_tab|sot)', re.IGNORECASE)
RE_END_OF_TAB = re.compile('(?:end_of_tab|eot)', re.IGNORECASE)


# Create the PDF object
pdf = FPDF(orientation="portrait", unit=PDF_UNIT, format=(PDF_WIDTH, PDF_HEIGHT))
pdf.set_margins(PDF_MARGIN_LEFT, PDF_MARGIN_TOP, PDF_MARGIN_RIGHT)

# Add all the fonts we'll be using
pdf.add_font(family="Poiret One", fname=os.path.join(FONTS_DIR, 'poiret_one.ttf'), uni=True)
pdf.add_font(family="Open Sans", fname=os.path.join(FONTS_DIR, 'open_sans.ttf'), uni=True)
pdf.add_font(family="Open Sans", style='B', fname=os.path.join(FONTS_DIR, 'open_sans_bold.ttf'), uni=True)
pdf.add_font(family="Open Sans", style='I', fname=os.path.join(FONTS_DIR, 'open_sans_italic.ttf'), uni=True)


def render_song(pdf_obj: FPDF, song: Song):
    pdf_obj.set_font(BODY_FONT, '', BODY_FONT_SIZE)

    with open(os.path.join(ROOT_DIR, song.filepath), encoding="utf-8") as f:
        for line in f:
            indented = line.startswith('\t')
            line = line.strip()
            # Figure out what type of line this is
            if RE_COMMENT.match(line):
                # This is a comment - we do nothing with this
                pass
            # Check if this is a title
            elif RE_TITLE.match(line):
                string = RE_TITLE.match(line).group('args')
                pdf_obj.set_font(family=TITLE_FONT, size=TITLE_FONT_SIZE)
                pdf_obj.cell(w=0, h=TITLE_FONT_SIZE, ln=1, txt=string)
                pdf_obj.set_font(family=BODY_FONT, size=BODY_FONT_SIZE)
            # Check if this is an alternate title
            elif RE_ALT_TITLE.match(line):
                string = RE_ALT_TITLE.match(line).group('args')
                string = f"({string})"
                pdf_obj.set_font(family=ALT_TITLE_FONT, size=ALT_TITLE_FONT_SIZE)
                pdf_obj.cell(w=0, h=ALT_TITLE_FONT_SIZE, ln=1, txt=string)
                pdf_obj.set_font(family=BODY_FONT, size=BODY_FONT_SIZE)
            # Check if this is an subtitle
            elif RE_SUBTITLE.match(line):
                string = RE_SUBTITLE.match(line).group('args')
                pdf_obj.set_font(family=SUBTITLE_FONT, style=SUBTITLE_FONT_STYLE, size=SUBTITLE_FONT_SIZE)
                pdf_obj.multi_cell(w=0, h=SUBTITLE_FONT_SIZE, txt=string)
                pdf_obj.set_font(family=BODY_FONT, size=BODY_FONT_SIZE)
            # Check if this is an unsupported command
            # This doesn't fully support the ChordPro implementation, because we don't need it
            elif RE_META.match(line) or RE_COMMAND.match(line):
                print(f"Matched an unsupported command, skipping: {line}")
            # A normal line
            else:
                if indented:
                    pdf_obj.set_x(PDF_INDENT)

                if RE_BOLD.match(line):
                    pdf_obj.set_font(family=BODY_FONT, style='B', size=BODY_FONT_SIZE)
                    line = RE_BOLD.match(line).group(1)
                else:
                    pdf_obj.set_font(family=BODY_FONT, size=BODY_FONT_SIZE)

                # Check if this is a line with chords
                if RE_LYRICS_CHORDS.match(line):
                    line_words = []
                    for line_segment in re.split("(\\[.*?\\])", line):
                        # If this is a chord, we print it
                        if RE_LYRICS_CHORDS.match(line_segment):
                            chord = line_segment[1:-1]
                            width = pdf_obj.get_string_width(chord)
                            pdf_obj.set_font(family=CHORD_FONT, style=CHORD_FONT_STYLE, size=CHORD_FONT_SIZE)
                            pdf_obj.cell(w=width, h=CHORD_FONT_SIZE, txt=chord)
                            pdf_obj.set_x(pdf_obj.get_x() - width)
                            pdf_obj.set_font(family=BODY_FONT, size=BODY_FONT_SIZE)
                        else:
                            line_words.append(line_segment)
                            pdf_obj.set_x(pdf_obj.get_x() + pdf_obj.get_string_width(line_segment))

                    # Linebreak + reset the location
                    pdf_obj.ln()
                    pdf_obj.set_x(PDF_INDENT if indented else PDF_MARGIN_LEFT)
                    line = ''.join(line_words)


                # Print the line (or the line minus the chords)
                pdf_obj.multi_cell(w=0, h=BODY_FONT_SIZE, txt=line)


# Do some writing
pdf.add_page()
render_song(pdf, Song("У дику далечінь"))
pdf.output('tmp.pdf', 'F')
