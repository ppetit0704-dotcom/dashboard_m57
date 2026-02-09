# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 11:55:50 2026

@author: P.PETIT
"""

import streamlit as st


def sidebar_upload():
    """Gestion du chargement des fichiers dans la sidebar"""

    with st.sidebar:

        st.header("📂 Chargement des données")

        file_budget = st.file_uploader(
            "Fichier budget",
            type=["csv", "xlsx"],
            key="budget_file"
        )

        file_realise = st.file_uploader(
            "Fichier réalisé",
            type=["csv", "xlsx"],
            key="realise_file"
        )

        st.divider()

    return file_budget, file_realise
