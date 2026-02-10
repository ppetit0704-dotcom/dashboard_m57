# -*- coding: utf-8 -*-
"""
Created on Sun Feb  8 11:26:02 2026

@author: P.PETIT
"""

# -*- coding: utf-8 -*-
"""
Module tables.py
@author: P.PETIT
"""

import streamlit as st
import pandas as pd
from ui.graphs import camembert_detail
from core.loader_grand_livre import get_ecritures_compte

# --- FONCTION UTILE POUR SOMME SÉCURISÉE ---
def safe_sum(df, col):
    """
    Retourne une somme numérique sécurisée pour une colonne.
    Compatible Series, DataFrame ou object.
    """
    if col not in df.columns:
        return 0.0

    serie = df[col]

    # si pandas renvoie un DataFrame (colonnes dupliquées)
    if isinstance(serie, pd.DataFrame):
        serie = serie.iloc[:, 0]

    return pd.to_numeric(serie, errors="coerce").sum()


# --- STYLE ---
st.markdown("""
<style>
.detail-box {
    background-color: #f2f2f2;
    padding: 1rem 1.2rem;
    border-radius: 6px;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #b0b0b0;
}

.detail-box-title {
    font-weight: 600;
    margin-bottom: 0.2rem;
}

.detail-box-subtitle {
    color: #555;
    font-size: 0.9rem;
}

.ecriture-box {
    background-color: #e8f4f8;
    padding: 0.8rem 1rem;
    border-radius: 4px;
    margin-top: 0.3rem;
    margin-bottom: 0.8rem;
    border-left: 3px solid #4a90a4;
}
</style>
""", unsafe_allow_html=True)


# Colonnes Liquidé
COLS_LIQUIDE = [f"Liquidé_N_{i}" for i in range(1, 6)]


# --- Tableau des chapitres avec Détails ---
def tableau_chapitres(df, annees, budget, section, sens, df_grand_livre=None):

    cols_base = ["Total_Prévu", "Réalisé", "Reste_engagé"]
    cols_liquide = [c for c in COLS_LIQUIDE if c in df.columns]
    cols_annees = [c for c in annees if c in df.columns]

    cols_numeriques = cols_base + cols_liquide + cols_annees

    # Sécurisation conversion numérique
    for col in cols_numeriques:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Agrégation par chapitre
    table = df.groupby("Chapitre")[cols_numeriques].sum().reset_index()

    # État ouvert/fermé
    if "chapitres_ouverts" not in st.session_state:
        st.session_state.chapitres_ouverts = {}

    st.subheader("📋 Tableau des chapitres")

    # ---- ENTÊTE ----
    header_cols = st.columns([2] + [2] * len(cols_base + cols_liquide) + [1])
    header_cols[0].markdown("**Chapitre**")
    for i, col in enumerate(cols_base + cols_liquide, start=1):
        header_cols[i].markdown(f"**{col.replace('_', ' ')}**")
    header_cols[-1].markdown("**Détails**")

    # ---- LIGNES ----
    for idx, row in table.iterrows():
        cols = st.columns([2] + [2] * len(cols_base + cols_liquide) + [1])
        cols[0].write(row["Chapitre"])

        for i, col in enumerate(cols_base + cols_liquide, start=1):
            valeur = row[col]
            if isinstance(valeur, pd.Series):  # si par hasard c'est une Series
                valeur = valeur.sum()
            valeur = 0.0 if pd.isna(valeur) else float(valeur)

            cols[i].write(f"{valeur:,.2f} €".replace(",", " "))

        # Bouton détail
        if cols[-1].button(
            "..." if not st.session_state.chapitres_ouverts.get(idx, False) else "...",
            key=f"detail_{idx}"
        ):
            st.session_state.chapitres_ouverts[idx] = not st.session_state.chapitres_ouverts.get(idx, False)

        # Affichage détail
        if st.session_state.chapitres_ouverts.get(idx, False):
            voir_detail_chapitre(df, budget, section, sens, row["Chapitre"], df_grand_livre)

    # ---- RAPPEL ENTÊTE AVANT TOTAL ----
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    header_cols = st.columns([2] + [2] * len(cols_base + cols_liquide) + [1])
    header_cols[0].markdown("**Chapitre**")
    for i, col in enumerate(cols_base + cols_liquide, start=1):
        header_cols[i].markdown(f"**{col.replace('_', ' ')}**")
    header_cols[-1].markdown("**Détails**")

    # ---- LIGNE TOTAL ----
    total_cols = st.columns([2] + [2] * len(cols_base + cols_liquide) + [1])
    total_cols[0].markdown(
        '<div style="background-color:#f0f0f0; font-weight:bold; padding:0.3rem;color:black">TOTAL</div>',
        unsafe_allow_html=True
    )
    for i, col in enumerate(cols_base + cols_liquide, start=1):
        total_val = safe_sum(table, col)
        total_cols[i].markdown(
            f'<div style="background-color:#f0f0f0; font-weight:bold; text-align:right; padding:0.3rem;color:black;">{total_val:,.2f} €</div>',
            unsafe_allow_html=True
        )
    total_cols[-1].write("")


