import re
from pyuca import Collator
from src.consts import *
from typing import List, Dict, Tuple, Optional
from fpdf import FPDF
from src.song import Song

from tqdm import tqdm

FONTS_DIR: str = os.path.normpath(os.path.join(ROOT_DIR, 'assets/fonts'))
SONG_DIR: str = os.path.normpath(os.path.join(ROOT_DIR, 'songs'))


class PDF(FPDF):
    def footer(self):
        # Go to 15 pt from bottom
        self.set_y(-20)
        # Select Arial italic 8
        self.set_font(BODY_FONT, '', 12)
        # Print centered page number
        self.cell(0, 10, f'- {self.page_no()} -', 0, 0, 'C')


def create_pdf_obj():
    """
    Creates a basic PDF object
    @return: The PDF object
    """
    pdf_obj = PDF(orientation="portrait", unit=PDF_UNIT, format=(PDF_WIDTH, PDF_HEIGHT))
    pdf_obj.set_margins(PDF_MARGIN_LEFT, PDF_MARGIN_TOP, PDF_MARGIN_RIGHT)
    pdf_obj.set_auto_page_break(auto=True, margin=PDF_MARGIN_BOTTOM)

    # Add all the fonts we'll be using
    path = os.path.join(FONTS_DIR, 'poiret_one.ttf')

    pdf_obj.add_font(family="Poiret One", fname=path, uni=True)
    pdf_obj.add_font(family="Caveat", fname=os.path.join(FONTS_DIR, 'caveat.ttf'), uni=True)
    pdf_obj.add_font(family="Open Sans", fname=os.path.join(FONTS_DIR, 'open_sans.ttf'), uni=True)
    pdf_obj.add_font(family="Open Sans", style='B', fname=os.path.join(FONTS_DIR, 'open_sans_bold.ttf'), uni=True)
    pdf_obj.add_font(family="Open Sans", style='I', fname=os.path.join(FONTS_DIR, 'open_sans_italic.ttf'), uni=True)
    return pdf_obj


TEMP_PDF = create_pdf_obj()


def render_line(pdf: PDF, string: str, font, font_size, font_style=''):
    """
    Renders a single line in the given style, and resets to the default body style
    @param pdf: The PDF object on which we render this line
    @param string: The string to render
    @param font: The font family used to render this string
    @param font_size: The font size used to render this string
    @param font_style: The font style used to render this string
    @return:
    """
    pdf.set_font(family=font, style=font_style, size=font_size)
    pdf.multi_cell(w=0, h=font_size, txt=string)
    pdf.set_font(family=BODY_FONT, style=BODY_FONT_STYLE, size=BODY_FONT_SIZE)


