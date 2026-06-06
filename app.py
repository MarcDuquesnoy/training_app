import streamlit as st
import psycopg2

def main():
    pg = st.navigation([
        st.Page("pages/accueil.py", title="Accueil", icon="🏋️‍♀️"),
        st.Page("pages/exercices.py", title="Exercices", icon="🙋‍♂️️"),
        st.Page("pages/performances.py", title="Performances", icon="〽️️"),
    ])

    pg.run()

if __name__ == "__main__":
    main()