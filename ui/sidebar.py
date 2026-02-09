import streamlit as st


def filtres(df):
    """
    Affichage des filtres.
    Le container (sidebar, expander, colonne, etc.)
    est défini dans app.py.
    """

    # -------------------------
    # Budget
    # -------------------------
    budgets = sorted(df["Libellé_budget"].dropna().unique())

    if "budget" not in st.session_state:
        st.session_state["budget"] = budgets[0]

    budget = st.selectbox(
        "Budget",
        budgets,
        index=budgets.index(st.session_state["budget"])
    )

    # -------------------------
    # Section
    # -------------------------
    sections = sorted(df["Section"].dropna().unique())

    section = st.selectbox(
        "Section",
        sections
    )

    # -------------------------
    # Sens
    # -------------------------
    sens_list = sorted(df["Sens"].dropna().unique())

    sens = st.selectbox(
        "Sens",
        sens_list
    )

    # -------------------------
    # Population
    # -------------------------
    population = st.number_input(
        "Population",
        min_value=1,
        value=2243,
        step=1
    )

    return budget, section, sens, population
