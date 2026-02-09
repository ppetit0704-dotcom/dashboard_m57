# -*- coding: utf-8 -*-
"""
Module graphs.py
@author: P.PETIT
Gestion des graphiques du dashboard
"""

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd


def camembert(df, top_n=4):
    """
    Affiche un camembert des chapitres avec répartition du réalisé.
    
    Args:
        df: DataFrame filtré
        top_n: Nombre de chapitres à afficher individuellement (les autres en "Autres")
    """
    grp = df.groupby("Chapitre")["Réalisé"].sum()
    grp = grp[grp > 0].sort_values(ascending=False)

    if len(grp) > top_n:
        top = grp.head(top_n)
        autres = grp.iloc[top_n:].sum()
        labels = list(top.index) + ["Autres"]
        values = list(top.values) + [autres]
    else:
        labels = grp.index
        values = grp.values

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    ax.set_title("Répartition par chapitres", loc="left")

    st.pyplot(fig)


def camembert_detail(df, budget, section, sens, chapitre, top_n=5):
    """
    Affiche un camembert des comptes d'un chapitre spécifique.
    
    Args:
        df: DataFrame complet
        budget: Filtre budget
        section: Filtre section
        sens: Filtre sens
        chapitre: Chapitre à détailler
        top_n: Nombre de comptes à afficher individuellement
    """
    # Filtrer les données pour le chapitre spécifique
    df_chapitre = df[
        (df["Libellé_budget"] == budget) &
        (df["Section"] == section) &
        (df["Sens"] == sens) &
        (df["Chapitre"] == chapitre)
    ].copy()
    
    # S'assurer que la colonne Réalisé est numérique
    df_chapitre["Réalisé"] = pd.to_numeric(df_chapitre["Réalisé"], errors="coerce").fillna(0)
    
    # Grouper par compte
    grp = df_chapitre.groupby("Compte")["Réalisé"].sum()
    grp = grp[grp > 0].sort_values(ascending=False)
    
    # Si aucune donnée
    if len(grp) == 0:
        st.info(f"Aucune donnée réalisée pour le chapitre {chapitre}")
        return
    
    # Gérer le top N
    if len(grp) > top_n:
        top = grp.head(top_n)
        autres = grp.iloc[top_n:].sum()
        labels = list(top.index) + ["Autres"]
        values = list(top.values) + [autres]
    else:
        labels = grp.index
        values = grp.values
    
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    ax.set_title(f"Répartition des comptes - Chapitre {chapitre}", loc="left")
    
    st.pyplot(fig)
