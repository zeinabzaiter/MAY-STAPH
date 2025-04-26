import streamlit as st
import pandas as pd
import plotly.express as px

# --- Charger les données ---
df = pd.read_excel('staph_aureus_pheno_final.xlsx')

# --- Forcer le bon nom de colonne ---
df.rename(columns={df.columns[0]: 'Semaine'}, inplace=True)

# --- Nettoyage ---
df['Semaine'] = pd.to_datetime(df['Semaine'], errors='coerce')
df = df.dropna(subset=['Semaine'])

# Forcer les colonnes numériques
for col in ['MRSA', 'VRSA', 'Wild', 'Other']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Ajouter numéro de semaine
df['Num_semaine'] = df['Semaine'].dt.isocalendar().week

# Ajouter Mois
df['Mois'] = df['Semaine'].dt.to_period('M').astype(str)

# Calculer le total
df['Total'] = df[['MRSA', 'VRSA', 'Wild', 'Other']].sum(axis=1)

# Calcul des pourcentages
df['% MRSA'] = (df['MRSA'] / df['Total']) * 100
df['% VRSA'] = (df['VRSA'] / df['Total']) * 100
df['% Wild'] = (df['Wild'] / df['Total']) * 100
df['% Other'] = (df['Other'] / df['Total']) * 100

# --- Calcul des alertes par Tukey ---
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

# --- Config Streamlit ---
st.set_page_config(page_title="Dashboard Staphylococcus aureus", layout="wide")
st.title("📈 Dashboard Hebdomadaire - Staphylococcus aureus")

# --- Filtres ---
st.sidebar.header("Filtres")
mois_selectionnes = st.sidebar.multiselect(
    "Sélectionner le(s) mois :",
    options=df['Mois'].unique(),
    default=list(df['Mois'].unique())
)

phenotypes_selectionnes = st.sidebar.multiselect(
    "Sélectionner les phénotypes :",
    options=['MRSA', 'VRSA', 'Wild', 'Other'],
    default=['MRSA', 'VRSA', 'Wild', 'Other']
)

# --- Application des filtres ---
df_filtre = df[df['Mois'].isin(mois_selectionnes)]

# --- Graphique ---
st.header("📊 Évolution Hebdomadaire des Phénotypes sélectionnés")

fig = px.line(
    df_filtre,
    x='Num_semaine',
    y=phenotypes_selectionnes,
    markers=True,
    labels={'value': 'Nombre de cas', 'Num_semaine': 'Semaine', 'variable': 'Phénotype'},
    color_discrete_map={
        'MRSA': 'orange',
        'VRSA': 'red',
        'Wild': 'green',
        'Other': 'blue'
    }
)
fig.update_layout(
    hovermode="x unified",
    title_text="Évolution des Phénotypes par Semaine",
    title_x=0.5
)
fig.update_xaxes(dtick=1, title='Semaine')
fig.update_yaxes(range=[0, 100], title='Nombre de cas (%)')  # Y de 0 à 100

st.plotly_chart(fig, use_container_width=True)

# --- Alertes ---
if df_filtre['MRSA_alerte'].any() or df_filtre['VRSA_alerte'].any():
    st.error("🚨 ALERTE : Dépassement seuil Tukey détecté sur certaines semaines.")
    st.dataframe(df_filtre[['Semaine', 'MRSA', 'MRSA_alerte', 'VRSA', 'VRSA_alerte']])
else:
    st.success("✅ Aucune alerte détectée.")

# --- Détail des données ---
st.header("📝 Détail des Données Filtrées")
st.dataframe(df_filtre)

