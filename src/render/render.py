import os
import re
from random import random, randint

from src.consts import *
from typing import List, Dict
from fpdf import FPDF
from src.song import Song

ROOT_DIR: str = os.path.normpath("../../")
FONTS_DIR: str = os.path.join(ROOT_DIR, 'assets/fonts')

def create_pdf_obj():
    """
    Creates a basic PDF object
    @return: The PDF object
    """
    pdf_obj = FPDF(orientation="portrait", unit=PDF_UNIT, format=(PDF_WIDTH, PDF_HEIGHT))
    pdf_obj.set_margins(PDF_MARGIN_LEFT, PDF_MARGIN_TOP, PDF_MARGIN_RIGHT)
    pdf_obj.set_auto_page_break(auto=True, margin=PDF_MARGIN_BOTTOM)

    # Add all the fonts we'll be using
    pdf_obj.add_font(family="Poiret One", fname=os.path.join(FONTS_DIR, 'poiret_one.ttf'), uni=True)
    pdf_obj.add_font(family="Caveat", fname=os.path.join(FONTS_DIR, 'caveat.ttf'), uni=True)
    pdf_obj.add_font(family="Open Sans", fname=os.path.join(FONTS_DIR, 'open_sans.ttf'), uni=True)
    pdf_obj.add_font(family="Open Sans", style='B', fname=os.path.join(FONTS_DIR, 'open_sans_bold.ttf'), uni=True)
    pdf_obj.add_font(family="Open Sans", style='I', fname=os.path.join(FONTS_DIR, 'open_sans_italic.ttf'), uni=True)
    return pdf_obj


TEMP_PDF = create_pdf_obj()


def render_line(pdf: FPDF, string: str, font, font_size, font_style=''):
    """
    Renders a single line in the given style, and resets to the default body style
    @param pdf: The FPDF object on which we render this line
    @param string: The string to render
    @param font: The font family used to render this string
    @param font_size: The font size used to render this string
    @param font_style: The font style used to render this string
    @return:
    """
    pdf.set_font(family=font, style=font_style, size=font_size)
    pdf.multi_cell(w=0, h=font_size, txt=string)
    pdf.set_font(family=BODY_FONT, style=BODY_FONT_STYLE, size=BODY_FONT_SIZE)

def render_meta(pdf: FPDF, lines: List[str], dry_run=False) -> float:
    """
    Renders the given metadata information (contained in lines) on the given PDF item
    @param dry_run: If we should actually render the meta, or return the total height of these blocks
    @param pdf: The FPDF object on which we render the meta lines
    @param lines: A list containing the metadata lines
    """
    if dry_run:
        pdf = TEMP_PDF
        pdf.add_page()

    start_y = pdf.get_y()

    for line in lines:
        line = line.strip()
        # Check if it's a title
        if RE_TITLE.match(line):
            string = RE_TITLE.match(line).group('args')
            render_line(pdf, string, TITLE_FONT, TITLE_FONT_SIZE, TITLE_FONT_STYLE)
        # Check if it's an alternate title
        elif RE_ALT_TITLE.match(line):
            string = "(" + RE_ALT_TITLE.match(line).group('args') + ")"
            render_line(pdf, string, ALT_TITLE_FONT, ALT_TITLE_FONT_SIZE, ALT_TITLE_FONT_STYLE)
        # Check if this is an subtitle
        elif RE_SUBTITLE.match(line):
            string = RE_SUBTITLE.match(line).group('args')
            render_line(pdf, string, SUBTITLE_FONT, SUBTITLE_FONT_SIZE, SUBTITLE_FONT_STYLE)
        # Catch-all
        else:
            print(f"Matched an unsupported command, skipping: {line}")

    return pdf.get_y() - start_y


