import streamlit as st
import pandas as pd
import plotly.express as px

# --- Charger les données ---
df = pd.read_excel('staph_aureus_pheno_final.xlsx')

# --- Préparation des données ---
# Renommer la colonne date pour plus de clarté
df = df.rename(columns={df.columns[0]: 'Semaine'})

# Calculer le total isolats par semaine
df['Total'] = df['MRSA'] + df['VRSA'] + df['Wild'] + df['Other']

# Calculer les %
df['% MRSA'] = (df['MRSA'] / df['Total']) * 100
[df['% VRSA'] = (df['VRSA'] / df['Total']) * 100

# --- Titre ---
st.set_page_config(page_title="Dashboard Surveillance MRSA/VRSA", layout="wide")
st.title("🔍 Surveillance des Phénotypes Staphylococcus aureus - 2024")

# --- Filtres ---
semaines = st.multiselect("Sélectionner les semaines :", options=df['Semaine'].unique(), default=df['Semaine'].unique())

# Filtrer les données
df_filtre = df[df['Semaine'].isin(semaines)]

# --- KPIs ---
st.header("Indicateurs Clés")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total MRSA", df_filtre['MRSA'].sum())
col2.metric("Total VRSA", df_filtre['VRSA'].sum())
col3.metric("Alertes MRSA", int(df_filtre['MRSA_alerte'].sum()))
col4.metric("Alertes VRSA", int(df_filtre['VRSA_alerte'].sum()))

# --- Graphique Interactif MRSA + VRSA ---
st.header("📊 Évolution Hebdomadaire")

fig = px.line(df_filtre, x='Semaine', y=['MRSA', 'VRSA'],
              labels={'value': 'Nombre', 'variable': 'Phénotype'},
              markers=True,
              hover_data={
                  'Semaine': True,
                  'MRSA': ':.0f',
                  'VRSA': ':.0f',
                  '% MRSA': ':.2f',
                  '% VRSA': ':.2f'
              })

fig.update_layout(hovermode="x unified", title_text="MRSA et VRSA par semaine", title_x=0.5)

st.plotly_chart(fig, use_container_width=True)

# --- Tableau Alertes ---
st.header("📊 Détails des Alertes")
st.dataframe(df_filtre[['Semaine', 'MRSA', 'MRSA_alerte', 'VRSA', 'VRSA_alerte', 'Wild', 'Other']])
