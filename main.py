import streamlit as st
import pandas as pd
import altair as alt
from streamlit_echarts import st_echarts
from connection import connection2
from sql_query_multiple import genre_query_all
from sql_querys import get_population_query, genre_query, voyage_query, job_query, get_migration_moyen_query
from sklearn.linear_model import LinearRegression
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Multi-Country Migration Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sélection des paramètres de l'année et du mois pour les données de population et de genre
st.title("Multi-Country Migration Dashboard")

# Sélection de pays pour les deux parties
countries = ["Tunisia", "Morocco", "France", "Spain", "Italy"]
selected_countries = st.multiselect("Select Countries", countries, default=countries[:2])

# Sélection de l'année pour les deux parties
year = st.slider("Select Year", 2010, 2023, 2023)

# Sélection du mois pour la partie genre
#month = st.selectbox("Select Month", range(1, 13), format_func=lambda x: f"{x:02}")


# Fonction pour charger les données de population
@st.cache_data
def load_population_data(country_code):
    conn = connection2()
    population_query = get_population_query(
        ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022',
         '2023'])
    df = conn.query(population_query, ttl="10m", params={"country": country_code})
    df.columns = ['Region', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020',
                  '2021', '2022', '2023']
    return df


# Chargement des données de population pour les pays sélectionnés
country_codes = {'Tunisia': 'tn', 'Morocco': 'mc', 'France': 'fr', 'Spain': 'sp', 'Italy': 'it'}
population_data = {country: load_population_data(country_codes[country]) for country in selected_countries}


