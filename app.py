import streamlit as st
import pandas as pd
import plotly.express as px

# --- Charger les données ---
df = pd.read_excel('staph_aureus_pheno_final.xlsx', header=0)

# Nettoyer les colonnes
df.columns = df.columns.str.strip()

# Forcer les colonnes numériques
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

# --- Calcul des alertes Tukey ---
# MRSA
q1_mrsa = df['MRSA'].quantile(0.25)
q3_mrsa = df['MRSA'].quantile(0.75)
iqr_mrsa = q3_mrsa - q1_mrsa
seuil_mrsa = q3_mrsa + 1.5 * iqr_mrsa

# VRSA
q1_vrsa = df['VRSA'].quantile(0.25)
q3_vrsa = df['VRSA'].quantile(0.75)
iqr_vrsa = q3_vrsa - q1_vrsa
seuil_vrsa = q3_vrsa + 1.5 * iqr_vrsa

df['MRSA_alerte'] = df['MRSA'] > seuil_mrsa
df['VRSA_alerte'] = df['VRSA'] > seuil_vrsa

# --- Configuration de la page ---
st.set_page_config(page_title="Dashboard Surveillance MRSA/VRSA", layout="wide")
st.title("🔍 Surveillance des Phénotypes Staphylococcus aureus - 2024")

# --- Filtres dynamiques ---
st.sidebar.header("Filtres")
mois_selectionnes = st.sidebar.multiselect(
    "Sélectionner le(s) mois :",
    options=df['Mois'].unique(),
    default=list(df['Mois'].unique())  # Correction ici
)

phenotypes_selectionnes = st.sidebar.multiselect(
    "Sélectionner les phénotypes :", 
    options=['Wild', 'Other', 'MRSA', 'VRSA'],
    default=['Wild', 'Other', 'MRSA', 'VRSA']  # Correction ici
)

# Appliquer les filtres
df_filtre = df[df['Mois'].isin(mois_selectionnes)]

# --- Debug affichage rapide ---
st.write("🔎 Aperçu des données filtrées :")
st.dataframe(df_filtre)

# --- Panneau Alerte ---
alertes_detectees = []

for idx, row in df_filtre.iterrows():
    if row['MRSA_alerte']:
        alertes_detectees.append(f"🚨 Alerte MRSA détectée semaine du {row['Semaine'].date()}")
    if row['VRSA_alerte']:
        alertes_detectees.append(f"🚨 Alerte VRSA détectée semaine du {row['Semaine'].date()}")

if alertes_detectees:
    st.error('⚠️ Attention : Alertes détectées !')
    for alerte in alertes_detectees:
        st.write(alerte)

# --- Indicateurs Clés ---
st.header("Indicateurs Clés")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total MRSA", int(df_filtre['MRSA'].sum()))
col2.metric("Total VRSA", int(df_filtre['VRSA'].sum()))
col3.metric("Alertes MRSA", int(df_filtre['MRSA_alerte'].sum()))
col4.metric("Alertes VRSA", int(df_filtre['VRSA_alerte'].sum()))

# --- Graphique principal ---
st.header("📈 Évolution Hebdomadaire des Phénotypes sélectionnés")
fig = px.line(
    df_filtre,
    x='Semaine',
    y=phenotypes_selectionnes,
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
fig.update_layout(hovermode="x unified", title_text="Évolution des Phénotypes par Semaine", title_x=0.5)
fig.update_xaxes(type='date')
fig.update_yaxes(rangemode='tozero')
st.plotly_chart(fig, use_container_width=True)

# --- Détails Alertes ---
st.header("📋 Détail des Alertes")
st.dataframe(df_filtre[['Semaine', 'MRSA', 'MRSA_alerte', 'VRSA', 'VRSA_alerte', 'Wild', 'Other']])

# --- Bouton de téléchargement ---
st.download_button(
    label="📥 Télécharger les données filtrées",
    data=df_filtre.to_csv(index=False).encode('utf-8'),
    file_name='resultats_filtres.csv',
    mime='text/csv'
)
