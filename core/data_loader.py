# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 11:58:42 2026

@author: P.PETIT
"""

import pandas as pd


def load_data(uploaded_file):
    """Charge un fichier uploadé Streamlit"""

    if uploaded_file is None:
        return None

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
    else:
        df = pd.read_excel(uploaded_file)

    return df
