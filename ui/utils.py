# core/utils.py
"""Utilitaires CSS, formatage et constantes partagées."""

import streamlit as st

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

APP_TITLE   = "PPEI — Budget & Finances"
APP_VERSION = "v2.0.0"
APP_ICON    = "💰"

COULEUR_DEP = "#2563a8"   # bleu dépenses
COULEUR_REC = "#16a34a"   # vert recettes
COULEUR_NEG = "#dc2626"   # rouge dépassement

SENS_LABELS  = {"D": "Dépenses", "R": "Recettes"}
SECT_LABELS  = {"F": "Fonctionnement", "I": "Investissement"}

# ---------------------------------------------------------------------------
# CSS global
# ---------------------------------------------------------------------------

CSS = """
<style>
/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3a5c 0%, #2563a8 100%);
}
[data-testid="stSidebar"] * { color: #f0f6ff !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #cbd5e1 !important; }

/* Métriques */
[data-testid="stMetric"] {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] { color: #1a3a5c !important; font-size: 1.4rem !important; font-weight: 700 !important; }

/* En-tête app */
.ppei-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #2563a8 100%);
    border-radius: 10px;
    padding: 18px 24px;
    margin-bottom: 20px;
    color: white;
}
.ppei-header h1 { color: white !important; margin: 0; font-size: 1.6rem; }
.ppei-header p  { color: #cbd5e1 !important; margin: 4px 0 0; font-size: 0.9rem; }

/* Jauges */
.jauge-container { margin: 6px 0; }
.jauge-label { font-size: 0.82rem; color: #374151; margin-bottom: 2px; }
.jauge-bar-bg {
    background: #e2e8f0; border-radius: 20px;
    height: 14px; overflow: hidden; width: 100%;
}
.jauge-bar-fill {
    height: 100%; border-radius: 20px;
    transition: width 0.4s ease;
}
.jauge-pct { font-size: 0.78rem; color: #64748b; margin-top: 2px; text-align: right; }

/* Tabs */
[data-testid="stTabs"] button {
    font-weight: 600;
    font-size: 0.85rem;
    padding: 8px 16px;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #2563a8 !important;
    border-bottom: 3px solid #2563a8;
}

/* Dataframe */
.stDataFrame { border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }

/* Badges budget */
.badge-budget {
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 6px;
}

/* Footer */
.ppei-footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.75rem;
    margin-top: 30px;
    padding-top: 12px;
    border-top: 1px solid #e2e8f0;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Formatage
# ---------------------------------------------------------------------------

def fmt_euros(val, decimales=2) -> str:
    """Formate un float en euros FR."""
    try:
        v = float(val)
        fmt = f"{v:,.{decimales}f} €"
        # séparateur milliers → espace insécable FR
        return fmt.replace(",", "\u202f")
    except Exception:
        return "—"


def fmt_pct(val, decimales=1) -> str:
    try:
        return f"{float(val):.{decimales}f} %"
    except Exception:
        return "—"


def couleur_taux(taux: float) -> str:
    """Retourne une couleur selon le taux de réalisation."""
    if taux >= 90:
        return COULEUR_NEG   # rouge : très élevé
    elif taux >= 60:
        return COULEUR_DEP   # bleu : normal
    else:
        return "#f59e0b"     # orange : faible


def jauge_html(label: str, taux: float, couleur: str = None) -> str:
    """Génère le HTML d'une jauge de progression."""
    t = max(0.0, min(taux, 100.0))
    c = couleur or couleur_taux(t)
    return f"""
    <div class="jauge-container">
        <div class="jauge-label">{label}</div>
        <div class="jauge-bar-bg">
            <div class="jauge-bar-fill" style="width:{t:.1f}%;background:{c};"></div>
        </div>
        <div class="jauge-pct">{t:.1f} %</div>
    </div>
    """


def badge_budget(label: str) -> str:
    return f'<span class="badge-budget">{label}</span>'

# ---------------------------------------------------------------------------
# Thème Plotly — universel clair/sombre
# ---------------------------------------------------------------------------

PLOTLY_FONT_COLOR   = "#e2e8f0"       # texte clair — lisible sur fond sombre
PLOTLY_FONT_TITLE   = "#ffffff"       # titres blancs
PLOTLY_GRID_COLOR   = "#334155"       # grille discrète sur fond sombre
PLOTLY_BG           = "#1e293b"       # fond graphique sombre explicite
PLOTLY_PAPER_BG     = "#1e293b"       # fond contour identique

COULEUR_PREVU       = "#475569"       # gris ardoise — "Prévu" visible sur sombre
COULEUR_DEP_PLOT    = "#3b82f6"       # bleu vif — Dépenses
COULEUR_REC_PLOT    = "#22c55e"       # vert vif — Recettes
COULEUR_ALERTE      = "#ef4444"       # rouge vif — dépassement


