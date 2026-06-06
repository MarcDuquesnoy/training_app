import plotly.graph_objs as go
import streamlit as st
import pandas as pd
import numpy as np
import psycopg2

st.set_page_config(page_title="Performances", page_icon="🏋️‍♀️")
st.title("Optimise tes séances 💪")
st.markdown("""Analyse les exercices faits au cours de tes séances.""")

# Connexion à PostgreSQL via les secrets Streamlit
@st.cache_resource
def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

conn = get_connection()

# Choix de la séances
with conn.cursor() as cur:
    cur.execute("SELECT distinct reference_body FROM body;")
    body = pd.DataFrame(cur.fetchall(), columns=["reference"])
    list_body = np.sort(body["reference"])
    conn.commit()


exercice = st.selectbox("Partie du corps 🏋", list_body)

# Tableau récapitulatif
with conn.cursor() as cur:
    cur.execute("""select body.reference_exercice
                  , avg(exercices.weight) as avg_weight
                  , max(exercices.weight) as max_weight
                  , avg(exercices.repetitions) as avg_rep
                  , max(exercices.repetitions) as max_rep
                  , count(*)
                from
                  exercices
                left join 
                  body
                on 
                  body.body_id = exercices.body_id
                where 
                  body.reference_body = '""" + exercice + """'
                group by 
                  body.reference_exercice
                order by 
                  count(*)
                desc"""
    )
    results = pd.DataFrame(cur.fetchall(), columns=["exercice", "avg_weight", "max_weight", "avg_rep", "max_rep", "total"])
    conn.commit()

#Figure n°1
fig = go.Figure(go.Bar(x=results["total"], y=results["exercice"], orientation='h',
                       marker_line=dict(width=0.5, color='black'),
                       marker=dict(color=results["total"], colorscale="sunsetdark_r", showscale=False,
                                   colorbar=dict(title="value"))
                       ))
fig.update_layout(barmode='stack', yaxis={'categoryorder': 'total descending'},
                  title=dict(text="Répartition des exercices pour : " + exercice), )
fig.update_yaxes(tickfont=dict(size=15, color="white"))
fig.update_xaxes(tickfont=dict(size=10, color="white"))
st.plotly_chart(fig)

# Tableau n°1
st.data_editor(
        results[["exercice", "avg_weight", "max_weight", "avg_rep", "max_rep"]],
        column_config={
            "evolution": st.column_config.BarChartColumn(
                "Répartition globale",
                help="Répartition globale",
                y_min=0,
                y_max=81,
            ),
        },
        hide_index=True,
    )


choice = st.selectbox("Exercice 🏋", st.session_state['list_body'])

# Tableau récapitulatif
with conn.cursor() as cur:
    cur.execute("""select weight
                  , repetitions
                from 
                  exercices
                left join 
                  trainings
                on 
                  trainings.training_id = exercices.exercice_id
                left join 
                  body
                on 
                  body.body_id = exercices.body_id
                where 
                  body.reference_exercice = '""" + choice + """'
                order by
                  trainings.created_at
                asc"""
    )
    evolution = pd.DataFrame(cur.fetchall(), columns=["weight", "repetitions"])
    conn.commit()

# Figure n°2
fig = go.Figure(go.Scattergl(
        y=evolution["weight"].rolling(window=20).mean(),
        name='Original',
        mode='lines+markers',
        line={'color': '#fbde9c'},
        connectgaps=True
))
fig.update_layout(title=dict(text="Evolution moyenne du poids soulevé (20 séries)"),
                  yaxis_title=dict(text='Poids', font=dict(size=16, color='white')),
                  xaxis_title=dict(text='Séries', font=dict(size=16, color='white')))
fig.update_yaxes(tickfont=dict(size=15, color="white"))
fig.update_xaxes(tickfont=dict(size=2, color="white"))
st.plotly_chart(fig)


fig = go.Figure(go.Scattergl(
        y=evolution["repetitions"].rolling(window=20).mean(),
        name='Original',
        mode='lines+markers',
        line={'color': '#fbde9c'},
        connectgaps=True
))
fig.update_layout(title=dict(text="Evolution moyenne du nombre de répétitions (20 séries)"),
                  yaxis_title=dict(text='Répétitions', font=dict(size=16, color='white')),
                  xaxis_title=dict(text='Séries', font=dict(size=16, color='white')))
fig.update_yaxes(tickfont=dict(size=15, color="white"))
fig.update_xaxes(tickfont=dict(size=2, color="white"))
st.plotly_chart(fig)
