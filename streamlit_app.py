import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# fest zugewiesen
saarland_groesse = 2569.69 # in km2
url_base = "https://de.wikipedia.org/wiki/"

# Funktionen

# zu erwartende Frage, die nicht mit Wikipedia beantwortet werden kann
def check_fussball(query):
    if query == "Fußballfeld" or query == "Fussballfeld":
        return True

# Schauen, ob es das auf Wikipedia gibt
def link_exists(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        st.write("Hast du dich verschrieben? Wenn nicht, dann kenne ich hierzu kein Ergebnis.")
        return False

# Die Fläche wird aus der Beschreibungstabelle von Wikipedia entnommen.
def get_area(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Infobox
    tables = soup.find_all('table', {'class': 'infobox'})

    for table in tables:
        rows = table.find_all('tr') # alle Zeilen
        flaeche_any = False
        for row in rows: # alle Einträge
            cells = row.find_all('td') # alle Einträge
            if len(cells) > 1 and "Fläche" in cells[0].get_text():
                flaeche_any = True
                area = cells[1].get_text()
                clean_area = re.sub(r'\[\d+\]', '', area)
                return clean_area.strip()
        if flaeche_any == False:
            st.write("Hierzu kenne ich keine Flächenangabe.")
            quit()


def clean_result(area):
    # Größe und Maßeinhei der Eintragung entnehmen.
    try:
        area = area.replace(".", "") # in englisches System umwandeln
        area = area.replace(",", ".") # in englisches System umwandeln
        for i in area.split(): # versuche, jedes Element der aus dem String resultierenden Liste, in ein Float zu verwandeln
            try:
                area_size = float(i)
                break # höre auf damit, wenn es zum ersten Mal klappt (nimmt also immer die kleinste Angabe bei mehreren)
            except:
                continue
        if 'km²' in area:
            area_measurement = 'km²'
        elif 'm²' in area:
            area_measurement = 'm²'
        else:
            area_measurement = 'unknown'
        return area_size, area_measurement
    except:
        quit()

def compute_relation(area_size, area_measurement, saarland_groesse):
    if area_measurement == 'km²':
        return area_size / saarland_groesse
    if area_measurement == 'm²':
        saarland_groesse_m2 = saarland_groesse * 1000000
        return area_size / saarland_groesse_m2
    else:
        return area_size / saarland_groesse
        
def create_response(relation):
    if relation < 1:
        st.write(f'Du hast etwas gefunden, das kleiner ist als das Saarland! {query} würde {round(1/relation, 2)} Mal ins Saarland passen.')
    elif relation > 1:
        st.write(f'Das Saarland würde {round(relation, 2)} Mal in {query} passen.')
    else:
        st.write(f'Du hast Saarland eingegeben oder?')


st.title("Die Saarland-Vergleichs-App")


query = st.text_input("Wie groß ist das Saarland im Vergleich zu ___ ?")

    
if check_fussball(query) == True:
    groesse = 0.00714
    masseinheit = "km²"
else:
    query_url = url_base + query

    if link_exists(query_url):
        r = 1
    else:
        st.write("Hast du dich verschrieben? Wenn nicht, dann kenne ich hierzu kein Ergebnis.")
        #quit()
    
    flaeche = get_area(query_url)
    groesse, masseinheit = clean_result(flaeche)

relation = compute_relation(groesse, masseinheit, saarland_groesse)
create_response(relation)
