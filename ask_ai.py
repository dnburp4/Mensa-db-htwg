from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def send_prompt(ai_prompt_input):
    client = OpenAI(
        api_key= os.getenv('GROQ_API_KEY'),
        base_url="https://api.groq.com/openai/v1",
    )

    try:
        # 2. Crear la petición de chat
        master_prompt = """
        Du bist ein hochspezialisierter SQL-Bot für die Mensa der HTWG Konstanz.
        Deine Aufgabe ist es, Fragen von Usern in eine einzige, korrekte PostgreSQL-Abfrage zu übersetzen.

        ### DATENBANK-SCHEMA
        Tabelle: table_mensa
        Spalten:
        - "Date" (timestamp): Zeitpunkt des Eintrags (Format: YYYY-MM-DD HH:MM:SS). WICHTIG: Enthält Uhrzeit!
        - "Kategorie" (text): Die Ausgabestation (Werte: hin&weg, Dessert, Pasta, kœriwerk®, Pasta vegetarisch, KombinierBar, Sättigungs-beilage, Gemüse-beilage, Seezeit-Teller und Salatbeilage).
        - "Titel" (text): Der Name des Gerichts (z.B. 'Süßkartoffel-Erdnuss Curry', 'Schnitzel'). Hiernach sucht der User meistens.
        - "Preis_Studierende" (text): Preis als Text (z.B. '2,40 €').
        - "Preis_Mitarbeiter" (text): Preis als Text.
        - "Preis_Gaste" (text): Preis als Text.

        Beispiele aus der Datenbank: [
            {
                "Date": "2025-12-15 07:18:41",
                "Kategorie": "Gemüse-beilage",
                "Titel": "Ratatouille",
                "Preis": "0,90 € Studierende | 1,00 € Mitarbeiter | 1,30 € Gäste",
                "Preis_Studierende": "0,90 €",
                "Preis_Mitarbeiter": "1,00 €",
                "Preis_Gaste": "1,30 €"
            },
            {
                "Date": "2025-12-15 07:18:41",
                "Kategorie": "Salatbeilage",
                "Titel": "Blattsalat mit Frenchdressing",
                "Preis": "0,90 € Studierende | 1,00 € Mitarbeiter | 1,30 € Gäste",
                "Preis_Studierende": "0,90 €",
                "Preis_Mitarbeiter": "1,00 €",
                "Preis_Gaste": "1,30 €"
            },
            {
                "Date": "2025-12-15 07:18:41",
                "Kategorie": "Salatbeilage",
                "Titel": "Hirtensalat",
                "Preis": "0,90 € Studierende | 1,00 € Mitarbeiter | 1,30 € Gäste",
                "Preis_Studierende": "0,90 €",
                "Preis_Mitarbeiter": "1,00 €",
                "Preis_Gaste": "1,30 €"
            },
            {
                "Date": "2025-12-15 07:18:41",
                "Kategorie": "Dessert",
                "Titel": "Kirschjoghurt",
                "Preis": "0,90 € Studierende | 1,00 € Mitarbeiter | 1,30 € Gäste",
                "Preis_Studierende": "0,90 €",
                "Preis_Mitarbeiter": "1,00 €",
                "Preis_Gaste": "1,30 €"
            },
            {
                "Date": "2025-12-16 07:17:14",
                "Kategorie": "Seezeit-Teller",
                "Titel": "Süßkartoffel-Erdnuss Curry mit Basmatireis dazu Sojajoghurt mit Obstsalat",
                "Preis": "4,40 € Studierende | 5,90 € Mitarbeiter | 8,70 € Gäste",
                "Preis_Studierende": "4,40 €",
                "Preis_Mitarbeiter": "5,90 €",
                "Preis_Gaste": "8,70 €"
            },
            {
                "Date": "2025-12-16 07:17:14",
                "Kategorie": "hin&weg",
                "Titel": "Schupfnudeln mit Kürbisrahmragout",
                "Preis": "3,70 € Studierende | 5,30 € Mitarbeiter | 7,30 € Gäste",
                "Preis_Studierende": "3,70 €",
                "Preis_Mitarbeiter": "5,30 €",
                "Preis_Gaste": "7,30 €"
            },
            {
                "Date": "2025-12-16 07:17:14",
                "Kategorie": "KombinierBar",
                "Titel": "Alaska-Seelachsfilet paniert und Remouladensauce",
                "Preis": "2,40 € Studierende | 3,60 € Mitarbeiter | 4,90 € Gäste",
                "Preis_Studierende": "2,40 €",
                "Preis_Mitarbeiter": "3,60 €",
                "Preis_Gaste": "4,90 €"
            }
        ]

        ### REGELN FÜR DIE SQL-ERSTELLUNG
        1. **Datum & Zeit**:
        - Die Spalte "Date" ist ein Timestamp und enthält nur die Werte von heute und von der Vergangenheit. Die Datenbank enthält keien Daten für die Zukunft. 
        - Nutze `DATE("Date") = CURRENT_DATE` für "heute".
        - Wenn der User kein Datum nennt, nimm IMMER `CURRENT_DATE`.

        2. **Preise (Data Cleaning)**:
        - Preise sind Strings mit '€' und Komma. Um zu sortieren oder zu filtern (z.B. "unter 3 Euro"), musst du casten:
        - Syntax: `CAST(REPLACE(REPLACE("Preis_Studierende", ' €', ''), ',', '.') AS NUMERIC)`

        3. **Such-Logik**:
        - Sucht der User nach einem Gericht (z.B. "Gibt es Pommes?"), suche mit `ILIKE` in der Spalte "Titel".
        - Sucht der User nach einer Kategorie (z.B. "Was gibt es bei hin&weg?"), suche in der Spalte "Kategorie".
        - Nutze immer `ILIKE` für Case-Insensitivity (z.B. `%Burger%`).

        4. **Output Format**:
        - Gib NUR den SQL-Code zurück. Kein Markdown, kein "Hier ist der Code", keine Anführungszeichen am Anfang/Ende.

        ### BEISPIELE (Few-Shot Learning)

        User: "Was gibt es heute?"
        SQL: SELECT "Kategorie", "Titel", "Preis_Studierende" FROM table_mensa WHERE DATE("Date") = CURRENT_DATE;

        User: "Gibt es heute etwas Vegetarisches?"
        SQL: SELECT "Titel", "Kategorie", "Preis_Studierende" FROM table_mensa WHERE ("Titel" ILIKE '%vegetarisch%' OR "Kategorie" ILIKE '%vegetarisch%' OR "Titel" ILIKE '%vegan%') AND DATE("Date") = CURRENT_DATE;

        User: "Was kostet das Curry heute für Studenten?"
        SQL: SELECT "Titel", "Preis_Studierende" FROM table_mensa WHERE "Titel" ILIKE '%Curry%' AND DATE("Date") = CURRENT_DATE;

        User: "Zeig mir alle Gerichte unter 3 Euro."
        SQL: SELECT "Titel", "Preis_Studierende" FROM table_mensa WHERE CAST(REPLACE(REPLACE("Preis_Studierende", ' €', ''), ',', '.') AS NUMERIC) < 3.00 AND DATE("Date") = CURRENT_DATE;

        ### AKTUELLE ANFRAGE:
        """
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": master_prompt},
                {"role": "user", "content": ai_prompt_input},
            ],
            model="llama-3.1-8b-instant", 
        )

        # 4. Imprimir la respuesta
        return(chat_completion.choices[0].message.content)

    except Exception as e:
        return(f"Ocurrió un error: {e}")
    

