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
from ui.cards import badge,badgeGreen,badgeRed, badgeBlue

#Affichage entete
def affiche_entete_chapitres(cols_base):
    """
    Affiche l'entête des colonnes pour le tableau des chapitres.
    """
    cols = st.columns([2] + [2]*len(cols_base) + [1])

    cols[0].markdown(
        "<span style='color:#00BCD4; font-weight:700'>Chapitre</span>",
        unsafe_allow_html=True
    )

    for i, col in enumerate(cols_base, start=1):
        cols[i].markdown(
            f"<span style='color:#00BCD4; font-weight:700'>{col}</span>",
            unsafe_allow_html=True
        )



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


def tableau_chapitres(df, budget, section=None, sens=None):
    """
    Crée un tableau des chapitres avec totaux et icône pour déplier le détail.
    """

    # --- 1. Filtre ---
    df_filtre = df[df["Libellé_budget"] == budget].copy()
    if section is not None:
        df_filtre = df_filtre[df_filtre["Section"] == section]
    if sens is not None:
        df_filtre = df_filtre[df_filtre["Sens"] == sens]

    # --- 2. Colonnes à agréger ---
    cols_base = [
        "Total_Prévu",
        "Réalisé",
        "Reste_engagé",
        "Liquidé_N_1",
        "Liquidé_N_2",
        "Liquidé_N_3",
        "Liquidé_N_4",
        "Liquidé_N_5"
    ]

    # --- 3. Group by Chapitre ---
    tableau = df_filtre.groupby("Chapitre", as_index=False)[cols_base].sum()
    tableau["Voir_détail"] = "👁️"

    # --- 4. Ligne total ---
    total = tableau[cols_base].sum()
    total["Chapitre"] = "TOTAL"
    total["Voir_détail"] = ""
    tableau = pd.concat([tableau, pd.DataFrame([total])], ignore_index=True)

    # --- 5. Formatage monétaire ---
    format_monnaie = "{:,.2f} €".format
    tableau_style = tableau.copy()
    for col in cols_base:
        tableau_style[col] = tableau[col].apply(lambda x: format_monnaie(x))

    # --- 6. Affichage Streamlit ---
    st.subheader(f"📋 Tableau des Chapitres ({budget})")

    for idx, row in tableau_style.iterrows():
        
        # Affichage de l'entête
        affiche_entete_chapitres(cols_base)
        if row["Chapitre"] != "TOTAL":
            cols_display = st.columns([2] + [2]*len(cols_base) + [1])
            cols_display[0].write(row["Chapitre"])
            for i, col in enumerate(cols_base, start=1):
                cols_display[i].write(row[col])
            
            # Afficher directement l'expander sans bouton
            with st.expander(f"Détail du Chapitre {row['Chapitre']}", expanded=False):
                voir_detail_chapitre(df, budget, section, sens, row["Chapitre"])
        else:
            # Ligne TOTAL
            st.markdown("### TOTAL")

            cols = st.columns(len(cols_base))
            
            for i, col in enumerate(cols_base):
                with cols[i]:
                    badge(col, row[col])

    return tableau_style




# --- Détail d'un chapitre ---
def voir_detail_chapitre(df, budget, section, sens, chapitre):
    """
    Affiche les détails d'un chapitre à partir du DataFrame principal.
    """

    # Colonnes de base
    cols_base = [
        "Compte",
        "Total_Prévu",
        "Réalisé",
        "Reste_engagé",
        "Liquidé_N_1",
        "Liquidé_N_2",
        "Liquidé_N_3",
        "Liquidé_N_4",
        "Liquidé_N_5"
    ]

    # Filtrer le chapitre
    df_detail = df[
        (df["Libellé_budget"] == budget) &
        (df["Section"] == section) &
        (df["Sens"] == sens) &
        (df["Chapitre"] == chapitre)
    ][cols_base].copy()

    if df_detail.empty:
        st.warning(f"Aucun détail trouvé pour le chapitre {chapitre}.")
        return

    # Conversion en numérique pour les calculs
    for col in cols_base[1:]:
        df_detail[col] = pd.to_numeric(
            df_detail[col], errors="coerce"
        ).fillna(0)

    # Affichage titre
    st.subheader(
        f"Détails du Chapitre {chapitre} ({budget} / {section} / {sens})"
    )

    # Affichage tableau avec formatage
    df_affiche = df_detail.copy()
    for col in cols_base[1:]:
        df_affiche[col] = df_affiche[col].map(
            lambda x: f"{x:,.2f} €".replace(",", " ")
        )

    st.dataframe(df_affiche, use_container_width=True, hide_index=True)

    # Totaux
    total_vals = df_detail[cols_base[1:]].sum()

    
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns(10)
    
    with c1:
            badgeGreen("",f"Total Prévu {total_vals['Total_Prévu']:,.2f} €")
    with c2:
            badge("",f"Réalisé {total_vals['Réalisé']:,.2f} €", "#045211")
    with c3:
            badgeRed("", f"Reste Engagé {total_vals['Reste_engagé']:,.2f} €")
    with c4:
            badgeBlue("",f"Liquidé N-1 {total_vals['Liquidé_N_1']:,.2f} €")
    with c5:
            badgeBlue("",f"Liquidé N-2 {total_vals['Liquidé_N_2']:,.2f} €")
    with c6:
            badgeBlue("",f"Liquidé N-3 {total_vals['Liquidé_N_3']:,.2f} €")
    with c7:
            badgeBlue("",f"Liquidé N-4 {total_vals['Liquidé_N_4']:,.2f} €")
    with c8:
            badgeBlue("",f"Liquidé N-5 {total_vals['Liquidé_N_5']:,.2f} €")   

    st.markdown("### 📈 Évolution des réalisations")

    # Création des données
    data_evolution = pd.DataFrame({
        "Année": ["N","N-1", "N-2", "N-3", "N-4", "N-5"],
        "Montant": [
            total_vals.get("Réalisé", 0),
            total_vals.get("Liquidé_N_1", 0),
            total_vals.get("Liquidé_N_2", 0),
            total_vals.get("Liquidé_N_3", 0),
            total_vals.get("Liquidé_N_4", 0),
            total_vals.get("Liquidé_N_5", 0),
        ]
    }) 
        
    import altair as alt

    chart = alt.Chart(data_evolution).mark_line(point=True).encode(
        x="Année",
        y=alt.Y("Montant", title="Montant (€)"),
        tooltip=["Année", "Montant"]
    ).properties(
        height=350
    )
    delta = total_vals["Réalisé"] - total_vals["Liquidé_N_1"]

    st.metric(
        label="Évolution N vs N-1",
        value=f"{total_vals['Réalisé']:,.2f} €",
        delta=f"{delta:,.2f} €"
)
    
    st.altair_chart(chart, use_container_width=True)
    
    # Graphique répartition
    st.markdown("---")
    st.subheader(f"📊 Répartition des comptes du chapitre {chapitre}")
    camembert_detail(df, budget, section, sens, chapitre)
