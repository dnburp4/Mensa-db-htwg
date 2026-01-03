import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import streamlit as st
import ask_ai 

def db_connection():
    load_dotenv()

    # 3. PostgreSQL connection Setup
    user = os.getenv("user")
    password = os.getenv("password")
    host = os.getenv("host")
    port = os.getenv("port")
    database = os.getenv("database")
   

    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}?sslmode=require&channel_binding=require')

    return engine

st.set_page_config(
    page_title="Mensa HTWG App",
    page_icon="🥨"
)



st.title("HTWG Mensa Report Bot SQL Generator")

user_input = st.text_input("Was möchtest du über die HTGW Mensa Gerichte wissen?")

if user_input:
    # 1. SQL generieren
    sql_query = ask_ai.send_prompt(user_input)
    
    # Debugging Option (um zu sehen was die KI schreibt)
    with st.expander("Zeige generiertes SQL"):
        st.code(sql_query, language='sql')
    
    try:
        # 2. SQL ausführen
        ergebnis_df = pd.read_sql(text(sql_query), con=db_connection())     
        st.dataframe(ergebnis_df, hide_index=True)
        #Hier wird der Output der Query gespeichert
        ergebnis_df_to_ai_variable = ergebnis_df.to_csv(index=False)

        #Ergebnis der Query als rohes SQL, user_input und Daten als csv Datei werden berarbietet
        if ergebnis_df_to_ai_variable: 
            with st.spinner("Formuliere Antwort..."):
                antwort_text = ask_ai.explain_result(
                sql_query=sql_query, 
                users_question_input=user_input, 
                query_data_csv=ergebnis_df_to_ai_variable
                )
        
        # 3. Antwort anzeigen
            st.markdown(f"### 🤖 Antwort:\n{antwort_text}")
            
    except Exception as e:
        st.error(f"Fehler bei der Anfrage: {e}")






