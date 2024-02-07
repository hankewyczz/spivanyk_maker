from typing import List, Optional
from bs4 import BeautifulSoup
import requests
from consts import Config
from song.local_song import LocalSong


class WikiSpivSong:
	def __init__(self, song_title):
		self.song_title = self.standardize_song_name(song_title)
		self.filepath = LocalSong.standardize_filepath(self.song_title)

		if LocalSong.exists(self.song_title):
			raise f"Song '{song_title}' already exists on disk; Will not create a new WikiSpivSong"

		self.alt_titles = self._get_backlinks(song_title)

	@classmethod
	def standardize_song_name(cls, song_title: str):
		""" Tries finding the closest-matching title in WikiSpiv,
		then tries finding the "root" song title (i.e. the most popular/used one) """

		closest_matching_title = cls._get_closest_matching_song_title(song_title)

		# It's possible WikiSpiv has no results; in that case, keep using the raw name
		if closest_matching_title:
			song_title = closest_matching_title

		# Try finding the "main" title of the song
		return cls._get_main_song_title(song_title)

	@classmethod
	def _get_closest_matching_song_title(cls, song_title: str) -> Optional[str]:
		""" Finds the WikiSpiv song title which most closely matches the given title.
		Helps correct for typos or small variations in titles. """
		base_url = f"{Config.WIKI_API_URL}&action=query&list=search&srsearch={song_title}&srwhat="
		
		# We try the most specific search type first
		response = requests.get(f"{base_url}nearmatch").json()
		results = response["query"]["search"]

		if len(results) == 0:
			response = requests.get(f"{base_url}title").json()
			results = response["query"]["search"]

		return results[0]["title"] if results else None
	
	@classmethod
	def _get_main_song_title(cls, song_title: str) -> str:
		""" Some songs have multiple names - this finds the "root" name that WikiSpiv redirects to. """

		url = f"{Config.WIKI_API_URL}&action=query&titles={song_title}&redirects"
		response = requests.get(url).json()
		# Get the resulting page from this query. This is the root page - ie. follow all redirects until there are no more
		#   If a page has no redirects, the root page is itself
		redirect_pages = response["query"]["pages"].values()
		root_page = list(redirect_pages)[0]

		return root_page["title"]
	
	def _get_backlinks(self, title: str) -> List[str]:
		""" Find every page which redirects to this page """
		url = f"{Config.WIKI_API_URL}&action=query&generator=redirects&titles={title}"
		response = requests.get(url).json()

		if "query" not in response or "pages" not in response["query"]:
			return []

		return sorted(page["title"] for _, page in response["query"]["pages"].items())

	def _download_raw_song(self):
		""" Downloads the Wiki page of the given song, and parses its contents
		:return: A tuple containing the credits and song contents, respectively
		"""
		url = f"{Config.WIKI_SONG_URL}/{self.song_title}?action=render"
		r = requests.get(url)

		if not r.ok:
			raise ValueError(f"Could not retrieve song {self.song_title} from WikiSpiv (error: {r.status_code})")

		soup = BeautifulSoup(r.text, 'html.parser')

		meta_divs = soup.find_all('div', class_='credit')
		song_meta = [div.get_text() for div in meta_divs]
		song_meta = [cred for cred in song_meta if cred]

		song_lyrics = soup.find_all('div', class_='spiv')[0]

		return song_meta, song_lyrics

	def _convert_song_content_to_chordpro(self, content):
		"""
		Converts WikiSpiv lyrics to ChordPro format
		@param content: The content of the WikiSpiv-formatted song
		@return: A string containing the ChordPro formatted lyrics
		"""
		out = []
		for line in content.find_all('div'):
			line_lst = ["\t"] if "indented" in line['class'] else []

			for span in line.find_all('span'):
				# If it's a linediv, we don't care - we care about the div inside
				if span['class'] == "linediv":
					span = span.contents[0]

				if "indented" in span['class']:
					line_lst.append("\t")
				if "data-chord" in span.attrs:
					chord = f"[{span['data-chord']}]" if span['data-chord'] else ""
					line_lst.append(f"{chord}{span.string}")
				elif "bang" in span['class']:
					line_lst.append(f"<bold>{span.string}</bold>")
				elif "chord" in span['class']:
					line_lst.append(' '.join(f"[{chord}]" for chord in span.string.split()))
				else:
					line_lst.append(span.string)

			out.append(''.join(line_lst))
		return '\n'.join(out)

	def _convert_song_to_chordpro(self, song_credits, song_contents) -> str:
		"""
		Converts this Song object to ChordPro format
		:return: The ChordPro formatted string of this Song
		"""
		out = ["## Saved from WIKISPIV.com"]
		out.append(f"{{title: {self.song_title}}}")
		out.extend((f"{{meta: alt_title {alt}}}" for alt in self.alt_titles))
		out.extend((f"{{subtitle: {credit}}}" for credit in song_credits))
		out.append('\n')
		out.append(self._convert_song_content_to_chordpro(song_contents))

		return '\n'.join(out)

	def download_song(self):
		song_credits, song_contents = self._download_raw_song()
		chordpro_text = self._convert_song_to_chordpro(song_credits, song_contents)

		with open(self.filepath, 'w', encoding='utf-8') as f:
			try:
				f.write(chordpro_text)
				print(f"Downloaded '{self.song_title}' from WikiSpiv")
			except ValueError as e:
				print(f"Skipping song: {e}")
				return None