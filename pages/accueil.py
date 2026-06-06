import streamlit as st
import psycopg2

st.set_page_config(page_title="Accueil", page_icon="🏋️‍♀️")
st.title("Application de musculation 💪")
st.markdown("""Déclare tes dernières séances à la salle et optimise tes performances.""")



# Connexion à PostgreSQL via les secrets Streamlit
@st.cache_resource
def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

conn = get_connection()


# Lire des données
with conn.cursor() as cur:
    cur.execute("SELECT count(*) FROM trainings;")
    nb_trainings = cur.fetchall()[0][0]

    cur.execute("SELECT count(*) FROM trainings WHERE stretching=1;")
    nb_stretching = cur.fetchall()[0][0]
    perf_stretching = round(nb_stretching / nb_trainings * 100, 1)

    cur.execute("SELECT count(*) FROM trainings WHERE hydrate=1;")
    nb_hydrate = cur.fetchall()[0][0]
    perf_hydrate = round(nb_hydrate / nb_trainings * 100, 1)

    conn.commit()

# Informations générales
st.write(f"Tu as déjà fait :red[{nb_trainings}] séances, avec une régularité dans les étirements à hauteur "
         f"de :red[{perf_stretching}] % et dans l'hydratation à hauteur de :red[{perf_hydrate}] % .")
st.markdown("#")


# Déclarer une séance
st.write("Ajoute maintenant de nouvelles séances.")

date = st.date_input("Date de la séance ⏱", value=None)

col1, col2 = st.columns(2)
with col1:
    stretch = st.radio("Etirements 🧘‍♂️", ["Oui", "Non"])
    stretch = 1 if stretch == "Oui" else 0
with col2:
    hydrate = st.radio("Hydratation 🥤", ["Oui", "Non"])
    hydrate = 1 if hydrate == "Oui" else 0

enter = st.button("Créer la séance")

if enter and date:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO trainings (date, stretching, hydrate) VALUES (%s, %s, %s);", (date, stretch, hydrate))
    conn.commit()
    st.success("La séance est ajoutée, tu peux maintenant y associer les excercies.")

elif enter and date is None:
    st.error("Tu n'as pas choisi de date.")
