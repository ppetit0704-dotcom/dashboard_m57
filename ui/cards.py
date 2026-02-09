import streamlit as st

def afficher_indicateurs(total_budget, total_realise, reste_engage, ratio, taux):
    c1, c2, c3, c4 = st.columns(4)

    badges = [
        ("💰 Budget prévu", f"{total_budget:,.2f} €", "blue"),
        ("✅ Réalisé", f"{total_realise:,.2f} € ({taux:.1f} %)", "#045211"),
        ("📊 Reste engagé", f"{reste_engage:,.2f} €", "#4C0452"),
        ("👤 Ratio / hab.", f"{ratio:,.2f} €", "#F54927")
    ]

    for col, (label, value, color) in zip([c1, c2, c3, c4], badges):
        col.markdown(
            f"""
            <div style="background-color:{color};padding:15px;border-radius:10px;text-align:center">
                <h4 style="margin:0">{label}</h4>
                <strong style="font-size:18px">{value}</strong>
            </div>
            """, unsafe_allow_html=True
        )

def badge(label, value, color="#FB9223"):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:12px;
            border-radius:8px;
            text-align:center;
            font-size:16px;
            font-weight:600;">
            <div style="font-size:13px; color:#555;">{label}</div>
            <div>{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
def badgeRed(label, value, color="red"):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:12px;
            border-radius:8px;
            text-align:center;
            font-size:16px;
            font-weight:600;">
            <div style="font-size:13px; color:white;">{label}</div>
            <div>{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
def badgeGreen(label, value, color="darkgreen"):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:12px;
            border-radius:8px;
            text-align:center;
            font-size:16px;
            font-weight:600;">
            <div style="font-size:13px; color:white;">{label}</div>
            <div>{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def badgeBlue(label, value, color="blue"):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:12px;
            border-radius:8px;
            text-align:center;
            font-size:16px;
            font-weight:600;">
            <div style="font-size:13px; color:white;">{label}</div>
            <div>{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
