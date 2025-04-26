import streamlit as st
import pandas as pd
import plotly.express as px

# --- Charger les données ---
df = pd.read_excel('staph_aureus_pheno_final.xlsx', header=0)

# Nettoyer les colonnes
df.columns = df.columns.str.strip()

# Forcer les colonnes en numérique
colonnes_a_convertir = ['MRSA', 'VRSA', 'Wild', 'Other']
for col in colonnes_a_convertir:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Corriger la colonne date
df['Semaine'] = pd.to_datetime(df['Semaine'], errors='coerce')

# Supprimer les lignes sans dates valides
df = df.dropna(subset=['Semaine'])

# Ajouter la colonne Mois
df['Mois'] = df['Semaine'].dt.to_period('M').astype(str)

# Calculer le total isolats
df['Total'] = df['MRSA'] + df['VRSA'] + df['Wild'] + df['Other']

# Calcul des pourcentages
df['% MRSA'] = (df['MRSA'] / df['Total']) * 100
df['% VRSA'] = (df['VRSA'] / df['Total']) * 100
df['% Wild'] = (df['Wild'] / df['Total']) * 100
df['% Other'] = (df['Other'] / df['Total']) * 100

# Définir les seuils d'alerte
seuil_mrsa = 31.875
seuil_vrsa = 2.5
df['MRSA_alerte'] = df['MRSA'] > seuil_mrsa
df['VRSA_alerte'] = df['VRSA'] > seuil_vrsa

# --- Configuration de la page ---
st.set_page_config(page_title="Dashboard Surveillance MRSA/VRSA", layout="wide")
st.title("🔍 Surveillance des Phénotypes Staphylococcus aureus - 2024")

# --- Filtres Mois ---
mois_selectionnes = st.multiselect(
    "Sélectionner le(s) mois :",
    options=df['Mois'].unique(),
    default=df['Mois'].unique()
)

df_filtre = df[df['Mois'].isin(mois_selectionnes)]

# --- Indicateurs Clés ---
st.header("Indicateurs Clés")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total MRSA", df_filtre['MRSA'].sum())
col2.metric("Total VRSA", df_filtre['VRSA'].sum())
col3.metric("Alertes MRSA", int(df_filtre['MRSA_alerte'].sum()))
col4.metric("Alertes VRSA", int(df_filtre['VRSA_alerte'].sum()))

# --- Graphique MRSA et VRSA ---
st.header("📈 Évolution Hebdomadaire MRSA et VRSA")
fig1 = px.line(
    df_filtre,
    x='Semaine',
    y=['MRSA', 'VRSA'],
    labels={'value': 'Nombre', 'variable': 'Phénotype'},
    markers=True,
    hover_data={
        'Semaine': True,
        'MRSA': ':.0f',
        'VRSA': ':.0f',
        '% MRSA': ':.2f',
        '% VRSA': ':.2f'
    }
)
fig1.update_layout(hovermode="x unified", title_text="MRSA et VRSA par semaine", title_x=0.5)
fig1.update_xaxes(type='date')
fig1.update_yaxes(rangemode='tozero')
st.plotly_chart(fig1, use_container_width=True)

# --- Graphique Tous Phénotypes ---
st.header("📊 Évolution Hebdomadaire de Tous les Phénotypes")
fig2 = px.line(
    df_filtre,
    x='Semaine',
    y=['Wild', 'Other', 'MRSA', 'VRSA'],
    labels={'value': 'Nombre de cas', 'variable': 'Phénotype'},
    markers=True,
    color_discrete_map={
        'Wild': 'green',
        'Other': 'blue',
        'MRSA': 'orange',
        'VRSA': 'red'
    },
    hover_data={
        'Semaine': True,
        'Wild': ':.0f',
        'Other': ':.0f',
        'MRSA': ':.0f',
        'VRSA': ':.0f',
        '% Wild': ':.2f',
        '% Other': ':.2f',
        '% MRSA': ':.2f',
        '% VRSA': ':.2f'
    }
)
fig2.update_layout(hovermode="x unified", title_text="Évolution des Phénotypes par Semaine", title_x=0.5)
fig2.update_xaxes(type='date')
fig2.update_yaxes(rangemode='tozero')
st.plotly_chart(fig2, use_container_width=True)

# --- Tableau des Alertes ---
st.header("📋 Détails des Alertes")
st.dataframe(df_filtre[['Semaine', 'MRSA', 'MRSA_alerte', 'VRSA', 'VRSA_alerte', 'Wild', 'Other']])

# --- Bouton Téléchargement ---
st.download_button(
    label="📥 Télécharger les données filtrées",
    data=df_filtre.to_csv(index=False).encode('utf-8'),
    file_name='resultats_filtres.csv',
    mime='text/csv'
)
