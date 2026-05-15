import streamlit as st
import psycopg2

# Connexion à PostgreSQL via les secrets Streamlit
@st.cache_resource
def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

conn = get_connection()

st.title("Mon app avec PostgreSQL")

# Lire des données
with conn.cursor() as cur:
    cur.execute("SELECT * FROM utilisateurs LIMIT 10;")
    rows = cur.fetchall()
    st.dataframe(rows)

# Insérer des données
nom = st.text_input("Nom")
if st.button("Ajouter") and nom:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO utilisateurs (nom) VALUES (%s);", (nom,))
    conn.commit()
    st.success(f"{nom} ajouté !")