import os
import re
import string
from typing import List, Dict, Tuple, Optional, Set

from fpdf import FPDF
from pyuca import Collator
from tqdm import tqdm

from consts import Config, Font
from song import Song, SongInfo

FONTS_DIR: str = os.path.normpath(os.path.join(Config.ROOT_DIR, 'assets/fonts'))



class PDF(FPDF):
    def __init__(self):
        # Create the FPDF instance and configure it
        super().__init__(orientation="portrait", unit=Config.PDF_UNIT, format=(Config.PDF_WIDTH, Config.PDF_HEIGHT))
        self.set_margins(Config.PDF_MARGIN_LEFT, Config.PDF_MARGIN_TOP, Config.PDF_MARGIN_RIGHT)
        self.set_auto_page_break(auto=True, margin=Config.PDF_MARGIN_BOTTOM)
        self.add_page()

        # Add all the fonts we'll be using
        self.add_font(family="Poiret One", fname=os.path.join(FONTS_DIR, 'poiret_one.ttf'), uni=True)
        self.add_font(family="Caveat", fname=os.path.join(FONTS_DIR, 'caveat.ttf'), uni=True)
        self.add_font(family="Open Sans", fname=os.path.join(FONTS_DIR, 'open_sans.ttf'), uni=True)
        self.add_font(family="Open Sans", style='B', fname=os.path.join(FONTS_DIR, 'open_sans_bold.ttf'), uni=True)
        self.add_font(family="Open Sans", style='I', fname=os.path.join(FONTS_DIR, 'open_sans_italic.ttf'), uni=True)
        self.add_font(family="Futura Futuris C", fname=os.path.join(FONTS_DIR, 'futura_futuris_c.ttf'), uni=True)
        self.add_font(family="Futura Futuris C", style='B', fname=os.path.join(FONTS_DIR, 'futura_futuris_c_bold.ttf'), uni=True)
        self.add_font(family="Futura Futuris C", style='I', fname=os.path.join(FONTS_DIR, 'futura_futuris_c_italic.ttf'), uni=True)
        self.add_font(family="Futura Futuris C Light", fname=os.path.join(FONTS_DIR, 'futura_futuris_c_light.ttf'), uni=True)
        self.add_font(family="Ubuntu", fname=os.path.join(FONTS_DIR, 'ubuntu.ttf'), uni=True)
        self.add_font(family="Ubuntu", style='I', fname=os.path.join(FONTS_DIR, 'ubuntu_italic.ttf'), uni=True)
        self.add_font(family="Ubuntu", style='B', fname=os.path.join(FONTS_DIR, 'ubuntu_bold.ttf'), uni=True)
        self.add_font(family="Ubuntu Light", fname=os.path.join(FONTS_DIR, 'ubuntu_light.ttf'), uni=True)
        self.add_font(family="Ubuntu Light", style="B", fname=os.path.join(FONTS_DIR, 'ubuntu.ttf'), uni=True)

        # Some basic config variables
        self.index_number_width = None
        self.index_text_width = None
        self.index_text_height = None

    def get_index_number_width(self) -> float:
        if not self.index_number_width:
            self.index_number_width = self.get_string_width("1234567")

        return self.index_number_width

    def get_index_text_width(self) -> float:
        if not self.index_text_width:
            self.index_text_width = Config.USABLE_PAGE_WIDTH - self.get_index_number_width()

        return self.index_text_width

    def get_index_text_height(self) -> float:
        if not self.index_text_height:
            self.index_text_height = Config.INDEX_SONG_FONT["size"] + Config.INDEX_SONG_PADDING

        return self.index_text_height

    def footer(self):
        self.set_y(-20)
        self.set_font(Config.BODY_FONT["family"], '', Config.BODY_FONT["size"])
        self.cell(0, 10, f'- {self.page_no()} -', 0, 0, 'C')

    def render_line(self, string: str, font: Font) -> None:
        """
        Renders a single line in the given style, and resets to the default body style
        @param string: The string to render
        @param font: The font object used to render this string
        """
        self.set_font_obj(font)
        self.multi_cell(w=0, h=font["size"], txt=string)
        self.set_font_obj(Config.BODY_FONT)

    def set_font_obj(self, font: Font, color=None) -> None:
        """
        Sets the font using a Font object
        @param color: An optional color parameter
        @param font: The Font to set
        """
        if color:
            self.set_text_color(*color)
        self.set_font(family=font["family"], style=font["style"], size=font["size"])

    def render_meta(self, lines: List[str], dry_run=False) -> float:
        """
        Renders the given metadata information (contained in lines) on the given PDF item
        @param dry_run: If we should actually render the meta, or return the total height of these blocks
        @param lines: A list containing the metadata lines
        """
        # If this is a dry run, we use a temporary PDF object
        if dry_run:
            pdf = TEMP_PDF
            pdf.add_page()
        else:
            pdf = self

        start_y = pdf.get_y()

        for line in lines:
            line = line.strip()
            # Check if it's a title
            if Config.RE_TITLE.match(line):
                line = Config.RE_TITLE.match(line).group('args')
                pdf.render_line(line, Config.TITLE_FONT)
            # Check if it's an alternate title
            elif Config.RE_ALT_TITLE.match(line):
                pass
                # line = "(" + Config.RE_ALT_TITLE.match(line).group('args') + ")"
                # pdf.render_line(line, Config.ALT_TITLE_FONT)
            # Check if this is an subtitle
            elif Config.RE_SUBTITLE.match(line):
                line = Config.RE_SUBTITLE.match(line).group('args')
                pdf.render_line(line, Config.SUBTITLE_FONT)
            # Catch-all
            else:
                print(f"Matched an unsupported command, skipping: {line}")


        return pdf.get_y() - start_y


    def render_lyrics(self, lines: List[str], dry_run=False) -> Dict[str, float]:
        """
        Renders the given lyrics
        @param dry_run: If we should actually render the lyrics, or return the total height of these blocks
        @param lines: A list of lyrics to render
        """
        # If this is a dry run, we use a temporary PDF object
        if dry_run:
            pdf = TEMP_PDF
            pdf.add_page()
        else:
            pdf = self

        # Set the default body font
        pdf.set_font_obj(Config.BODY_FONT)

        two_cols = self._split_song(lines)

        if two_cols:
            col1, col2 = two_cols
            margin = pdf._two_col_margin(col1, col2)
            if margin > 0:
                return pdf._render_lyrics_two_col(col1, col2, margin)

        # Otherwise, we stick with the default render method
        return pdf._render_lyrics_one_col(lines)

    @staticmethod
    def _split_song(lines: List[str]) -> Optional[Tuple[List[str], List[str]]]:
        """
        Splits a given song into two columns (if possible)
        @param lines: The lines of the song
        @return: Two lists representing the two columns, or None if a break is not possible
        """
        # First - find the indexes of every linebreak in the song
        breaks = [i for i, v in enumerate(lines) if not v.strip()]

        if len(breaks) == 0:
            return

        # Then, find the most suitable break to split the song in two
        middle_break = min(breaks, key=lambda x: abs(x - 1 - len(lines) // 2))

        # Split the lyrics into the two columns
        return lines[:middle_break], lines[middle_break+1:]

    def _two_col_margin(self, col1: List[str], col2: List[str]):
        """
        Calculates the horizontal margin between the two columns
        @param col1: The first column
        @param col2: The second column
        @return: The horizontal margin, or -1 if the two columns do not fit all the requirements (eg. are shorter than
            the minimum height, are too wide, etc).
        """
        # Calculate the dimensions of both columns
        start_y = self.get_y()
        TEMP_PDF.add_page()
        col1_dims = TEMP_PDF._render_lyrics_one_col(col1)
        TEMP_PDF.add_page()
        col2_dims = TEMP_PDF._render_lyrics_one_col(col2)
        self.set_y(start_y)

        # Check how much space we would have left if we rendered in two cols
        space_left = Config.USABLE_PAGE_WIDTH - (col1_dims['w'] + col2_dims['w'])
        enough_space_left = space_left >= Config.MIN_COLUMN_MARGIN

        # Check if both columns are at least the minimum height
        cols_match_min_height = (col1_dims['h'] > Config.MIN_SONG_HEIGHT and col2_dims['h'] > Config.MIN_SONG_HEIGHT)

        # Check if this song will fit onto the page
        total_height = self.get_y() + max(col1_dims['h'], col2_dims['h']) + Config.PDF_MARGIN_BOTTOM
        song_fits_height = total_height <= Config.PDF_HEIGHT

        if enough_space_left and cols_match_min_height and song_fits_height:
            return min(space_left, Config.MAX_COLUMN_MARGIN)

        return -1


    def _render_lyrics_two_col(self, col1: List[str], col2: List[str], margin_size) -> Dict[str, float]:
        """
        Render a song lyrics in two columns
        @param margin_size: The margin size between the two columns
        @param col1: The first column to render
        @param col2: The second column to render
        """
        # Save the starting Y-coordinate, render the first column, and save the end Y-coordinate
        start_y = self.get_y()
        col1_dims = self._render_lyrics_one_col(col1)
        end_y = self.get_y()

        # Calculate the middle X-coordinate (where the line will be drawn)
        middle_x = col1_dims['w'] + Config.PDF_MARGIN_LEFT + (margin_size / 2)

        # Reset the Y coordinate
        self.set_y(start_y)
        # Calculate the starting x-coordinate for the second column, then render
        start_x = col1_dims['w'] + margin_size + Config.PDF_MARGIN_LEFT
        col2_dims = self._render_lyrics_one_col(col2, start_x=start_x)

        # Calculate the max Y coordinate and draw the dividing line
        max_y = max(end_y, self.get_y())
        self.line(middle_x, start_y + Config.SONG_TITLE_MARGIN, middle_x, max_y)
        # Reset the Y-coordinate to the max-Y reached
        self.set_y(max_y)

        return {
            'h': max(col1_dims['h'], col2_dims['h']),
            'w': col1_dims['w'] + col2_dims['w']
        }

    def _render_lyrics_one_col(self, lines: List[str], start_x=Config.PDF_MARGIN_LEFT) -> Dict[str, float]:
        """
        Renders the given lyrics in a single column
        @param lines: A list of lines to render
        @param start_x: The starting X coordinate of the lyrics
        """
        start_y = self.get_y()
        self.set_y(start_y + Config.SONG_TITLE_MARGIN)
        max_x = 0

        for line in lines:
            # Reset the X-coordinate for each line
            self.set_x(start_x)
            # Check if this line is indented, then strip all whitespace
            indented = line.startswith('\t')
            line = line.strip()

            if indented:
                self.set_x(start_x + Config.PDF_INDENT)

            # Check if this line is bolded
            if Config.RE_BOLD.match(line):
                self.set_font(family=Config.BODY_FONT["family"], style='UI', size=Config.BODY_FONT["size"])
                line = Config.RE_BOLD.match(line).group(1)
            else:
                self.set_font_obj(Config.BODY_FONT)

            # Check if this is a line with chords
            if Config.RE_LYRICS_CHORDS.match(line):
                # This is the minimum X we can write on
                # This prevents us from writing chords on top of each other
                min_x = self.get_x()
                line_words = []
                for line_segment in re.split("(\\[.*?])", line):
                    # If this is a chord, we print it
                    if Config.RE_LYRICS_CHORDS.match(line_segment):
                        # Strip the brackets from the chord
                        chord = line_segment[1:-1]
                        # Calculate the width of the chord
                        width = self.get_string_width(chord)
                        # Set the chord font
                        self.set_font_obj(Config.CHORD_FONT, Config.CHORD_FONT["color"])
                        # Make sure we don't write over other chords
                        self.set_x(max(self.get_x(), min_x))
                        self.cell(w=width, h=Config.CHORD_FONT["size"], txt=chord)
                        # Update the min_x and max_x
                        min_x = self.get_x() + self.get_string_width(" ")  # The MINIMUM X-coordinate we can write on
                        max_x = max(self.get_x(), max_x)  # The MAXIMUM X-coordinate we have reached so far
                        self.set_x(self.get_x() - width)
                        self.set_font_obj(Config.BODY_FONT, Config.BODY_FONT["color"])
                    else:
                        line_words.append(line_segment)
                        self.set_x(self.get_x() + self.get_string_width(line_segment))

                # Linebreak
                self.ln()
                self.set_y(self.get_y() + Config.LINE_HEIGHT)
                line = ''.join(line_words)

            # Reset the X position (in case of chords)
            self.set_x(start_x + (Config.PDF_INDENT if indented else 0))
            # Update the max X position
            max_x = max(self.get_string_width(line) + self.get_x(), max_x)
            # If we have an empty line, the width is 0 - which means unlimited. Instead, we want a small width
            string_width = max(self.get_string_width(line), 0.1)
            # Print the line (or the line minus the chords)
            self.cell(w=string_width, h=Config.BODY_FONT["size"], ln=1, txt=line)
            self.set_y(self.get_y() + Config.LINE_HEIGHT)

        return {
            'h': self.get_y() - start_y,
            'w': max_x - start_x,
        }

    def render_song(self, song: Song) -> Optional[Tuple[str, List[str], int]]:
        """
        Renders the given Song object on the given PDF object
        @param song: The Song object which we render
        @return: The title of this song, the alternate titles, and the page number on which this song starts
        """
        try:
            meta_height = self.render_meta(song.info.meta, True)
            lyric_dims = self.render_lyrics(song.info.lyrics, True)
        except EOFError:
            print(f"Song {song.title} is too long to render")
            return None

        song_height = meta_height + lyric_dims['h']
        # Check if this song can be rendered on the current page - if not, add another
        if song_height > (Config.PDF_HEIGHT - (self.get_y() + Config.PDF_MARGIN_BOTTOM)):
            self.add_page()

        # Here, we calculate if there would be enough room at the bottom of the page to render an image.
        #   If not - we spread the songs out instead
        free_space = Config.PDF_HEIGHT - (self.get_y() + song_height) - Config.PDF_MARGIN_BOTTOM
        # If we don't have enough space, AND this song isn't the first on the page
        if free_space <= Config.MIN_IMAGE_HEIGHT and self.get_y() != Config.PDF_MARGIN_TOP:
            # Bump the song down to the bottom
            page_bottom = Config.PDF_HEIGHT - Config.PDF_MARGIN_BOTTOM - (free_space / 2)
            self.set_y(page_bottom - song_height)

        page_no = self.page_no()
        self.render_meta(song.info.meta)  # Render the metadata of this song
        self.render_lyrics(song.info.lyrics)  # Render the lyrics of this song

        if self.page_no() != page_no:
            print(f"Song {song.info.title} splits multiple pages")

        return song.info.title, song.info.alt_titles, page_no

    def render_songs(self, songs: List[Song], sort_by_name) -> Tuple[List[Tuple[str, int]], Set[str]]:
        """
        Renders all of the songs in a section
        @param songs: A list of the SOng objects
        @param sort_by_name: Whether we sort the songs by their name or not
        @return: A list of tuples containing the song name and page number
        """
        page_numbers = []
        chords = set()
        first = True
        for song in tqdm(songs):
            if not first:
                self.set_y(self.get_y() + Config.SONG_MARGIN)
            else:
                first = False

            out = self.render_song(song)
            if not out:
                continue

            title, alt_titles, page_no = out

            page_numbers.append((title, page_no))
            chords.update(song.get_chords())
            if any("#" in chord or "♭" in chord or "b" in chord for chord in song.get_chords()):
                print(title)


            if sort_by_name:
                # We only bother adding the alternate titles if we sort by name
                #   Otherwise, what's the point? The alt titles would be right below the main one anyways
                for alt in alt_titles:
                    txt = f"{alt} (під '{title}')"
                    page_numbers.append((txt, page_no))

        # Add a page between sections
        self.add_page()

        if sort_by_name:
            return sorted(page_numbers, key=lambda x: Collator().sort_key(x[0])), chords

        return page_numbers, chords


    def _render_index_song(self, song: str, page: int):
        """
        Renders a single entry in the index
        @param song: The song title
        @param page: The page number
        """
        # Figure out how much space we need for numbers (if your pages go higher, we've got other issues)
        text_height = self.get_index_text_height()
        text_width = self.get_index_text_width()

        start_y = self.get_y()
        start_x = self.get_x()
        # Check if this line will go around to the next page
        if start_y + text_height + Config.PDF_MARGIN_BOTTOM > Config.PDF_HEIGHT:
            start_y = Config.PDF_MARGIN_TOP

        # Write the song title
        self.multi_cell(w=text_width, h=text_height, border='B', txt=song)
        # Link the song title to its page
        song_link = self.add_link()
        self.set_link(song_link, page=page)
        self.link(x=start_x, y=start_y, w=text_width, h=text_height, link=song_link)

        end_y = self.get_y()
        # Update the XY, so we write the number next to the title
        self.set_xy(text_width + Config.PDF_MARGIN_LEFT, start_y)
        self.multi_cell(w=self.get_index_number_width(), h=end_y - start_y, border='B', align='C', txt=str(page))
        # Update the y-coordinate to be the larger of the two
        self.set_y(max(self.get_y(), end_y))

    def _render_index_section(self, section: Tuple[str, List[Tuple[str, int]]]):
        """
        Renders a section of the index
        @param section: A list containing tuples of the song title and the page number
        @return:
        """
        # Don't start a new section if we don't have much room on this page
        if self.get_y() + Config.PDF_MARGIN_BOTTOM + 50 > Config.PDF_HEIGHT:
            self.add_page()

        # Write the section header
        self.set_font_obj(Config.INDEX_TITLE_FONT)
        self.ln()
        self.multi_cell(w=0, h=Config.INDEX_TITLE_FONT["size"], txt=section[0])
        self.set_font_obj(Config.INDEX_SONG_FONT)
        self.ln()

        # Write all the songs in the section
        for song, page in section[1]:
            self._render_index_song(song, page)


    def render_index(self, sections: List[Tuple[str, List[Tuple[str, int]]]]) -> None:
        """
        Renders the index of this songbook
        @param sections: The sections of the index - each section has a (name, List[(song_name, song_page_number)])
        """
        if self.get_y() != Config.PDF_MARGIN_TOP:
            # If we have space left on the existing page, use it
            if self.get_y() < (Config.PDF_HEIGHT // 2):
                self.set_y(self.get_y() + Config.SONG_MARGIN)
            else:
                self.add_page()

        self.render_line("Індекс", Config.TITLE_FONT)

        self.set_font_obj(Config.INDEX_SONG_FONT)

        for section in sections:
            self._render_index_section(section)


    def _render_chordboard(self, string_gap: float, fret_gap: float, string_y: float):
        """
        Renders the chordboard (strings & frets) for a chord
        @param string_gap: The gap between strings
        @param fret_gap: The gap between frets
        @param string_y: The starting y-position for the strings (ie. below the fretboard)

        """
        start_x = self.get_x()
        end_x = start_x + Config.CHORD_WIDTH
        start_y = self.get_y()

        self.line(start_x, start_y, end_x, start_y)
        self.line(start_x, string_y, end_x, string_y)

        # Draw the strings
        for i in range(6):
            x = start_x + string_gap * i
            self.line(x, start_y, x, start_y + Config.CHORD_HEIGHT)

        # Draw the frets
        for i in range(4):
            y = string_y + fret_gap * (i + 1)
            self.line(start_x, y, end_x, y)

        self.set_xy(start_x, string_y)

    def _render_chord_fingering(self, frets: List[int], string_gap, fret_gap, start_text_y):
        """
        Draws the chord fingering
        @param frets: The list of string fingering
        @param string_gap: The gap between strings
        @param fret_gap: The gap between frets
        @param start_text_y: The y-location of the chord notes ABOVE the fretboard
            (ie. to denote a closed or open string)
        """
        start_x = self.get_x()
        start_y = self.get_y()

        # Draw the circles
        for string, fret in enumerate(frets):
            # Draw the fingering
            if fret == -1:
                self.text(start_x + (string_gap * string), start_text_y, 'X')
            if fret < 1:
                continue
            x = start_x + string_gap * string
            y = start_y + fret_gap * fret
            diff = Config.CHORD_CIRCLE_DIAM / 2
            self.ellipse(x - diff, y - diff, Config.CHORD_CIRCLE_DIAM, Config.CHORD_CIRCLE_DIAM, style='F')

    def _render_chord(self, name: str, base: int, frets: List[int], min_x: float) -> None:
        """
        Render a single chord
        @param name: The name of the chord
        @param base: The base fret of the chord
        @param frets: The fret fingering of the chord
        """

        if max(frets) > Config.MAX_FRETS:
            return

        start_x = self.get_x()
        start_y = self.get_y()

        # Draw the name of the chord
        self.set_font_obj(Config.BODY_FONT)
        self.cell(Config.CHORD_WIDTH, h=Config.BODY_FONT["size"], ln=2, txt=name, align='C')


        info_font_size = 7
        self.set_font(Config.CHORD_FONT["family"], Config.CHORD_FONT["style"], info_font_size)
        # Draw the fretboard info (if not default)
        if base != 1:
            self.cell(Config.CHORD_WIDTH, h=info_font_size, ln=2, txt=f'Fret {base - 1}', align='C')

        end_x = start_x + Config.CHORD_WIDTH
        start_text_y = self.get_y() + info_font_size
        start_chord_y = start_text_y + 3

        string_gap = Config.CHORD_WIDTH / 5
        fret_gap = (Config.CHORD_HEIGHT - 10) / 4
        fretboard_gap = Config.CHORD_HEIGHT - Config.CHORD_STRING_HEIGHT
        string_y = fretboard_gap + start_chord_y

        self.set_xy(start_x, start_chord_y)
        self._render_chordboard(string_gap, fret_gap, string_y)
        self._render_chord_fingering(frets, string_gap, fret_gap, start_text_y)

        end_y = string_y + Config.CHORD_STRING_HEIGHT
        # Update the X and Y
        next_end_x = end_x + Config.CHORD_MARGIN_HORIZONTAL + Config.CHORD_WIDTH + Config.PDF_MARGIN_RIGHT
        if next_end_x > Config.PDF_WIDTH:
            self.set_xy(min_x, end_y + Config.CHORD_MARGIN_VERTICAL)
        else:
            self.set_xy(end_x + Config.CHORD_MARGIN_HORIZONTAL, start_y)

        # Find out if we need a new page
        next_end_y = self.get_y() + Config.CHORD_HEIGHT + Config.PDF_MARGIN_BOTTOM
        if next_end_y > Config.PDF_HEIGHT:
            self.add_page()
            self.set_x(min_x)



    def render_chords(self, chords: List[str]) -> None:
        """
        Renders the chord page.
        @param chords: A list of the names of the chords
        """
        if self.get_y() != Config.PDF_MARGIN_TOP:
            self.add_page()

        self.set_font_obj(Config.TITLE_FONT)
        self.cell(w=0, h=Config.TITLE_FONT["size"], txt="Акорди", align='C', ln=2)

        # Figure out how many chords we can put in one row
        def _chord_width(x):
            return Config.CHORD_WIDTH * (x + 1) + Config.CHORD_MARGIN_HORIZONTAL * x

        width = 0
        for i in range(10):
            width = _chord_width(i)
            if width > Config.USABLE_PAGE_WIDTH:
                width = _chord_width(i - 1)
                break

        space_left = Config.USABLE_PAGE_WIDTH - width
        start_x = Config.PDF_MARGIN_LEFT + (space_left / 2)
        self.set_x(start_x)

        for chord in chords:
            if chord in Config.KNOWN_CHORDS:
                chord_obj = Config.KNOWN_CHORDS[chord]

                while "copy" in chord_obj:
                    chord = chord_obj['copy']
                    chord_obj = Config.KNOWN_CHORDS[chord]

                self._render_chord(chord, chord_obj['base'], chord_obj['frets'], start_x)
            else:
                print(f"No chord '{chord}'")


        self.set_y(self.get_y() + Config.CHORD_HEIGHT * 2)


TEMP_PDF = PDF()

def render_pdf(sections: List[Tuple[str, List[Song], bool]], outfile: str):
    """
    Renders our songbook.
    @param outfile: The location of the resulting PDF
    @param sections: The sections of the songbook. A section is List[(section_name, List[songs], sort_sec_by_name?)]
    """
    # Create the PDF object
    pdf = PDF()

    # Do some writing
    section_indexes = []
    chords = set()
    for name, songs, sort_by_name in sections:
        print(f"Section '{name}'", flush=True)
        sec_index, sec_chords = pdf.render_songs(songs, sort_by_name)
        section_indexes.append((name, sec_index))
        chords.update(sec_chords)

    print("Rendering index & chord chart")
    pdf.render_chords(sorted(chords))
    pdf.render_index(section_indexes)
    pdf.output(outfile, 'F')
