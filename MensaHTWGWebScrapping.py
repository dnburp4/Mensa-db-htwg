from bs4 import BeautifulSoup
import requests
import pandas as pd
from sqlalchemy import create_engine
import re
import os
from dotenv import load_dotenv
import datetime


def webScrappingUni(): 
    
    hwtgPageToScrape = requests.get("https://seezeit.com/essen/speiseplaene/mensa-htwg/")
    soupAsHTMLCode = BeautifulSoup(hwtgPageToScrape.text, "html.parser")
    tab2 = soupAsHTMLCode.find("div", class_="contents_aktiv")
    gerichte = tab2.find_all("div", class_="speiseplanTagKat")


    gerichteListe = []

    for gericht in gerichte:

        roh_titel = gericht.find("div", class_="title").get_text(" ", strip=True)

        try:
            gerichteListe.append({
                "Kategorie": gericht.find("div", class_="category").get_text(strip=True),
                #Mit Hilfe von Regular Expression werden die Nummern in Klammern von Titel vermieden
                "Titel": re.sub(r"\s*\([^)]*\)", "", roh_titel).strip(),
                "Preis": gericht.find("div", class_="preise").get_text(strip=True)
            })

        except AttributeError:
            continue

    df_gerichte = pd.DataFrame(gerichteListe)


    # Split 'Preis' in drei neue Spalten, behalte die Originalspalte
    df_gerichte[['Preis_Studierende', 'Preis_Mitarbeiter', 'Preis_Gaste']] = df_gerichte['Preis'].str.split('|', n=2, expand=True)
    df_gerichte['Preis_Studierende'] = df_gerichte['Preis_Studierende'].str.strip()
    df_gerichte['Preis_Mitarbeiter'] = df_gerichte['Preis_Mitarbeiter'].str.strip()
    df_gerichte['Preis_Gaste'] = df_gerichte['Preis_Gaste'].str.strip()
    df_gerichte['Preis_Studierende'] = df_gerichte['Preis_Studierende'].str.replace(r'(\d+,\d+\s*€).*', r'\1', regex=True)
    df_gerichte['Preis_Mitarbeiter'] = df_gerichte['Preis_Mitarbeiter'].str.replace(r'(\d+,\d+\s*€).*', r'\1', regex=True)
    df_gerichte['Preis_Gaste'] = df_gerichte['Preis_Gaste'].str.replace(r'(\d+,\d+\s*€).*', r'\1', regex=True)

    print(df_gerichte)
    df_gerichte.info()


    df_gerichte["Date"] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    df_gerichte = df_gerichte[['Date','Kategorie','Titel','Preis','Preis_Studierende','Preis_Mitarbeiter','Preis_Gaste']]

    #df_gerichte.to_csv(r"mensa.csv", index=False)
    #print("Succes csv was uploaded succesfully")


    load_dotenv()

    # 3. PostgreSQL connection Setup
    user = os.getenv("user")
    password = os.getenv("password")
    host = os.getenv("host")
    port = os.getenv("port")
    database = os.getenv("database")


    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')


    #Save to DB
    df_gerichte.to_sql('table_mensa', con=engine, if_exists='append', index = False)

    print("Succes sending the daba to SQL neon")
