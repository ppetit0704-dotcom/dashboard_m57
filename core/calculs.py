def calculer_sommes_par_chapitre(df, annees):
    import pandas as pd
    # Convertir les colonnes numériques en float pour éviter les erreurs de format
    cols_numeriques = ["Total_Prévu", "Réalisé", "Reste_engagé"] + list(annees)
    for col in cols_numeriques:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")  # remplace les valeurs invalides par NaN

    sommes = {}
    report_a_nouveau = 0.0
    report_a_nouveau_invest=0.0

    grp = df.groupby("Chapitre")

    for chapitre, data in grp:
        code = str(chapitre).split("-")[0].strip()

        sommes[code] = {
            "libelle": chapitre,
            "Total_Prévu": data["Total_Prévu"].sum(),
            "Réalisé": data["Réalisé"].sum(),
            "Reste_engagé": data["Reste_engagé"].sum(),
        }

        if code == "002":
            report_a_nouveau = data["Réalisé"].sum()
        
        if code == "001":
            report_a_nouveau_invest = data["Réalisé"].sum()

        for an in annees:
            sommes[code][an] = data[an].sum()

    return sommes, report_a_nouveau,report_a_nouveau_invest



def calcul_autofinancement(df,budget):

    # Ne garder que le budget communal pour le report_n1
    #df_communal = df[df["Libellé_budget"] == "BUDGET COMMUNAL"]  # ou le nom exact dans ton CSV
    df_communal = df[df["Libellé_budget"] == budget]

    # Groupe pour tous les calculs de produits/charges (peut rester sur tout le df)
    grp = df.groupby("Chapitre")
    sommes = {
        str(ch).split("-")[0].strip(): data["Réalisé"].sum()
        for ch, data in grp
    }

    produits = sum(sommes.get(c, 0) for c in ["70","73","731","74","75","013"])
    charges  = sum(sommes.get(c, 0) for c in ["011","012","014","65"])
    marge = produits - charges

    charges_autres = sum(sommes.get(c, 0) for c in ["66","67"])
    produits_autres = sum(sommes.get(c, 0) for c in ["76","77"])
    epargne_brute = marge - charges_autres + produits_autres
    epargne_nette = epargne_brute - sommes.get("16", 0)

    # ✅ Report N1 = réalisé du chapitre 002 **uniquement dans le budget communal**
    report_grp = df_communal.groupby("Chapitre")
    report_sommes = {
        str(ch).split("-")[0].strip(): data["Réalisé"].sum()
        for ch, data in report_grp
    }
    report_n1 = report_sommes.get("002", 0)


    # Retour formaté
    return {
        "Marge brute": f"{marge:,.2f} €",
        "Epargne brute": f"{epargne_brute:,.2f} €",
        "Epargne nette": f"{epargne_nette:,.2f} €",
        "Dont produits exceptionnels": f"{produits_autres:,.2f} €",
        "Report N -1": f"{report_n1:,.2f} €",
        "Disponibilité": f"{(epargne_nette + report_n1):,.2f} €"
    }

