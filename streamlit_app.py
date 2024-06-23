import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

saarland_groesse = 2569.69 # in km2
url_base = "https://de.wikipedia.org/wiki/"

def link_exists(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        # Handle exceptions (e.g., network problems, invalid URLs)
        st.write("Hast du dich verschrieben?")
        return False

def get_area(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all tables in the page
    tables = soup.find_all('table', {'class': 'infobox'})

    for table in tables:
        # Find all rows in the table
        rows = table.find_all('tr')
        for row in rows:
            # Find all cells in the row
            cells = row.find_all('td')
            if len(cells) > 1 and "Fläche" in cells[0].get_text():
                # Extract the text from the cell next to "Fläche"
                area = cells[1].get_text()
                clean_area = re.sub(r'\[\d+\]', '', area)
                return clean_area.strip()

def clean_result(area):
    area = area.split()
    area_size = area[0].replace(".", "")
    area_size = area_size.replace(",", ".")
    area_size = float(area_size)
    area_measurement = area[-1]
    return area_size, area_measurement

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

query_url = url_base + query

st.write(query)
if link_exists(query_url):
    r = 1
else:
    st.write("Hast du dich verschrieben?")
    #quit()
    
flaeche = get_area(query_url)
groesse, masseinheit = clean_result(flaeche)

relation = compute_relation(groesse, masseinheit, saarland_groesse)
st.write(relation)
create_response(relation)
