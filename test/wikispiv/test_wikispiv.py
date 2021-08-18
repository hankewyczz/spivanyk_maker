from src.wikispiv.wikispiv import *


def test_title_search():
    assert "Цвіт України і краса" == title_search("Цвіт України і краса")
    assert "Цвіт України і краса" == title_search("Цвіт україни і краса")
    assert "Цвіт України і краса" == title_search("Цвіт_України_і_краса")
    assert "Цвіт України і краса" == title_search("цвіт_україни_і_краса")

    assert "Пластовий гімн" == title_search("Пластовий гімн")
    assert "Пластовий гімн" == title_search("пластовий гімн")

    assert "Коли у путь" == title_search("Коли У путь")
    assert "Бий барабан" == title_search("Бий барабан")



def test_get_root_page():
    assert "Гімн Пласту" == get_root_page("Цвіт України і краса")
    assert "Гімн Пласту" == get_root_page("Цвіт україни І Краса")
    assert "Гімн Пласту" == get_root_page("Пластовий гімн")
    assert "Гімн Пласту" == get_root_page("Гімн Пласту")

    assert "Бий барабан" == get_root_page("Коли у путь")
    assert "Бий барабан" == get_root_page("Бий барабан")
    assert "Бий барабан" == get_root_page("Бий Барабан")


def test_get_backlinks():
    assert [] == get_backlinks("Цвіт України і краса")
    assert [] == get_backlinks("Пластовий гімн")
    assert {"Цвіт України і краса", "Пластовий гімн"} == set(get_backlinks("Гімн Пласту"))
    assert {"Цвіт України і краса", "Пластовий гімн"} == set(get_backlinks("гімн пласту"))

    assert [] == get_backlinks("Коли у путь")
    assert {"Коли у путь"} == set(get_backlinks("Бий барабан"))


def test_alternate_titles():
    assert {"Гімн Пласту", "Пластовий гімн"} == set(get_alternate_titles("Цвіт України і краса"))
    assert {"Гімн Пласту", "Пластовий гімн"} == set(get_alternate_titles("Цвіт_України_і_краса"))
    assert {"Цвіт України і краса", "Гімн Пласту"} == set(get_alternate_titles("Пластовий гімн"))
    assert {"Цвіт України і краса", "Пластовий гімн"} == set(get_alternate_titles("Гімн Пласту"))

    assert {"Бий барабан"} == set(get_alternate_titles("Коли у путь"))
    assert {"Коли у путь"} == set(get_alternate_titles("Бий барабан"))
