import os
import re

from render_vars import *
from typing import List, Optional, Dict
from fpdf import FPDF
from src.song import Song

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

def render_meta(pdf: FPDF, lines: List[str], dry_run=False) -> Optional[float]:
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

    if dry_run:
        return pdf.get_y() - start_y


def render_lyrics(pdf: FPDF, lines: List[str], dry_run=False) -> Optional[float]:
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
    # Calculate the max width of the lyrics
    song_dims = render_lyrics_one_col(TEMP_PDF, lines, True)
    max_width = song_dims['w']

    # If we have the room to render in two lines, we do so
    song_fits_width = max_width + COLUMN_MARGIN < (PAGE_WIDTH // 2)
    if song_fits_width:
        # Find the breaks between verses
        breaks = [i for i, v in enumerate(lines) if not v.strip()]
        middle_break = min(breaks, key=lambda x: abs(x - len(lines) // 2))

        col1, col2 = lines[:middle_break], lines[middle_break:]

        # Calculate the max height, and see if it fits in the page
        col1_height = render_lyrics_one_col(TEMP_PDF, col1, True)['h']
        col2_height = render_lyrics_one_col(TEMP_PDF, col2, True)['h']
        height = max(col1_height, col2_height)
        song_fits_height = pdf.get_y() + height + PDF_MARGIN_BOTTOM < PDF_HEIGHT

        if middle_break != 0:
            if song_fits_height:
                return render_lyrics_two_col(pdf, col1, col2, dry_run)
            else:
                raise EOFError("Song is too long for a single page")
        # Otherwise, we stick with the default render method

    return render_lyrics_one_col(pdf, lines, dry_run)

def render_lyrics_two_col(pdf: FPDF, col1: List[str], col2: List[str], dry_run) -> Optional[Dict[str, float]]:
    """
    Render a song lyrics in two columns
    @param dry_run: If we should actually render the lyrics, or just return the height
    @param pdf: The PDF object on which to render the song
    @param col1: The first column to render
    @param col2: The second column to render
    """
    # Save the starting point of the left column
    start_y = pdf.get_y()
    render_lyrics_one_col(pdf, col1, dry_run)
    end_y = pdf.get_y()

    col1_dims = render_lyrics_one_col(pdf, col1, True)
    left_width = col1_dims['w']
    # Draw a dividing line
    middle_x = left_width + PDF_MARGIN_LEFT + (COLUMN_MARGIN / 2)

    pdf.set_y(start_y)
    start_x = left_width + COLUMN_MARGIN + PDF_MARGIN_LEFT
    render_lyrics_one_col(pdf, col2, dry_run, start_x=start_x)

    col2_dims = render_lyrics_one_col(pdf, col2, True, start_x=start_x)

    bottom_x = max(end_y, pdf.get_y())
    # Draw a dividing line
    pdf.line(middle_x, start_y, middle_x, bottom_x)
    pdf.set_y(bottom_x)

    if dry_run:
        return {
            'h': max(col1_dims['h'], col2_dims['h']),
            'w': col1_dims['w'] + col2_dims['w']
        }

def render_lyrics_one_col(pdf: FPDF, lines: List[str], dry_run, start_x=PDF_MARGIN_LEFT) -> Optional[Dict[str, float]]:
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
        pdf.set_x(start_x)
        indented = line.startswith('\t')
        line = line.strip()

        if indented:
            pdf.set_x(start_x + PDF_INDENT)

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
                    chord = line_segment[1:-1]
                    width = pdf.get_string_width(chord)
                    pdf.set_font(family=CHORD_FONT, style=CHORD_FONT_STYLE, size=CHORD_FONT_SIZE)
                    # Make sure we don't write over other chords
                    pdf.set_x(max(pdf.get_x(), min_x))
                    pdf.cell(w=width, h=CHORD_FONT_SIZE, txt=chord)
                    # Update the min_x and max_x
                    min_x = pdf.get_x() + pdf.get_string_width(" ")
                    max_x = max(pdf.get_x(), max_x)
                    pdf.set_x(pdf.get_x() - width)
                    pdf.set_font(family=BODY_FONT, style=BODY_FONT_STYLE, size=BODY_FONT_SIZE)
                else:
                    line_words.append(line_segment)
                    pdf.set_x(pdf.get_x() + pdf.get_string_width(line_segment))

            # Linebreak
            pdf.ln()
            line = ''.join(line_words)

        # Reset the X position (in case of chords)
        pdf.set_x(start_x + (PDF_INDENT if indented else 0))
        # Update the max X position
        max_x = max(pdf.get_string_width(line) + pdf.get_x(), max_x)
        # If we have an empty line, the width is 0 - which means unlimited. Instead, we want a small width
        string_width = max(pdf.get_string_width(line), 0.1)
        # Print the line (or the line minus the chords)
        pdf.cell(w=string_width, h=BODY_FONT_SIZE, ln=1, txt=line)



    if dry_run:
        return {
            'h': pdf.get_y() - start_y,
            'w': max_x - start_x,
        }


def render_song(pdf: FPDF, song: Song) -> None:
    """
    Renders the given Song object on the given FPDF object
    @param pdf: The FPDF object on which we render this song
    @param song: The Song object which we render
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
    except EOFError as e:
        print(f"Song {song.title} is too long to render")
        return

    lyric_height = lyric_dims['h']
    # Check if this song can be rendered on the current page - if not, add another
    if meta_height + lyric_height > (PDF_HEIGHT - (pdf.get_y() + PDF_MARGIN_BOTTOM)):
        pdf.add_page()

    render_meta(pdf, meta)      # Render the metadata of this song
    render_lyrics(pdf, lyrics)  # Render the lyrics of this song




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
        render_song(pdf_obj, Song(song))



    pdf_obj.output('tmp.pdf', 'F')


render_pdf()