def plotly_base_layout(height=320, margin=None, title=None, barmode=None) -> dict:
    """
    Layout Plotly thème sombre explicite.
    Fond #1e293b, textes blancs/clairs forcés — lisible quel que soit le thème Streamlit.
    """
    m = margin or dict(t=30, b=30, l=0, r=10)
    layout = dict(
        height=height,
        margin=m,
        paper_bgcolor=PLOTLY_PAPER_BG,
        plot_bgcolor=PLOTLY_BG,
        font=dict(color=PLOTLY_FONT_COLOR, family="Segoe UI, system-ui, sans-serif", size=11),
        legend=dict(
            orientation="h", y=1.08, x=0,
            font=dict(color=PLOTLY_FONT_COLOR, size=10),
            bgcolor="rgba(30,41,59,0.85)",
            bordercolor=PLOTLY_GRID_COLOR,
            borderwidth=1,
        ),
        xaxis=dict(
            gridcolor=PLOTLY_GRID_COLOR,
            zerolinecolor=PLOTLY_GRID_COLOR,
            tickfont=dict(color=PLOTLY_FONT_COLOR, size=10),
            title=dict(font=dict(color=PLOTLY_FONT_COLOR)),
            linecolor=PLOTLY_GRID_COLOR,
        ),
        yaxis=dict(
            gridcolor=PLOTLY_GRID_COLOR,
            zerolinecolor=PLOTLY_GRID_COLOR,
            tickfont=dict(color=PLOTLY_FONT_COLOR, size=10),
            title=dict(font=dict(color=PLOTLY_FONT_COLOR)),
            linecolor=PLOTLY_GRID_COLOR,
        ),
        hoverlabel=dict(bgcolor="#0f172a", font_color="#e2e8f0", font_size=11),
    )
    if title:
        layout["title"] = dict(text=title, font=dict(color=PLOTLY_FONT_TITLE, size=13), x=0)
    if barmode:
        layout["barmode"] = barmode
    return layout


def plotly_bar_colors(taux_list: list) -> list:
    """Vert vif si taux < 100 %, rouge vif si >= 100 %."""
    return [COULEUR_ALERTE if t >= 100 else COULEUR_REC_PLOT for t in taux_list]


# ---------------------------------------------------------------------------
# Sidebar commune
# ---------------------------------------------------------------------------

def sidebar_filters(df_sit, df_gl):
    """
    Affiche les filtres sidebar et retourne (df_sit_f, df_gl_f, budget_sel).
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏛️ Filtres")

    budgets = sorted(df_sit["Libellé_budget"].dropna().unique().tolist())
    budget_sel = st.sidebar.selectbox("Budget", budgets)

    df_sit_f = df_sit[df_sit["Libellé_budget"] == budget_sel].copy()
    df_gl_f  = df_gl[df_gl["Libellé_budget"] == budget_sel].copy()

    # Filtre section optionnel
    sections = ["Toutes"] + [f"{k} — {v}" for k, v in SECT_LABELS.items()]
    sect_sel = st.sidebar.selectbox("Section", sections)
    if sect_sel != "Toutes":
        code = sect_sel.split(" — ")[0]
        df_sit_f = df_sit_f[df_sit_f["Section"] == code]
        df_gl_f  = df_gl_f[df_gl_f["Section"] == code]

    # Infos
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{len(df_sit_f)}** lignes situation")
    st.sidebar.markdown(f"**{len(df_gl_f)}** lignes grand livre")

    # Liens & infos
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "🐛 [Signaler un bug](mailto:contact@ppei.fr) | "
        "📘 [Documentation](#)"
    )
    st.sidebar.markdown(f"<small>{APP_VERSION}</small>", unsafe_allow_html=True)

    return df_sit_f, df_gl_f, budget_sel


# ---------------------------------------------------------------------------
# Bandeau sélection budget indépendant
# ---------------------------------------------------------------------------

def bandeau_budget_independant(budget_actif: str = "") -> None:
    """
    Affiche un bandeau HTML informatif indiquant que l'onglet
    dispose de son propre filtre budget, indépendant de la sidebar.
    """
    if budget_actif:
        contenu = f"""
        <div style="
            background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%);
            border-radius: 10px;
            padding: 14px 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 14px;
        ">
            <div style="font-size: 1.6rem;">📋</div>
            <div>
                <div style="color:#bfdbfe;font-size:0.72rem;font-weight:700;
                            letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px;">
                    Filtre budget indépendant
                </div>
                <div style="color:#ffffff;font-size:0.95rem;font-weight:600;">
                    Budget actif : <span style="color:#fbbf24;">{budget_actif}</span>
                </div>
                <div style="color:#93c5fd;font-size:0.75rem;margin-top:3px;">
                    ℹ️ Ce filtre est indépendant de la sélection principale de la sidebar.
                </div>
            </div>
        </div>
        """
    else:
        contenu = """
        <div style="
            background: linear-gradient(135deg, #7c2d12 0%, #ea580c 100%);
            border-radius: 10px;
            padding: 14px 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 14px;
        ">
            <div style="font-size: 1.6rem;">⚠️</div>
            <div>
                <div style="color:#fed7aa;font-size:0.72rem;font-weight:700;
                            letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px;">
                    Sélection requise
                </div>
                <div style="color:#ffffff;font-size:0.95rem;font-weight:600;">
                    Veuillez sélectionner votre budget ci-dessous
                </div>
                <div style="color:#fdba74;font-size:0.75rem;margin-top:3px;">
                    ℹ️ Cet onglet dispose de son propre filtre budget,
                    indépendant de la sélection principale.
                </div>
            </div>
        </div>
        """
    import streamlit as st
    st.markdown(contenu, unsafe_allow_html=True)