# Afficher les données de population pour chaque pays sélectionné
def display_population_data(df, year, country):
    st.subheader(f"{country} Population Data for {year}")
    if str(year) in df.columns:
        chart_data = df[['Region', str(year)]].rename(columns={str(year): 'Population'})
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Region:N', title='Region'),
            y=alt.Y('Population:Q', title='Population'),
            tooltip=['Region:N', 'Population:Q']
        ).properties(width=600, height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error(f"Data for the year {year} is not available.")


st.header("Population by Region")
for country in selected_countries:
    display_population_data(population_data[country], year, country)


# Fonction pour charger les données de genre
@st.cache_data
def load_gender_data():
    conn = connection2()
    df = conn.query(genre_query_all, ttl="10m")
    df.columns = ['name', 'Année', 'Mois', 'Total', 'Enfants', 'Femmes', 'Hommes']
    return df


# Chargement des données de genre
gender_data = load_gender_data()

# Sélection des paramètres de l'année et du mois pour les données de genre
selected_year_gender = st.selectbox("Choose a year", options=gender_data["Année"].unique(), key='year_gender')
selected_month_gender = st.selectbox("Choose a month", options=gender_data["Mois"].unique(), key='month_gender')
selected_countries_gender = st.multiselect("Choose Countries", options=gender_data["name"].unique(),
                                           key='countries_gender')

# Afficher les graphiques de genre pour chaque pays sélectionné
if selected_countries_gender:
    cols = st.columns(len(selected_countries_gender))
    for col, country in zip(cols, selected_countries_gender):
        with col:
            st.subheader(f"Gender Distribution in {country}")
            filtered_data = gender_data[
                (gender_data["name"] == country) & (gender_data["Année"] == selected_year_gender) & (
                        gender_data["Mois"] == selected_month_gender)]

            if filtered_data.empty:
                st.error(f"No data found for {country} in the selected year and month.")
            else:
                pie_values = filtered_data[['Enfants', 'Femmes', 'Hommes']].sum()
                pie_data = [
                    {"value": int(pie_values['Enfants']), "name": "Enfants", "itemStyle": {"color": "yellow"}},
                    {"value": int(pie_values['Femmes']), "name": "Femmes", "itemStyle": {"color": "pink"}},
                    {"value": int(pie_values['Hommes']), "name": "Hommes", "itemStyle": {"color": "blue"}}
                ]

                options = {
                    "title": {
                        "text": f"Distribution by Gender in {country}",
                        "left": "center"
                    },
                    "tooltip": {
                        "trigger": "item",
                        "formatter": "{a} <br/>{b} : {c} ({d}%)"
                    },
                    "legend": {
                        "orient": "vertical",
                        "left": "left"
                    },
                    "series": [
                        {
                            "name": "Gender Distribution",
                            "type": "pie",
                            "radius": "50%",
                            "data": pie_data,
                            "emphasis": {
                                "itemStyle": {
                                    "shadowBlur": 10,
                                    "shadowOffsetX": 0,
                                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                                }
                            },
                            "animationDuration": 1000,
                            "animationEasing": "elasticOut"
                        }
                    ]
                }

                st_echarts(options=options, height="400px",
                           key=f"{selected_year_gender}-{selected_month_gender}-{country}")

# Section indépendante pour les prédictions de population
st.header("Population Predictions")

# Sélection de pays pour les prédictions
selected_countries_pred = st.multiselect("Select Countries for Prediction", countries, default=countries[:2])

# Sélection de la plage d'années pour les prédictions
start_year_pred = st.slider("Start Year for Prediction", 2024, 2025, 2025)
end_year_pred = st.slider("End Year for Prediction", 2026, 2030, 2030)


# Fonction pour faire des prédictions linéaires de la population
def predict_population(df, start_year, end_year):
    predictions = {}

    years = np.array([int(col) for col in df.columns[1:]]).reshape(-1, 1)
    future_years = np.array(range(start_year, end_year + 1)).reshape(-1, 1)

    for region in df['Region']:
        population = df[df['Region'] == region].values[0][1:]
        model = LinearRegression()
        model.fit(years, population)
        pred = model.predict(future_years)
        predictions[region] = pred

    # Préparer les données pour affichage
    pred_df = pd.DataFrame(predictions, index=range(start_year, end_year + 1)).reset_index().rename(
        columns={'index': 'Year'})
    pred_df = pred_df.melt(id_vars=['Year'], var_name='Region', value_name='Predicted Population')

    return pred_df


# Afficher les prédictions de population pour chaque pays sélectionné
if selected_countries_pred:
    st.subheader(f"Population Predictions for {start_year_pred}-{end_year_pred}")
    for country in selected_countries_pred:
        st.subheader(f"Predicted Population for {country}")
        pred_df = predict_population(population_data[country], start_year_pred, end_year_pred)

        chart = alt.Chart(pred_df).mark_line().encode(
            x='Year:O',
            y='Predicted Population:Q',
            color='Region:N',
            tooltip=['Year:O', 'Region:N', 'Predicted Population:Q']
        ).properties(width=800, height=400)

        st.altair_chart(chart, use_container_width=True)


# Fonction pour charger les données de voyages
@st.cache_data
def load_voyage_data(country_code):
    conn = connection2()
    df = conn.query(voyage_query, ttl="10m", params={"country": country_code})
    df.columns = ['Année', 'Mois', 'Total', 'Voyages']
    return df

st.header("Number of Voyages")
# Chargement des données de voyages pour les pays sélectionnés
voyage_data = {country: load_voyage_data(country_codes[country]) for country in countries}

LIST_MONTH = ['Septembre', 'Août', 'Avril', 'Décembre', 'Février', 'Janvier', 'Juillet', 'Juin', 'Mai', 'Mars',
              'Novembre', 'Octobre']

# Sélection des paramètres de l'année et du mois pour les données de voyages
selected_year_voyage = st.selectbox("Choose a year for Voyage Data", options=list(range(2010, 2024)), key='year_voyage')
selected_month_voyage = st.selectbox("Choose a month for Voyage Data", options=LIST_MONTH, key='month_voyage')
selected_countries_voyage = st.multiselect("Choose Countries for Voyage Data", options=countries,
                                           key='countries_voyage')


# Fonction pour créer les données de la jauge
def create_gauge_data(number_of_journeys):
    return [{"value": int(number_of_journeys), "name": "Nombre de voyage"}]


# Options de la jauge
def gauge_options(gauge_data):
    return {
        "series": [
            {
                "type": 'gauge',
                "startAngle": 90,
                "endAngle": -270,
                "pointer": {
                    "show": True,
                    "length": '80%',
                    "width": 8,
                    "itemStyle": {
                        "color": "red"
                    }
                },
                "progress": {
                    "show": True,
                    "overlap": False,
                    "roundCap": True,
                    "color": "red"
                },
                "axisLine": {
                    "lineStyle": {
                        "width": 30,
                        "color": [[1, 'red']]
                    }
                },
                "axisTick": {
                    "show": False
                },
                "splitLine": {
                    "show": False,
                    "length": 30,
                },
                "axisLabel": {
                    "distance": 15,
                    "color": "#999",
                    "fontSize": 15
                },
                "anchor": {
                    "show": True,
                    "showAbove": True,
                    "size": 25,
                    "itemStyle": {
                        "borderWidth": 10
                    }
                },
                "title": {
                    "show": False
                },
                "detail": {
                    "valueAnimation": True,
                    "formatter": '{value}',
                    "color": 'auto',
                    "fontSize": 40,
                    "offsetCenter": [0, '70%']
                },
                "data": gauge_data,
                "max": 1000
            }
        ]
    }


# Afficher les jauges pour chaque pays sélectionné

if selected_countries_voyage:
    cols = st.columns(len(selected_countries_voyage))
    for col, country in zip(cols, selected_countries_voyage):
        with col:
            st.subheader(f"Number of Voyages in {country}")
            filtered_data = voyage_data[country][(voyage_data[country]["Année"] == selected_year_voyage) & (
                    voyage_data[country]["Mois"] == selected_month_voyage)]

            if filtered_data.empty:
                st.error(f"No data found for {country} in the selected year and month.")
            else:
                journeys_made = filtered_data['Voyages'].iloc[0]
                gauge_data = create_gauge_data(journeys_made)
                options = gauge_options(gauge_data)
                st_echarts(options=options, height="400px", key=f"gauge_chart_{country}")


# Job data section
st.header("Niveaux acdemiques")
@st.cache_data
def load_data_job(country_id):
    conn = connection2()
    df = conn.query(job_query, ttl="10m", params={"country": country_id})
    df.columns = ['Année', 'Mois', 'Total', 'Élèves', 'Étudiants', 'Chômeurs', 'Travailleurs']
    return df


def display_job_data(df, selected_years, selected_months):
    filtered_data = df[df['Année'].isin(selected_years) & df['Mois'].isin(selected_months)]
    filtered_data = filtered_data.sort_values(by=['Année', 'Mois'])

    if not filtered_data.empty:
        line_data = []
        category_colors = ["#c23531", "#2f4554", "#61a0a8", "#d48265"]
        for idx, category in enumerate(["Élèves", "Étudiants", "Chômeurs", "Travailleurs"]):
            line_series = {
                "name": category,
                "type": "line",
                "data": filtered_data[category].tolist(),
                "smooth": True,
                "symbol": "none",
                "sampling": "average",
                "itemStyle": {
                    "color": category_colors[idx]
                }
            }
            line_data.append(line_series)

        axis_data = filtered_data.apply(lambda row: f"{row['Mois']} {row['Année']}", axis=1).tolist()

        options = {
            "title": {
                "text": ''
            },
            "tooltip": {
                "trigger": 'axis'
            },
            "legend": {
                "data": ["Élèves", "Étudiants", "Chômeurs", "Travailleurs"]
            },
            "grid": {
                "left": '3%',
                "right": '4%',
                "bottom": '3%',
                "containLabel": True
            },
            "toolbox": {
                "feature": {
                    "dataZoom": {
                        "yAxisIndex": 'none'
                    },
                    "saveAsImage": {}
                }
            },
            "xAxis": {
                "type": 'category',
                "boundaryGap": False,
                "data": axis_data
            },
            "yAxis": {
                "type": 'value'
            },
            "dataZoom": [
                {
                    "type": 'slider',
                    "start": 0,
                    "end": 100
                },
                {
                    "type": 'inside',
                    "start": 0,
                    "end": 10
                }
            ],
            "series": line_data
        }

        st_echarts(options=options, height="400px")
    else:
        st.error("No data available for the selected time period.")


LIST_ANNEE = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
selected_years = st.multiselect("Select Years", options=sorted(LIST_ANNEE), default=sorted(LIST_ANNEE)[-1])
selected_months = st.multiselect("Select Months", options=sorted(LIST_MONTH), default=sorted(LIST_MONTH)[-1])
selected_countries_job = st.multiselect("Choose Countries for Job Data", options=countries, key='countries_job')

country_codes_id = {'Tunisia': 1, 'Morocco': 5, 'France': 2, 'Spain': 3, 'Italy': 4}
job_data = {country: load_data_job(country_codes_id[country]) for country in country_codes_id}

for country in selected_countries_job:
    display_job_data(job_data[country], selected_years, selected_months)

# Bateau data section
import pandas as pd
import altair as alt


@st.cache_data
def load_data_moyen(country_code):
    conn = connection2()
    migration_moyens = ['maritime', 'bateauxpeche', 'bateauxpneumatique', 'bateauxplaisance', 'navirestransport',
                        'terrestre', 'cachettesdesvehicules', 'apied', 'velos', 'aerienne', 'fauxdocuments', 'vols',
                        'train', 'bus', 'voiture', 'camions']
    migration_moyen_query = get_migration_moyen_query(migration_moyens)
    df = conn.query(migration_moyen_query, ttl="10m", params={"country": country_code})
    df.columns = ['Année', 'Mois', 'Total', 'Nombre de Voyages', 'Voie Maritime', 'Bateaux de Pêche',
                  'Bateaux Pneumatiques', 'Bateaux de Plaisance', 'Navires de Transport de Passagers', 'Voie Terrestre',
                  'Cachettes dans des Véhicules', 'À Pied à Travers des Zones Montagneuses', 'Vélos ou Motocycles',
                  'Voie Aérienne', 'Utilisation des Faux Documents', 'Vols en Connexion avec Plusieurs Escales',
                  'Train', 'Bus', 'Voitures', 'Camions']
    return df

st.header("Moyen de transport ")
def display_moyen_data(df, year, country):
    st.subheader(f"{country} Transport Data for {year}")
    df_year = df[df["Année"] == year]
    if not df_year.empty:
        data = df_year.melt(id_vars=["Mois"], value_vars=['Voie Maritime', 'Bateaux de Pêche', 'Bateaux Pneumatiques',
                                                          'Bateaux de Plaisance', 'Navires de Transport de Passagers',
                                                          'Voie Terrestre', 'Cachettes dans des Véhicules',
                                                          'À Pied à Travers des Zones Montagneuses',
                                                          'Vélos ou Motocycles', 'Voie Aérienne',
                                                          'Utilisation des Faux Documents',
                                                          'Vols en Connexion avec Plusieurs Escales', 'Train', 'Bus',
                                                          'Voitures', 'Camions'],
                            var_name='Transport Type', value_name='Value')

        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X('Mois:N', title='Month'),
            y=alt.Y('Value:Q', title='Value'),
            color='Transport Type:N',
            tooltip=['Mois:N', 'Transport Type:N', 'Value:Q']
        ).properties(width=800, height=400)

        st.altair_chart(chart, use_container_width=True)
    else:
        st.error(f"No data available for {country} in {year}.")


# Sélection de l'année pour les données de moyens de transport
year_to_show_moyen = st.selectbox('Select a year', LIST_ANNEE, key="year_to_show_moyen")
selected_countries_moyen = st.multiselect("Choose Countries for Transport Data", options=countries,
                                          key='countries_moyen')
moyen_data = {country: load_data_moyen(country_codes[country]) for country in country_codes}

# Affichage des données pour chaque pays sélectionné
for country in selected_countries_moyen:
    display_moyen_data(moyen_data[country], year_to_show_moyen, country)

