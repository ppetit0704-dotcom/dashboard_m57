# =====================================================
# IMPORTS
# =====================================================

import streamlit as st
from pathlib import Path

ROOT_DIR = Path(__file__).parent

from core.loader import load_csv
from core.loader_grand_livre import load_grand_livre
from core.calculs import calculer_sommes_par_chapitre, calcul_autofinancement

from ui.sidebar import filtres
from ui.cards import afficher_indicateurs, badge, badgeRed, badgeGreen, badgeBlue
from ui.tables import tableau_chapitres
from ui.graphs import camembert


# =====================================================
# CONFIG STREAMLIT
# =====================================================

st.set_page_config(
    layout="wide",
    page_title="Dashboard comptable M57"
)

# =====================================================
# ETAT APPLICATION
# =====================================================

if "acces_dashboard" not in st.session_state:
    st.session_state.acces_dashboard = False


# =====================================================
# PAGE D'ACCUEIL
# =====================================================

logo_path = "assets/logo.png"

if not st.session_state.acces_dashboard:

    st.image(str(logo_path), width=480)

    st.title("📊 Tableau de bord comptable – M57")

    st.markdown("""
    ### Bienvenue

    Cet outil permet l'analyse du budget communal au format M57 :

    - Suivi des réalisations budgétaires
    - Analyse par chapitres
    - Indicateurs d'auto-financement
    - Visualisation graphique

    L'accès est réservé aux utilisateurs autorisés.
    """)

    if st.button("🔐 Accéder au tableau de bord"):
        st.session_state.acces_dashboard = True
        st.rerun()

    st.stop()


# =====================================================
# AUTHENTIFICATION GOOGLE (STREAMLIT CLOUD)
# =====================================================

if not st.user.is_logged_in:

    st.title("🔐 Connexion requise")
    st.info("Veuillez vous connecter avec votre compte Google.")

    st.login()
    st.stop()


# -----------------------------------------------------
# FILTRAGE OPTIONNEL DES EMAILS AUTORISÉS
# -----------------------------------------------------

emails_autorises = [
    "prenom.nom@ville.fr",
    "admin@ville.fr"
]

if emails_autorises and st.user.email not in emails_autorises:
    st.error("⛔ Accès non autorisé")
    st.stop()


# =====================================================
# HEADER
# =====================================================

st.image(str(logo_path), width=480)

st.title("📊 Tableau de bord comptable – M57")
st.caption(
    "Version 2.00.01 Stable | Tableau de bord comptable [M57] | Auteur : P. PETIT | 06/02/2026"
)


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.success(f"Connecté : {st.user.name}")

    if st.button("🔓 Se déconnecter"):
        st.logout()

    st.divider()

    with st.expander("📂 Chargement des données", expanded=True):

        file = st.file_uploader(
            "📁 Fichier CSV principal",
            type="csv"
        )

        st.markdown("---")

        st.caption(
            "Pour afficher le détail des écritures par compte, "
            "chargez le fichier 'Edition_du_grand_livre.CSV'"
        )

        if "df_grand_livre" not in st.session_state:
            st.session_state.df_grand_livre = None

        file_gl = st.file_uploader(
            "📝 Grand Livre (optionnel)",
            type="csv",
            key="grand_livre_uploader"
        )


# =====================================================
# CHARGEMENT GRAND LIVRE
# =====================================================

if file_gl and st.session_state.df_grand_livre is None:
    with st.spinner("Chargement du grand livre..."):
        st.session_state.df_grand_livre = load_grand_livre(file_gl)

        if st.session_state.df_grand_livre is not None:
            st.success(
                f"✅ Grand livre chargé : "
                f"{len(st.session_state.df_grand_livre)} écritures"
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


# =====================================================
# CALCULS
# =====================================================

sommes, report_a_nouveau, report_a_nouveau_invest = calculer_sommes_par_chapitre(
    df_filtre,
    annees
)

total_budget = df_filtre["Total_Prévu"].sum()

if section == "F" and sens == "R":
    total_realise = df_filtre["Réalisé"].sum() - report_a_nouveau
elif section == "I" and sens == "R":
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

tableau_chapitres(
    df_filtre,
    annees,
    budget,
    section,
    sens,
    st.session_state.df_grand_livre
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

st.subheader("💰 Auto-financement (Budget communal)")

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

