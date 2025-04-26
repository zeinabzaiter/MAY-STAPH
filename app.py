import streamlit as st
import pandas as pd
import plotly.express as px

# Charger les données corrigées
df = pd.read_excel('staph_aureus_pheno_final.xlsx')

# Corriger les dates
df['Semaine'] = pd.to_datetime(df['Semaine'], errors='coerce')

# Supprimer les lignes où la date n'est pas valide
df = df.dropna(subset=['Semaine'])

# Colonnes à forcer en numérique
for col in ['MRSA', 'VRSA', 'Wild', 'Other']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Créer la colonne Mois pour filtrer
df['Mois'] = df['Semaine'].dt.to_period('M').astype(str)

# Calcul total
df['Total'] = df[['MRSA', 'VRSA', 'Wild', 'Other']].sum(axis=1)

# Calcul pourcentages
df['% MRSA'] = df['MRSA'] / df['Total'] * 100
df['% VRSA'] = df['VRSA'] / df['Total'] * 100
df['% Wild'] = df['Wild'] / df['Total'] * 100
df['% Other'] = df['Other'] / df['Total'] * 100

# Dashboard Streamlit
st.set_page_config(page_title="Dashboard Staph", layout="wide")
st.title("📈 Dashboard Hebdomadaire - Staphylococcus aureus")

# Filtres
mois_selectionnes = st.sidebar.multiselect("Mois :", options=df['Mois'].unique(), default=list(df['Mois'].unique()))
phenotypes_selectionnes = st.sidebar.multiselect("Phénotypes :", options=['MRSA', 'VRSA', 'Wild', 'Other'], default=['MRSA', 'VRSA', 'Wild', 'Other'])

# Appliquer filtres
df_filtre = df[df['Mois'].isin(mois_selectionnes)]

# Graphique
fig = px.line(
    df_filtre,
    x='Semaine',
    y=phenotypes_selectionnes,
    markers=True,
    title="Évolution des Phénotypes par semaine",
    color_discrete_map={
        'MRSA': 'orange',
        'VRSA': 'red',
        'Wild': 'green',
        'Other': 'blue'
    }
)
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# Détails
st.dataframe(df_filtre)

