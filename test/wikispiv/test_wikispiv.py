from src.wikispiv.song import *


def test_title_search():
    titles = ["Цвіт України і краса", "Алилуя (В хатині тихій чарівній)", "Без природи, нас нема",
              "Ukraeenska mova", "Ride, kozak, ride", "Koobassa / Osyledtsee", "B.O.R.S.C.H.T.",
              "Пластовий гімн", "Бий барабан", "Коли у путь", "Горить ватра"]

    for title in titles:
        assert title == songtitle_search(title.upper())
        assert title == songtitle_search(title.lower())
        assert title == songtitle_search(title.capitalize())
        assert title == songtitle_search(title.replace(' ', '_'))



def test_get_main_title():
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

def test_snake_case():
    assert "цвіт_україни_і_краса" == snake_case("Цвіт України і краса")
    assert "алилуя_в_хатині_тихій_чарівній" == snake_case("Алилуя (В хатині тихій чарівній)")
    assert "без_природи_нас_нема" == snake_case("Без природи, нас нема")
    assert "ukraeenska_mova" == snake_case("Ukraeenska mova")
    assert "ride_kozak_ride" == snake_case("Ride, kozak, ride")
    assert "koobassa_osyledtsee" == snake_case("Koobassa / Osyledtsee")
    assert "borscht" == snake_case("B.O.R.S.C.H.T.")


def test_song_filename():
    assert "цвіт_україни_і_краса.cho" == song_filename("Цвіт України і краса")
    assert "алилуя_в_хатині_тихій_чарівній.cho" == song_filename("Алилуя (В хатині тихій чарівній)")
    assert "без_природи_нас_нема.cho" == song_filename("Без природи, нас нема")
    assert "ukraeenska_mova.cho" == song_filename("Ukraeenska mova")
    assert "ride_kozak_ride.cho" == song_filename("Ride, kozak, ride")
    assert "koobassa_osyledtsee.cho" == song_filename("Koobassa / Osyledtsee")
    assert "borscht.cho" == song_filename("B.O.R.S.C.H.T.")