# --- Détail d'un chapitre ---
def voir_detail_chapitre(df, budget, section, sens, chapitre, df_grand_livre=None):
    st.markdown(
     """
     <style>
     color:cyan;
     background-color:blue;
     }
     </style>
     """,
     unsafe_allow_html=True
     )

    cols_base = ["Compte", "Total_Prévu", "Réalisé", "Reste_engagé"]
    cols_liquide = [c for c in COLS_LIQUIDE if c in df.columns]
    cols_affichees = cols_base + cols_liquide

    df_detail = df.loc[
        (df["Libellé_budget"] == budget) &
        (df["Section"] == section) &
        (df["Sens"] == sens) &
        (df["Chapitre"] == chapitre),
        cols_affichees
    ].copy()

    # Calcul des totaux AVANT formatage
    df_totaux = df_detail.copy()
    for col in cols_affichees:
        if col != "Compte":
            df_totaux[col] = pd.to_numeric(df_totaux[col], errors="coerce").fillna(0)

    # Conversion + formatage manuel pour affichage
    for col in cols_affichees:
        if col != "Compte":
            df_detail[col] = pd.to_numeric(df_detail[col], errors="coerce").fillna(0).map(
                lambda x: f"{x:,.2f} €".replace(",", " ")
            )

    st.write(f"**Détails du Chapitre {chapitre} ({budget} / {section} / {sens})**")
    st.markdown(
        f"""
        <div class="detail-box">
            <strong>Détails du Chapitre {chapitre}</strong><br>
            <em>{budget} / {section} / {sens}</em>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Gestion des écritures compte par compte ---
    if "comptes_ouverts" not in st.session_state:
        st.session_state.comptes_ouverts = {}

    st.markdown("#### Comptes du chapitre")

    for idx_compte, row_compte in df_detail.iterrows():
        compte = row_compte["Compte"]
        compte_key = f"{chapitre}_{compte}_{idx_compte}"
        nb_cols_data = len(cols_affichees)
        cols_compte = st.columns([2] * nb_cols_data + [1])

        for i, col in enumerate(cols_affichees):
            cols_compte[i].write(row_compte[col])

        # Bouton pour écrire
        if df_grand_livre is not None:
            if cols_compte[-1].button(
                "📝",
                key=f"ecriture_{compte_key}",
                help="Voir les écritures"
            ):
                dialog_ecritures(
                    df_grand_livre,
                    budget,
                    section,
                    sens,
                    compte
                )
        else:
            cols_compte[-1].write("—")

    # ---- RAPPEL ENTÊTE AVANT TOTAL ----
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    header_cols = st.columns([2] + [2] * len(cols_base[1:] + cols_liquide) + [1])
    header_cols[0].markdown("**Compte**")
    for i, col in enumerate(cols_base[1:] + cols_liquide, start=1):
        header_cols[i].markdown(f"**{col.replace('_', ' ')}**")
    header_cols[-1].markdown("**Écritures**")

    # ---- LIGNE TOTAL ----
    total_cols = st.columns([2] + [2] * len(cols_base[1:] + cols_liquide) + [1])
    total_cols[0].markdown(
        '<div style="background-color:#f0f0f0; font-weight:bold; padding:0.3rem;color:black">TOTAL</div>',
        unsafe_allow_html=True
    )
    for i, col in enumerate(cols_base[1:] + cols_liquide, start=1):
        total_val = safe_sum(df_totaux, col)
        total_cols[i].markdown(
            f'<div style="background-color:#f0f0f0; font-weight:bold; text-align:right; padding:0.3rem;color:black;">{total_val:,.2f} €</div>',
            unsafe_allow_html=True
        )
    total_cols[-1].write("")

    # ---- Graphique de détail
    st.markdown("---")
    st.subheader(f"📊 Répartition des comptes du chapitre {chapitre}")
    camembert_detail(df, budget, section, sens, chapitre)

@st.dialog("📝 Détail des écritures")
def dialog_ecritures(df_grand_livre, budget, section, sens, compte):
    
    st.markdown(
     """
     <style>
     div[data-testid="stDialog"] > div {
         width: 140vw !important;
         max-width: 1400px !important;
     }
     </style>
     """,
     unsafe_allow_html=True
     )

    container = st.container()

    with container:
        st.caption(f"{budget} / {section} / {sens}")

        afficher_ecritures_compte(
            df_grand_livre,
            budget,
            section,
            sens,
            compte
        )



# --- Affichage des écritures d'un compte ---
def afficher_ecritures_compte(df_grand_livre, budget, section, sens, compte):
    ecritures = get_ecritures_compte(df_grand_livre, budget, section, sens, compte)

    if ecritures.empty:
        st.info(f"Aucune écriture trouvée pour le compte {compte}")
        return

    st.markdown(
        f"""
        <div class="ecriture-box">
            <strong>📝 Écritures du compte {compte}</strong><br>
            <em>{len(ecritures)} écriture(s)</em>
        </div>
        """,
        unsafe_allow_html=True
    )

    cols_ecritures = [
        "Date", "type", "Objet", "N_Bordereau", "N_Pièce",
        "Tiers", "Montant_HT", "Montant_TTC", "Réalisé"
    ]
    cols_disponibles = [c for c in cols_ecritures if c in ecritures.columns]
    df_ecritures_affichage = ecritures[cols_disponibles].copy()

    for col in ["Montant_HT", "Montant_TTC", "Réalisé"]:
        if col in df_ecritures_affichage.columns:
            df_ecritures_affichage[col] = df_ecritures_affichage[col].apply(
                lambda x: f"{float(x):,.2f} €".replace(",", " ") if pd.notna(x) else "0.00 €"
            )

    st.dataframe(df_ecritures_affichage, use_container_width=True, hide_index=True)

    total_realise = ecritures["Réalisé"].sum()
    st.caption(f"💰 Total réalisé : {total_realise:,.2f} €".replace(",", " "))
