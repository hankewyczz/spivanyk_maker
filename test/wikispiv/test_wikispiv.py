from src.wikispiv.song import *


def test_title_search():
    assert "Цвіт України і краса" == songtitle_search("Цвіт України і краса")
    assert "Цвіт України і краса" == songtitle_search("Цвіт україни і краса")
    assert "Цвіт України і краса" == songtitle_search("Цвіт_України_і_краса")
    assert "Цвіт України і краса" == songtitle_search("цвіт_україни_і_краса")

    assert "Пластовий гімн" == songtitle_search("Пластовий гімн")
    assert "Пластовий гімн" == songtitle_search("пластовий гімн")

    assert "Коли у путь" == songtitle_search("Коли У путь")
    assert "Бий барабан" == songtitle_search("Бий барабан")



def test_get_root_page():
    assert "Гімн Пласту" == get_main_title("Цвіт України і краса")
    assert "Гімн Пласту" == get_main_title("Пластовий гімн")
    assert "Гімн Пласту" == get_main_title("Гімн Пласту")

    assert "Бий барабан" == get_main_title("Коли у путь")
    assert "Бий барабан" == get_main_title("Бий барабан")


def test_get_backlinks():
    assert [] == get_backlinks("Цвіт України і краса")
    assert [] == get_backlinks("Пластовий гімн")
    assert {"Пластовий гімн", "Цвіт України і краса"} == set(get_backlinks("Гімн Пласту"))

    assert [] == get_backlinks("Коли у путь")
    assert {"Коли у путь"} == set(get_backlinks("Бий барабан"))

def test_slugify():
    assert "цвіт_україни_і_краса" == snake_case("Цвіт України і краса")
    assert "алилуя_в_хатині_тихій_чарівній" == snake_case("Алилуя (В хатині тихій чарівній)")
    assert "без_природи_нас_нема" == snake_case("Без природи, нас нема")

