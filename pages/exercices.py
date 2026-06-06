import streamlit as st
import pandas as pd
import numpy as np
import psycopg2

st.set_page_config(page_title="Exercices", page_icon="🏋️‍♀️")
st.title("Gère tes entrainements 💪")
st.markdown("""Renseigne les exercices faits au cours de tes séances.""")


# Connexion à PostgreSQL via les secrets Streamlit
@st.cache_resource
def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

conn = get_connection()

# Choix de la séances
with conn.cursor() as cur:
    cur.execute("SELECT training_id, date FROM trainings;")
    trainings = pd.DataFrame(cur.fetchall(), columns=["id", "date"])
    t = st.selectbox("Choix de la séance", trainings.iloc[:, 1])
    st.markdown("#")
    training_id = trainings[trainings["date"] == t]["id"].tolist()[0]
    conn.commit()


# Ajouter des séries
st.write("Ajoute des séries pour ta séance sélectionnée 💪")

with (conn.cursor() as cur):
    cur.execute("SELECT body_id, reference_exercice FROM body;")
    body = pd.DataFrame(cur.fetchall(), columns=["id", "reference"])
    list_body = np.sort(body["reference"])
    st.session_state['list_body'] = list_body
    conn.commit()


col1, col2, col3, col4 = st.columns(4)
with col1:
    exercice = st.selectbox("Exercice 🏋", list_body)
    body_id = body[body["reference"] == exercice]["id"].tolist()[0]
with col2:
    serie = st.slider("Séries 🔢", 1, 10)
with col3:
    weight = st.text_input("Poids 🧲")
with col4:
    repetition = st.slider("Répétition 🔢", 1, 25)

enter = st.button("Ajoute ton exercice")

if enter and weight != "":
    with conn.cursor() as cur:
        for i in range(serie):
            cur.execute("INSERT INTO exercices (training_id, body_id, weight, repetitions) VALUES (%s, %s, %s, %s);", (training_id, body_id, weight, repetition))
    conn.commit()
    st.success("Ton exercice est ajouté, au suivant 💪.")

elif enter and weight == "":
    st.error("Tu n'as pas renseigné les informations nécessaires.")