"""
@author : Philippe. PETIT
@version : 2.0.2
@Description : Tableau de bord comptable (import de fichier csv formaté)
@format : Entete CSV:  [
    'Sens', 'Section', 'Chapitre', 'Libellé_budget', 'Compte',
    'Total_Prévu', 'Réalisé', 'Reste_engagé',
    'Liquidé_N_1', 'Liquidé_N_2', 'Liquidé_N_3', 'Liquidé_N_4', 'Liquidé_N_5'
]
"""

import sys
from pathlib import Path

# =====================================================
# CONFIGURATION DU PATH
# =====================================================

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# =====================================================
# IMPORTS
# =====================================================

import streamlit as st

from core.loader import load_csv
from core.loader_grand_livre import load_grand_livre
from core.calculs import calculer_sommes_par_chapitre, calcul_autofinancement

from ui.sidebar import filtres
from ui.cards import afficher_indicateurs, badge, badgeRed, badgeGreen, badgeBlue
from ui.tables import tableau_chapitres,voir_detail_chapitre
from ui.graphs import camembert


# =====================================================
# CONFIG STREAMLIT
# =====================================================

st.set_page_config(layout="wide", page_title="Tableau de bord comptable M57")

# =====================================================
# HEADER
# =====================================================

logo_path = ROOT_DIR / "assets" / "logo.png"
st.image(str(logo_path), width=480)

st.title("📊 Tableau de bord comptable – M57")
st.caption(
    "Version 2.00.02 Stable | Tableau de bord comptable [M57] | Auteur : Philippe PETIT | 06/02/2026"
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    # -----------------------------
    # CHARGEMENT DES FICHIERS
    # -----------------------------
    with st.expander("📂 Chargement des données", expanded=True):

        file = st.file_uploader(
            "📁 Fichier CSV principal",
            type="csv"
        )

     



# =====================================================
# SI PAS DE FICHIER → STOP
# =====================================================

if not file:
    st.info("⬅️ Chargez le fichier principal dans le panneau de gauche.")
    st.stop()

# =====================================================
# CHARGEMENT DONNÉES
# =====================================================

df, annees = load_csv(file)

# =====================================================
# FILTRES (SIDEBAR)
# =====================================================

with st.sidebar:
    with st.expander("🔎 Filtres", expanded=True):
        budget, section, sens, population = filtres(df)

# =====================================================
# FILTRAGE
# =====================================================

df_filtre = df[
    (df["Libellé_budget"] == budget) &
    (df["Section"] == section) &
    (df["Sens"] == sens)
]

#st.write(df_filtre)

# =====================================================
# CALCULS
# =====================================================

sommes, report_a_nouveau,report_a_nouveau_invest = calculer_sommes_par_chapitre(
    df_filtre,
    annees
)

total_budget = df_filtre["Total_Prévu"].sum()

if section == "F" and sens == "R":
    total_realise = df_filtre["Réalisé"].sum() - report_a_nouveau 
else:
    if section == "I" and sens == "R":
        total_realise = df_filtre["Réalisé"].sum() - report_a_nouveau_invest 
    else:
        total_realise = df_filtre["Réalisé"].sum()

reste_engage = df_filtre["Reste_engagé"].sum()

ratio = (total_realise + reste_engage) / population
taux = (total_realise / total_budget * 100) if total_budget else 0

# =====================================================
# INDICATEURS
# =====================================================

afficher_indicateurs(
    total_budget,
    total_realise,
    reste_engage,
    ratio,
    taux
)

st.divider()

# =====================================================
# TABLEAU
# =====================================================

# Appel unique de la fonction tableau_chapitres
df_tableau = tableau_chapitres(
    df,
    budget=budget,
    section=section,
    sens=sens
)


st.divider()

# =====================================================
# GRAPHIQUE
# =====================================================

camembert(df_filtre)

st.divider()

# =====================================================
# AUTO-FINANCEMENT
# =====================================================

st.subheader(f"💰 Auto-financement ({budget})")

auto = calcul_autofinancement(df,budget)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    badge("Marge brute", auto["Marge brute"])

with c2:
    badge("Épargne brute", auto["Epargne brute"])
    
with c3:
    badgeRed("Dont produits exceptionnels", auto["Dont produits exceptionnels"])

with c4:
    badgeGreen("Épargne nette", auto["Epargne nette"])

with c5:
    badgeBlue("Report N-1", auto["Report N -1"])

with c6:
    badgeGreen("Epargne disponible", auto["Disponibilité"])