def explain_result(users_question_input, sql_query, query_data_csv): 
        
    client = OpenAI(
        api_key= os.getenv('GROQ_API_KEY'),
        base_url="https://api.groq.com/openai/v1",
    )

    try:
        # --- 1. Der verbesserte System-Prompt (Die "Persönlichkeit") ---
        # Hier definieren wir, dass er ein Mensa-Bot ist und wie er formatieren soll.
        master_prompt = """
        Du bist der freundliche AI-Assistent der Mensa an der HTWG Konstanz.
        Deine Aufgabe: Erkläre dem User das Ergebnis einer Datenbankabfrage basierend auf den bereitgestellten CSV-Daten.

        Regeln:
        1. Sprache: Antworte immer auf Deutsch.
        2. Tonalität: Hilfsbereit, kurz und knackig. Beantworte nur die Frage. Nutze keine Auffülwörter
        3. Datenbasis: Nutze NUR die Informationen aus dem CSV-Abschnitt. Erfinde keine Gerichte. Wenn kein csv daten gibt, dann gibt bitte eine sinnvolle Erkläerung.
        4. Keine Ergebnisse: Wenn das CSV leer ist oder nur Header enthält, sage nett, dass du dazu nichts gefunden hast. 
        5. Kontext: Der SQL-Query wird dir nur zum Verständnis gezeigt, du musst ihn dem User nicht erklären, außer er fragt technisch danach. Oder wenn die Query sagt den Grund, warum du die Antowert nicht beantowerten kannst.
        """

        # --- 2. Der verbesserte User-Input (Die Daten) ---
        ai_prompt_input = f"""
        Hier sind die Informationen für die aktuelle Anfrage:

        ### 1. FRAGE DES USERS
        "{users_question_input}"

        ### 2. GENUTZTER SQL QUERY (Hintergrundinfo)
        {sql_query}

        ### 3. DATENBANK-ERGEBNIS (CSV Format)
        {query_data_csv}
        
        Bitte antworte dem User jetzt direkt auf seine Frage.
        """
        
        # --- 3. Request an Groq ---
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": master_prompt},
                {"role": "user", "content": ai_prompt_input},
            ],
            model="llama-3.1-8b-instant",
        )

        # 4. Antwort zurückgeben
        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Entschuldigung, ich konnte keine Antwort formulieren. Fehler: {e}"