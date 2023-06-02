import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import csv
import dash
import dash_core_components as dcc
import dash_html_components as html


def akceptuj_cookie(driver):
    time.sleep(1)
    try:
        cookie_button = driver.find_element(by=By.CSS_SELECTOR, value='[id="onetrust-accept-btn-handler"]')
        cookie_button.click()
    except Exception:
        cookie_button = driver.find_element(by=By.CSS_SELECTOR, value='[data-role="accept-consent"]')
        cookie_button.click()


def scrape_dane_samochodow_otomoto():
    driver = webdriver.Chrome()
    driver.get('https://www.otomoto.pl/osobowe/')

    akceptuj_cookie(driver)

    ogloszenia_elementy = driver.find_elements(By.CSS_SELECTOR, value='[data-testid="listing-ad"]')
    ogloszenia_elementy2 = driver.find_elements(By.CSS_SELECTOR, value='[data-testid="carsmile-listing-ad"]')
    ogloszenia_elementy.append(ogloszenia_elementy2)

    dane_samochodow = []
    ilosc_ogloszen = len(ogloszenia_elementy)
    for element in ogloszenia_elementy:
        try:
            cena_element = element.find_element(By.CSS_SELECTOR, value='[class="ooa-1bmnxg7 evg565y11"]')
            cena = float(cena_element.text.replace(' ', '').replace('PLN', ''))
            dane_samochodow.append(cena)
        except Exception as e:
            print("please wait...")

    driver.quit()
    return ilosc_ogloszen, min(dane_samochodow), max(dane_samochodow), sum(dane_samochodow) / len(dane_samochodow)


def scrape_dane_samochodow_allegro():
    driver = webdriver.Chrome()
    driver.get('https://allegro.pl/kategoria/samochody-osobowe-4029')

    akceptuj_cookie(driver)

    ogloszenia_elementy = driver.find_elements(By.CSS_SELECTOR, value='[class="mx7m_1 mnyp_co mlkp_ag _6a66d_u7-8J"]')

    dane_samochodow = []
    ilosc_ogloszen = len(ogloszenia_elementy)
    for element in ogloszenia_elementy:
        try:
            cena_element = element.find_element(By.CSS_SELECTOR, value='[data-test-tag="price-container"]')
            cena = float(cena_element.text.replace(' ', '').replace('zł', '').split(",")[0].replace(",", ""))
            dane_samochodow.append(cena)
        except Exception as e:
            print("please wait...")

    driver.quit()
    return ilosc_ogloszen, min(dane_samochodow), max(dane_samochodow), sum(dane_samochodow) / len(dane_samochodow)


def zapisz_do_csv(nazwa_pliku, data, dane_otomoto, dane_allegro):
    naglowki = ['Data', 'Ilość Ogłoszeń Otomoto', 'Cena Min. Otomoto', 'Cena Max. Otomoto', 'Cena Średnia Otomoto',
                'Ilość Ogłoszeń Allegro', 'Cena Min. Allegro', 'Cena Max. Allegro', 'Cena Średnia Allegro']
    nowy_wiersz = [data, dane_otomoto[0], dane_otomoto[1], dane_otomoto[2], dane_otomoto[3], dane_allegro[0],
                   dane_allegro[1], dane_allegro[2], dane_allegro[3]]

    try:
        if os.path.exists(nazwa_pliku):
            with open(nazwa_pliku, 'a', newline='', encoding='utf-8') as plik:
                writer = csv.writer(plik)
                writer.writerow(nowy_wiersz)
        else:
            with open(nazwa_pliku, 'w', newline='', encoding='utf-8') as plik:
                writer = csv.writer(plik)
                writer.writerow(naglowki)
                writer.writerow(nowy_wiersz)
    except FileNotFoundError:
        print("Błąd: Nie można zapisać danych do pliku.")


def wczytaj_dane_z_csv(nazwa_pliku):
    dane = pd.read_csv(nazwa_pliku)
    return dane


def generuj_wykres(dane):
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Graph(
            id='wykres',
            figure={
                'data': [
                    {'x': dane['Data'], 'y': dane['Cena Średnia Otomoto'], 'type': 'line', 'name': 'Średnia Otomoto'},
                    {'x': dane['Data'], 'y': dane['Cena Min. Otomoto'], 'type': 'line', 'name': 'Minimalna Otomoto'},
                    {'x': dane['Data'], 'y': dane['Cena Max. Otomoto'], 'type': 'line', 'name': 'Maksymalna Otomoto'},
                    {'x': dane['Data'], 'y': dane['Cena Średnia Allegro'], 'type': 'line', 'name': 'Średnia Allegro'},
                    {'x': dane['Data'], 'y': dane['Cena Min. Allegro'], 'type': 'line', 'name': 'Minimalna Allegro'},
                    {'x': dane['Data'], 'y': dane['Cena Max. Allegro'], 'type': 'line', 'name': 'Maksymalna Allegro'}
                ],
                'layout': {
                    'title': 'Zachowanie cen samochodów',
                    'xaxis': {'title': 'Data'},
                    'yaxis': {'title': 'Cena (zł)'}
                }
            }
        )
    ])
    app.run_server(debug=True)


def main():
    folder = "C:/Users/szymon.wujec/OneDrive - JLL/Desktop/Szymon/PJATK/PAD/H7/output"
    nazwa_pliku = os.path.join(folder, "wyniki.csv")
    if not os.path.exists(folder):
        os.makedirs(folder)

    data = datetime.datetime.now().strftime('%Y-%m-%d %H')
    dane_otomoto = scrape_dane_samochodow_otomoto()
    dane_allegro = scrape_dane_samochodow_allegro()

    zapisz_do_csv(nazwa_pliku, data, dane_otomoto, dane_allegro)

    dane = wczytaj_dane_z_csv(nazwa_pliku)
    generuj_wykres(dane)


if __name__ == "__main__":
    main()
