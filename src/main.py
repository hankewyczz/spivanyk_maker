from pathlib import Path
from typing import Optional, Tuple

from song import *
from src.render.render import render_pdf


def get_song(raw_title: str) -> Optional[Song]:
    """
    Try to get the song matching this title, first locally, then from WikiSpiv
    @param raw_title: The raw title for which we search
    @return: A Song object if the song could be located, None otherwise
    """
    # Try to standardize the title
    title = songtitle_search(raw_title)

    # If we can't standardize it, use the raw name
    if not title:
        title = raw_title

    # Next, we ensure we're using the main title of the song
    title = get_main_title(title)

    song_obj = Song(title)
    filepath = os.path.join("../songs", song_obj.filename)

    if not Path(filepath).exists():
        while True:
            reply = str(input(f'Song "{title}" does not exist. Try downloading from WikiSpiv? (y/n): ')).lower().strip()
            if reply and reply[0] == 'y':
                break
            if reply and reply[0] == 'n':
                return None
        with open(filepath, 'w', encoding='utf-8') as f:
            try:
                f.write(song_obj.to_chordpro())
            except ValueError as e:
                print(e)
                print("Skipping song")
                return None
        print(f"Downloaded '{title}' from WikiSpiv")
    return song_obj


def main():
    sections: List[Tuple[str, str, bool]] = UPU_SPIVANYK
    outfile = 'tmp.pdf'

    sections_objs = []
    for name, songs, sort_by_name in sections:
        song_lst = [get_song(song.strip()) for song in songs.split('\n') if song.strip()]
        song_lst: List[Song] = [x for x in song_lst if x]  # Filter None values

        sections_objs.append((name, song_lst, sort_by_name))

    print("Rendering PDF")
    render_pdf(sections_objs, os.path.join(ROOT_DIR, outfile))



UPU_SPIVANYK = [
        ("Гімни/Молотви",
         """
         Гімн закарпатських пластунів
         Гімн Пласту
         Отче Наш
         Пластовий Обіт
         При ватрі
         Царю небесний
         """,
         True
         ),
        ("Для Запалленя Ватри",
         """
         Гей-гу, ватра горить
         Горить ватра
         """,
         True
         ),
        ("Пісні",
         """
         8-ий колір
        Бий барабан
        Била мене мати
        Біла хата в саду
        Вогов
        Водограй
        Воля 
        Вона
        Гей, забава!
        Гей, скобе!
        Гори, гори
        Грішник   
        З сиром пироги
        Заходить сонце золоте
        Кедь ми прийшла карта
        Козак Від'їжджає
        Лебеді материнства
        Лента за лентою
        Надія є
        Найкращі Дівчата
        Не бійся жити
        Нині
        Ой Видно Село
        Ой на горі цигани стояли
        Писаний Камінь
        Пісня Буде Поміж Нас
        Подай дівчино ручку на прощання
        Рушив поїзд
        Село
        Соловію
        Спалена пісня
        Старенький трамвай
        Там, під Львівським замком
        Ти ж мене підманула
        Хвилю тримай
        Циганочко моя
        Чабан
        Чарівні очі
        Чекатиму
        Червона рожа трояка
        Червона рута
        Чом Ти Не Прийшов
        Чотири Рожі
        Шабелина
        Юначе, ти знай
        Я Піду В Далекі Гори
        """,
         True),
        ("Таборові Пісні",
         """
        Пісня Нового Соколу
        У дику далечінь
        Шум води і спокій лісу
        """,
         False
         )
    ]


if __name__ == "__main__":
    main()