def render_meta(pdf: PDF, lines: List[str], dry_run=False) -> float:
    """
    Renders the given metadata information (contained in lines) on the given PDF item
    @param dry_run: If we should actually render the meta, or return the total height of these blocks
    @param pdf: The PDF object on which we render the meta lines
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


def render_lyrics(pdf: PDF, lines: List[str], dry_run=False) -> Dict[str, float]:
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
    start_y = pdf.get_y()
    col1_dims = _render_lyrics_one_col(TEMP_PDF, col1, True)
    col2_dims = _render_lyrics_one_col(TEMP_PDF, col2, True)
    pdf.set_y(start_y)

    # Check how much space we would have left if we rendered in two cols
    two_col_free_space = USABLE_PAGE_WIDTH - (col1_dims['w'] + col2_dims['w'])
    # If the free space is greater than the minimum margin we want, try to render in two columns
    if two_col_free_space > MIN_COLUMN_MARGIN:
        # Find the larger column heights
        larger_col = max(col1_dims['h'], col2_dims['h'])

        # Check if this song will fit onto the page
        song_fits_height = pdf.get_y() + larger_col + PDF_MARGIN_BOTTOM <= PDF_HEIGHT

        # Check to see if this breaks at a good spot
        if middle_break != 0 and (col1_dims['h'] > MIN_SONG_HEIGHT and col2_dims['h'] > MIN_SONG_HEIGHT):
            # Make sure the song fits on the page
            if song_fits_height:
                # The margin will be the largest allowable size
                margin_size = min(two_col_free_space, MAX_COLUMN_MARGIN)
                return _render_lyrics_two_col(pdf, col1, col2, dry_run, margin_size=margin_size)
            else:
                raise EOFError("Song is too long for a single page")

    # Otherwise, we stick with the default render method
    return _render_lyrics_one_col(pdf, lines, dry_run)


def _render_lyrics_two_col(pdf: PDF, col1: List[str], col2: List[str], dry_run, margin_size) -> Dict[str, float]:
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


def _render_lyrics_one_col(pdf: PDF, lines: List[str], dry_run, start_x=PDF_MARGIN_LEFT) -> Dict[str, float]:
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
            pdf.set_font(family=BODY_FONT, style='UI', size=BODY_FONT_SIZE)
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
                    pdf.set_text_color(*CHORD_COLOR)
                    # Make sure we don't write over other chords
                    pdf.set_x(max(pdf.get_x(), min_x))
                    pdf.cell(w=width, h=CHORD_FONT_SIZE, txt=chord)
                    # Update the min_x and max_x
                    min_x = pdf.get_x() + pdf.get_string_width(" ")  # The MINIMUM X-coordinate we can write on
                    max_x = max(pdf.get_x(), max_x)  # The MAXIMUM X-coordinate we have reached so far
                    pdf.set_x(pdf.get_x() - width)
                    pdf.set_font(family=BODY_FONT, style=BODY_FONT_STYLE, size=BODY_FONT_SIZE)
                    pdf.set_text_color(*BODY_COLOR)
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

    return {
        'h': pdf.get_y() - start_y,
        'w': max_x - start_x,
    }


def render_song(pdf: PDF, song: Song) -> Optional[Tuple[str, List[str], int]]:
    """
    Renders the given Song object on the given PDF object
    @param pdf: The PDF object on which we render this song
    @param song: The Song object which we render
    @return: The title of this song, the alternate titles, and the page number on which this song starts
    """
    meta = []
    lyrics = []
    song_title = ""
    song_alt_titles = []

    with open(os.path.join(SONG_DIR, song.filename), encoding="utf-8") as f:
        for line in f:
            # Check if this line is a comment (we skip it)
            if RE_COMMENT.match(line):
                pass
            # Check if it's a title, alt_title, or subtitle
            elif RE_TITLE.match(line):
                meta.append(line)
                song_title = RE_TITLE.match(line).group('args')
            elif RE_ALT_TITLE.match(line):
                meta.append(line)
                song_alt_titles.append(RE_ALT_TITLE.match(line).group('args'))
            elif RE_SUBTITLE.match(line):
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
        return None

    song_height = meta_height + lyric_dims['h']
    # Check if this song can be rendered on the current page - if not, add another
    if song_height > (PDF_HEIGHT - (pdf.get_y() + PDF_MARGIN_BOTTOM)):
        pdf.add_page()

    # Here, we calculate if there would be enough room at the bottom of the page to render an image.
    #   If not - we spread the songs out instead
    free_space = PDF_HEIGHT - (pdf.get_y() + song_height) - PDF_MARGIN_BOTTOM
    # If we don't have enough space, AND this song isn't the first on the page
    if free_space <= MIN_IMAGE_HEIGHT and pdf.get_y() != PDF_MARGIN_TOP:
        page_bottom = PDF_HEIGHT - PDF_MARGIN_BOTTOM - (free_space / 2)
        # Bump the song down to the bottom
        pdf.set_y(page_bottom - song_height)


    page_no = pdf.page_no()
    render_meta(pdf, meta)  # Render the metadata of this song
    render_lyrics(pdf, lyrics)  # Render the lyrics of this song

    return song_title, song_alt_titles, page_no


def render_songs(pdf: PDF, songs: List[Song], sort_by_name) -> List[Tuple[str, int]]:
    """
    Renders all of the songs in a section
    @param pdf: The PDF object on which to render the songs
    @param songs: A list of the SOng objects
    @param sort_by_name: Whether we sort the songs by their name or not
    @return: A list of tuples containing the song name and page number
    """
    page_numbers = []

    first = True
    for song in tqdm(songs):
        if not first:
            pdf.set_y(pdf.get_y() + SONG_MARGIN)
        else:
            first = False

        out = render_song(pdf, song)
        if not out:
            continue

        title, alt_titles, page_no = out

        page_numbers.append((title, page_no))

        if sort_by_name:
            # We only bother adding the alternate titles if we sort by name
            #   Otherwise, what's the point? The alt titles would be right below the main one anyways
            for alt in alt_titles:
                txt = f"{alt} (під '{title}')"
                page_numbers.append((txt, page_no))

    if sort_by_name:
        c = Collator()
        return sorted(page_numbers, key=lambda x: c.sort_key(x[0]))

    return page_numbers


def render_index(pdf: PDF, sections: List[Tuple[str, List[Tuple[str, int]]]]) -> None:
    """
    Renders the index of this songbook
    @param pdf: The PDF on which we render the index
    @param sections: The sections of the index - each section has a (name, List[(song_name, song_page_number)])
    """
    pdf.add_page()
    render_line(pdf, "Індекс", TITLE_FONT, TITLE_FONT_SIZE, TITLE_FONT_STYLE)

    pdf.set_font(INDEX_SONG_FONT, INDEX_SONG_STYLE, INDEX_SONG_SIZE)
    # Figure out how much space we need for numbers (if your pages go higher, we've got other issues)
    number_width = pdf.get_string_width("1234567")
    text_width = USABLE_PAGE_WIDTH - number_width
    text_height = INDEX_SONG_SIZE + INDEX_SONG_PADDING

    for section in sections:
        # Write the section header
        pdf.set_font(INDEX_TITLE_FONT, INDEX_TITLE_STYLE, INDEX_TITLE_SIZE)
        pdf.ln()
        pdf.multi_cell(w=0, h=INDEX_TITLE_SIZE, txt=section[0])
        pdf.set_font(INDEX_SONG_FONT, INDEX_SONG_STYLE, INDEX_SONG_SIZE)
        pdf.ln()
        # Write all the songs in the section
        for song, page in section[1]:
            start_y = pdf.get_y()
            # Check if this line will go around to the next page
            if start_y + text_height + PDF_MARGIN_BOTTOM > PDF_HEIGHT:
                start_y = PDF_MARGIN_TOP

            # Write the song title
            pdf.multi_cell(w=text_width, h=text_height, border='B', txt=song)
            end_y = pdf.get_y()
            # Update the XY, so we write the number next to the title
            pdf.set_xy(text_width + PDF_MARGIN_LEFT, start_y)
            # Write the page number (make sure height matches that of the title).
            pdf.multi_cell(w=number_width, h=end_y-start_y, border='B', align='C', txt=str(page))
            # Update the y-coordinate to be the larger of the two
            pdf.set_y(max(pdf.get_y(), end_y))



def render_pdf(sections: List[Tuple[str, List[Song], bool]], outfile: str):
    """
    Renders our songbook.
    @param outfile: The location of the resulting PDF
    @param sections: The sections of the songbook. A section is List[(section_name, List[songs], sort_sec_by_name?)]
    """
    # Create the PDF object
    pdf_obj = create_pdf_obj()

    # Do some writing
    pdf_obj.add_page()

    section_indexes = []

    for name, songs, sort_by_name in sections:
        print(f"Section '{name}'", flush=True)
        index = render_songs(pdf_obj, songs, sort_by_name)
        section_indexes.append((name, index))

    render_index(pdf_obj, section_indexes)
    pdf_obj.output(outfile, 'F')