def render_lyrics(pdf: FPDF, lines: List[str], dry_run=False) -> Dict[str, float]:
    """
    Renders the given lyrics
    @param dry_run: If we should actually render the lyrics, or return the total height of these blocks
    @param pdf: The PDF on which we render the lyrics
    @param lines: A list of lyrics to render
    """
    if dry_run:
        pdf = TEMP_PDF
        pdf.add_page()

    # Set the default body font
    pdf.set_font(family=BODY_FONT, style=BODY_FONT_STYLE, size=BODY_FONT_SIZE)

    # Check if this song can be printed in two columns, rather than one (to save space)
    # First, find the breaks between verses
    breaks = [i for i, v in enumerate(lines) if not v.strip()]
    # Then, find the most suitable break to split the song in two
    middle_break = min(breaks, key=lambda x: abs(x - len(lines) // 2))
    # Split the lyrics into the two columns
    col1, col2 = lines[:middle_break], lines[middle_break:]

    # Calculate the dimensions of both columns
    col1_dims = _render_lyrics_one_col(TEMP_PDF, col1, True)
    col2_dims = _render_lyrics_one_col(TEMP_PDF, col2, True)


    # Check how much space we would have left if we rendered in two cols
    two_col_free_space = PAGE_WIDTH - (col1_dims['w'] + col2_dims['w'])
    # If the free space is greater than the minimum margin we want, try to render in two columns
    if two_col_free_space > MIN_COLUMN_MARGIN:
        # Find the smaller and larger column heights
        smaller_col = min(col1_dims['h'], col2_dims['h'])
        larger_col = max(col1_dims['h'], col2_dims['h'])

        # Check if this a somewhat even break (if it's too lopsided, we don't want it)
        even_break = smaller_col > (larger_col / 2)
        # Check if this song will fit onto the page
        song_fits_height = pdf.get_y() + larger_col + PDF_MARGIN_BOTTOM < PDF_HEIGHT

        # Check to see if this breaks at a good spot
        if middle_break != 0 and even_break:
            # Make sure the song fits on the page
            if song_fits_height:
                # The margin will be the largest allowable size
                margin_size = min(two_col_free_space, MAX_COLUMN_MARGIN)
                return _render_lyrics_two_col(pdf, col1, col2, dry_run, margin_size=margin_size)
            else:
                raise EOFError("Song is too long for a single page")

    # Otherwise, we stick with the default render method
    return _render_lyrics_one_col(pdf, lines, dry_run)

def _render_lyrics_two_col(pdf: FPDF, col1: List[str], col2: List[str], dry_run, margin_size) -> Dict[str, float]:
    """
    Render a song lyrics in two columns
    @param margin_size: The margin size between the two columns
    @param dry_run: If we should actually render the lyrics, or just return the height
    @param pdf: The PDF object on which to render the song
    @param col1: The first column to render
    @param col2: The second column to render
    """
    # Save the starting Y-coordinate
    start_y = pdf.get_y()
    # Render the first column
    col1_dims = _render_lyrics_one_col(pdf, col1, dry_run)
    # Save the ending Y-coordinate
    end_y = pdf.get_y()

    # Calculate the middle X-coordinate (where the line will be drawn)
    middle_x = col1_dims['w'] + PDF_MARGIN_LEFT + (margin_size / 2)

    # Reset the Y coordinate
    pdf.set_y(start_y)
    # Calculate the starting x-coordinate for the second column
    start_x = col1_dims['w'] + margin_size + PDF_MARGIN_LEFT
    # Render the second column
    col2_dims = _render_lyrics_one_col(pdf, col2, dry_run, start_x=start_x)

    # Calculate the max Y coordinate
    max_y = max(end_y, pdf.get_y())
    # Draw the dividing line
    pdf.line(middle_x, start_y, middle_x, max_y)
    # Reset the Y-coordinate to the max-Y reached
    pdf.set_y(max_y)

    return {
        'h': max(col1_dims['h'], col2_dims['h']),
        'w': col1_dims['w'] + col2_dims['w']
    }

def _render_lyrics_one_col(pdf: FPDF, lines: List[str], dry_run, start_x=PDF_MARGIN_LEFT) -> Dict[str, float]:
    """
    Renders the given lyrics in a single column
    @param pdf: The PDF object on which we render the lines
    @param dry_run: If we should actually render the lyrics, or just return the height
    @param lines: A list of lines to render
    @param start_x: The starting X coordinate of the lyrics
    """
    if dry_run:
        pdf = TEMP_PDF
        pdf.add_page()

    start_y = pdf.get_y()
    max_x = 0

    for line in lines:
        # Reset the X-coordinate for each line
        pdf.set_x(start_x)
        # Check if this line is indented, then strip all whitespace
        indented = line.startswith('\t')
        line = line.strip()

        if indented:
            pdf.set_x(start_x + PDF_INDENT)

        # Check if this line is bolded
        if RE_BOLD.match(line):
            pdf.set_font(family=BODY_FONT, style='B', size=BODY_FONT_SIZE)
            line = RE_BOLD.match(line).group(1)
        else:
            pdf.set_font(family=BODY_FONT, style=BODY_FONT_STYLE, size=BODY_FONT_SIZE)

        # Check if this is a line with chords
        if RE_LYRICS_CHORDS.match(line):
            # This is the minimum X we can write on
            # This prevents us from writing chords on top of each other
            min_x = pdf.get_x()
            line_words = []
            for line_segment in re.split("(\\[.*?])", line):
                # If this is a chord, we print it
                if RE_LYRICS_CHORDS.match(line_segment):
                    # Strip the brackets from the chord
                    chord = line_segment[1:-1]
                    # Calculate the width of the chord
                    width = pdf.get_string_width(chord)
                    # Set the chord font
                    pdf.set_font(family=CHORD_FONT, style=CHORD_FONT_STYLE, size=CHORD_FONT_SIZE)
                    # Make sure we don't write over other chords
                    pdf.set_x(max(pdf.get_x(), min_x))
                    pdf.cell(w=width, h=CHORD_FONT_SIZE, txt=chord)
                    # Update the min_x and max_x
                    min_x = pdf.get_x() + pdf.get_string_width(" ") # The MINIMUM X-coordinate we can write on
                    max_x = max(pdf.get_x(), max_x) # The MAXIMUM X-coordinate we have reached so far
                    pdf.set_x(pdf.get_x() - width)
                else:
                    pdf.set_font(family=BODY_FONT, style=BODY_FONT_STYLE, size=BODY_FONT_SIZE)
                    line_words.append(line_segment)
                    pdf.set_x(pdf.get_x() + pdf.get_string_width(line_segment))

            # Linebreak
            pdf.ln()
            line = ''.join(line_words)

        # Reset the font
        pdf.set_font(family=BODY_FONT, style=BODY_FONT_STYLE, size=BODY_FONT_SIZE)
        # Reset the X position (in case of chords)
        pdf.set_x(start_x + (PDF_INDENT if indented else 0))
        # Update the max X position
        max_x = max(pdf.get_string_width(line) + pdf.get_x(), max_x)
        # If we have an empty line, the width is 0 - which means unlimited. Instead, we want a small width
        string_width = max(pdf.get_string_width(line), 0.1)
        # Print the line (or the line minus the chords)
        pdf.cell(w=string_width, h=BODY_FONT_SIZE, ln=1, txt=line)



    return {
        'h': pdf.get_y() - start_y,
        'w': max_x - start_x,
    }


def render_song(pdf: FPDF, song: Song) -> int:
    """
    Renders the given Song object on the given FPDF object
    @param pdf: The FPDF object on which we render this song
    @param song: The Song object which we render
    @return: The page number on which this song starts
    """
    meta = []
    lyrics = []

    with open(os.path.join(ROOT_DIR, song.filepath), encoding="utf-8") as f:
        for line in f:
            # Check if this line is a comment (we skip it)
            if RE_COMMENT.match(line):
                pass
            # Check if it's a title, alt_title, or subtitle
            elif RE_TITLE.match(line) or RE_ALT_TITLE.match(line) or RE_SUBTITLE.match(line):
                meta.append(line)
            # Check if it's an unsupported command (ie. one I didn't implement because I don't use it)
            elif RE_META.match(line):
                print(f"Matched an unsupported command, skipping: {line}")
            # A normal line
            else:
                lyrics.append(line)

    try:
        meta_height = render_meta(pdf, meta, True)
        lyric_dims = render_lyrics(pdf, lyrics, True)
    except EOFError:
        print(f"Song {song.title} is too long to render")
        return

    lyric_height = lyric_dims['h']
    # Check if this song can be rendered on the current page - if not, add another
    if meta_height + lyric_height > (PDF_HEIGHT - (pdf.get_y() + PDF_MARGIN_BOTTOM)):
        pdf.add_page()

    page_no = pdf.page_no()
    render_meta(pdf, meta)      # Render the metadata of this song
    render_lyrics(pdf, lyrics)  # Render the lyrics of this song

    return page_no


def render_pdf():
    # Create the PDF object
    pdf_obj = create_pdf_obj()

    # Do some writing
    pdf_obj.add_page()


    render_song(pdf_obj, Song("Вогов"))

    songs = ["Купала на Івана",
             "Надія є",
             "Пройшли мандрування",
             "Розпрягайте, хлопці, коні",
             "Роксоляна",
             "У дику далечінь",
             "Чабан",
             "Чорні очка",
             "Ще не вмерлa Укрaїнa",
             "гімн пласту"]

    for song in songs:
        pdf_obj.set_y(pdf_obj.get_y() + SONG_MARGIN)
        print(render_song(pdf_obj, Song(song)))



    pdf_obj.output('tmp.pdf', 'F')


render_pdf()
