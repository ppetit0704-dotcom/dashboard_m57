# -*- coding: utf-8 -*-
"""
Module loader_grand_livre.py
@author: P.PETIT
Gestion du chargement du fichier Edition du grand livre
"""

import pandas as pd
import streamlit as st


def load_grand_livre(file):
    """
    Charge le fichier CSV Edition du grand livre.
    
    Args:
        file: Fichier uploadé via st.file_uploader
        
    Returns:
        DataFrame avec les écritures comptables
    """
    try:
        # Chargement avec encodage latin-1 et séparateur point-virgule
        df = pd.read_csv(
            file, 
            sep=";", 
            encoding="latin-1",
            dtype=str  # Garder tout en string au départ
        )
        
        # Nettoyer les noms de colonnes (enlever les espaces)
        df.columns = df.columns.str.strip()
        
        # Colonnes numériques à convertir
        cols_numeriques = [
            "Total__R_V_", "Engagé", "Dégagé", "Liquidé", 
            "Montant_HT", "Montant_TVA_récupérable", "Montant_TTC", 
            "Réalisé", "Reste_engagé"
        ]
        
        # Conversion numérique avec gestion des erreurs
        for col in cols_numeriques:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        
        # Filtrer les lignes vides (totaux/sous-totaux)
        df = df[
            df["Compte"].notna() & 
            (df["Compte"] != "") & 
            df["Date"].notna() &
            (df["Date"] != "")
        ].copy()
        
        return df
        
    except Exception as e:
        st.error(f"Erreur lors du chargement du grand livre : {str(e)}")
        return None


def get_ecritures_compte(df_grand_livre, budget, section, sens, compte):
    """
    Récupère les écritures d'un compte spécifique.
    
    Args:
        df_grand_livre: DataFrame du grand livre
        budget: Filtre budget
        section: Filtre section  
        sens: Filtre sens
        compte: Numéro de compte avec libellé (ex: "001 - Solde d'exécution...")
        
    Returns:
        DataFrame filtré avec les écritures du compte
    """
    if df_grand_livre is None or df_grand_livre.empty:
        return pd.DataFrame()
    
    # Extraire juste le numéro de compte (avant le tiret et le libellé)
    # Ex: "001 - Solde d'exécution..." → "001"
    compte_num = compte.split(" - ")[0].strip() if " - " in compte else compte.strip()
    
    # DEBUG : afficher ce qu'on cherche
    # st.write(f"DEBUG: Recherche compte_num = '{compte_num}', budget = '{budget}', section = '{section}', sens = '{sens}'")
    
    # Filtrer les écritures
    # On filtre d'abord sur budget, section, sens
    df_filtre = df_grand_livre[
        (df_grand_livre["Libellé_budget"] == budget) &
        (df_grand_livre["Section"] == section) &
        (df_grand_livre["Sens"] == sens)
    ].copy()
    
    # DEBUG: voir combien on a après premier filtre
    # st.write(f"DEBUG: Après filtre budget/section/sens : {len(df_filtre)} lignes")
    
    # Ensuite on filtre sur le compte
    # La colonne "Compte" dans le grand livre contient le format complet "XXX - Libellé"
    # On vérifie si le numéro de compte correspond
    df_ecritures = df_filtre[
        df_filtre["Compte"].str.startswith(compte_num + " -", na=False) |
        (df_filtre["Compte"] == compte_num)
    ].copy()
    
    # DEBUG: voir le résultat final
    # st.write(f"DEBUG: Écritures trouvées : {len(df_ecritures)}")
    # if len(df_ecritures) > 0:
    #     st.write("DEBUG: Premiers comptes trouvés:", df_ecritures["Compte"].unique()[:5])
    
    return df_ecritures
