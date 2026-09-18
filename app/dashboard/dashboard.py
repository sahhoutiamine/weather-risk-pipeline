import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from app.config.database import engine

st.set_page_config(page_title="Weather Risk Dashboard", layout="wide")


# ==========================================
# Data loading (cached to avoid hitting DB on every interaction)
# ==========================================

@st.cache_data(ttl=300)
def load_data():
    query = """
        SELECT
            c.city_name,
            c.latitude,
            c.longitude,
            f.forecast_date,
            f.temp_max,
            f.temp_min,
            f.precipitation_sum,
            f.precipitation_probability,
            f.wind_speed,
            f.wind_gusts,
            r.risk_score,
            r.risk_level,
            r.risk_reason,
            r.temperature_category,
            r.precipitation_category,
            r.wind_category
        FROM forecast f
        JOIN cities c ON c.city_id = f.city_id
        JOIN risk_score r ON r.forecast_id = f.forecast_id
        ORDER BY f.forecast_date, c.city_name
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    df["forecast_date"] = pd.to_datetime(df["forecast_date"])
    return df


df = load_data()

st.title("🌦️ Weather Risk Dashboard — Morocco Delivery Operations")


# ==========================================
# Sidebar filters
# ==========================================

st.sidebar.header("Filtres")

# Filter: ville
cities = sorted(df["city_name"].unique())
selected_cities = st.sidebar.multiselect("Ville", cities, default=cities)

# Filter: date range
min_date, max_date = df["forecast_date"].min(), df["forecast_date"].max()
date_range = st.sidebar.date_input(
    "Période (plage de dates)",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Filter: période relative
periode = st.sidebar.selectbox(
    "Période relative",
    ["Toutes", "Aujourd'hui + 2 jours", "3-7 jours"]
)

# Filter: niveau de risque
risk_levels = ["Low", "Medium", "High", "Critical"]
selected_levels = st.sidebar.multiselect("Niveau de risque", risk_levels, default=risk_levels)

# --- Apply filters ---
filtered = df[
    df["city_name"].isin(selected_cities) &
    df["risk_level"].isin(selected_levels)
]

if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["forecast_date"] >= start) & (filtered["forecast_date"] <= end)]

if periode == "Aujourd'hui + 2 jours":
    cutoff = min_date + pd.Timedelta(days=2)
    filtered = filtered[filtered["forecast_date"] <= cutoff]
elif periode == "3-7 jours":
    cutoff = min_date + pd.Timedelta(days=2)
    filtered = filtered[filtered["forecast_date"] > cutoff]


# ==========================================
# KPIs
# ==========================================

st.subheader("Indicateurs clés")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Nombre de villes", filtered["city_name"].nunique())
col2.metric(
    "Température max (°C)",
    f"{filtered['temp_max'].max():.1f}" if not filtered.empty else "—"
)
col3.metric(
    "Précipitations max (mm)",
    f"{filtered['precipitation_sum'].max():.1f}" if not filtered.empty else "—"
)

nb_risky_periods = filtered[filtered["risk_level"].isin(["High", "Critical"])].shape[0]
col4.metric("Périodes à risque (High/Critical)", nb_risky_periods)

if not filtered.empty:
    top_risk_row = filtered.loc[filtered["risk_score"].idxmax()]
    top_city_label = f"{top_risk_row['city_name']} ({top_risk_row['forecast_date'].date()})"
else:
    top_city_label = "—"
col5.metric("Ville la plus à risque", top_city_label)


# ==========================================
# Alertes — répond directement à "où et quand être vigilant"
# ==========================================

st.subheader("⚠️ Alertes — où et quand être vigilant")

alerts = filtered[filtered["risk_level"].isin(["High", "Critical"])].sort_values(
    "risk_score", ascending=False
)

if alerts.empty:
    st.success("Aucune période à risque élevé détectée sur la sélection actuelle.")
else:
    st.dataframe(
        alerts[["city_name", "forecast_date", "risk_score", "risk_level", "risk_reason"]]
        .rename(columns={
            "city_name": "Ville",
            "forecast_date": "Date",
            "risk_score": "Score",
            "risk_level": "Niveau",
            "risk_reason": "Raison",
        }),
        use_container_width=True,
        hide_index=True,
    )


# ==========================================
# Carte du Maroc — points colorés selon le risque
# ==========================================

st.subheader("🗺️ Carte du risque par ville")

if filtered.empty:
    st.info("Aucune donnée à afficher sur la carte pour cette sélection.")
else:
    # One point per city = worst (max) risk score in the current filtered selection
    city_summary = (
        filtered.groupby(["city_name", "latitude", "longitude"], as_index=False)
        .agg(max_risk_score=("risk_score", "max"))
    )

    # Recover the risk_level + date corresponding to that max score, for hover info
    worst_row_per_city = filtered.loc[
        filtered.groupby("city_name")["risk_score"].idxmax()
    ][["city_name", "risk_level", "forecast_date"]]

    city_summary = city_summary.merge(worst_row_per_city, on="city_name")

    def risk_color(level):
        if level in ["High", "Critical"]:
            return "red"
        elif level == "Medium":
            return "orange"
        else:
            return "blue"

    city_summary["color"] = city_summary["risk_level"].apply(risk_color)

    fig_map = px.scatter_map(
        city_summary,
        lat="latitude",
        lon="longitude",
        color="color",
        color_discrete_map={"blue": "blue", "orange": "orange", "red": "red"},
        size="max_risk_score",
        size_max=20,
        hover_name="city_name",
        hover_data={
            "max_risk_score": True,
            "risk_level": True,
            "forecast_date": True,
            "latitude": False,
            "longitude": False,
            "color": False,
        },
        zoom=4.8,
        center={"lat": 31.5, "lon": -6.5},
        map_style="open-street-map",
    )
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=500)
    fig_map.update_layout(showlegend=False)

    st.plotly_chart(fig_map, use_container_width=True)

    st.caption("🔵 Low   🟠 Medium   🔴 High / Critical")


# ==========================================
# Évolution du risque par ville (ligne temporelle)
# ==========================================

st.subheader("Évolution du risque par ville")

if filtered.empty:
    st.info("Aucune donnée à afficher pour cette sélection.")
else:
    fig_line = px.line(
        filtered.sort_values("forecast_date"),
        x="forecast_date",
        y="risk_score",
        color="city_name",
        markers=True,
        labels={
            "forecast_date": "Date",
            "risk_score": "Score de risque",
            "city_name": "Ville",
        },
    )
    fig_line.add_hline(
        y=40, line_dash="dash", line_color="orange", annotation_text="Seuil Medium/High"
    )
    st.plotly_chart(fig_line, use_container_width=True)


# ==========================================
# Heatmap : ville x date
# ==========================================

st.subheader("Carte thermique : risque par ville et date")

if filtered.empty:
    st.info("Aucune donnée à afficher pour cette sélection.")
else:
    heatmap_data = filtered.pivot_table(
        index="city_name", columns="forecast_date", values="risk_score", aggfunc="max"
    )
    fig_heatmap = px.imshow(
        heatmap_data,
        color_continuous_scale="YlOrRd",
        aspect="auto",
        labels=dict(color="Score de risque"),
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)


# ==========================================
# Données détaillées (repliable)
# ==========================================

with st.expander("Voir les données détaillées"):
    st.dataframe(filtered, use_container_width=True, hide_index=True)