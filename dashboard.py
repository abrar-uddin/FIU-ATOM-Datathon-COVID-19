import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

county_picker = st.sidebar.selectbox('Select County',
                                     ("Dade", 'Broward', 'Collier', 'All')
                                     )

st.title('Local COVID-19 Tracker')

state_data_url = "https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/Florida_COVID19_Case_Line_Data_NEW/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
county_data_url = 'https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/Florida_COVID19_Cases/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'


@st.cache
def getData(api):
    try:
        data = requests.get(api)
        return data
    except:
        st.write('## **API DOWN!**')

# TODO: Remove state data if not used
# Getting the data
state_data = getData(state_data_url)
county_data = getData(county_data_url)

# State Data Preprocessing
state_data = state_data.json()['features']
state_data = pd.json_normalize(state_data)
state_data = state_data.drop(['attributes.Case1', 'attributes.EventDate', 'attributes.ChartDate',
                                'attributes.ObjectId'], axis=1)

# County Data Preprocessing
county_data = county_data.json()['features']
county_data = pd.json_normalize(county_data)
county_data = county_data.drop(['attributes.OBJECTID', 'attributes.OBJECTID_12_13', 'attributes.State',
                                'attributes.COUNTYNAME', 'attributes.DEPCODE', 'attributes.COUNTY',
                                'geometry.rings', 'attributes.Shape__Length', 'attributes.Shape__Area'], axis=1)

if county_picker != "All":
    # State Data
    selected_county = state_data['attributes.County'] == county_picker
    local_counties_state = state_data[selected_county]

    # County Data
    selected_county = county_data['attributes.County_1'] == county_picker
    local_counties_county = county_data[selected_county]
else:
    # State Data
    broward = state_data['attributes.County'] == 'Broward'
    dade = state_data['attributes.County'] == 'Dade'
    collier = state_data['attributes.County'] == 'Collier'
    local_counties_state = state_data[broward]
    local_counties_state = local_counties_state.append(state_data[dade])
    local_counties_state = local_counties_state.append(state_data[collier])

    # County Data
    broward = county_data['attributes.County_1'] == 'Broward'
    dade = county_data['attributes.County_1'] == 'Dade'
    collier = county_data['attributes.County_1'] == 'Collier'
    local_counties_county = county_data[broward]
    local_counties_county = local_counties_county.append(county_data[dade])
    local_counties_county = local_counties_county.append(county_data[collier])

# st.write(local_counties_county)

fig = go.Figure()
fig = make_subplots(rows=2, cols=2,
                    specs=[[{'type': 'domain'}, {'type': 'domain'}], [{'type': 'xy'}, {'type': 'xy'}]])

fig.add_trace(go.Indicator(
    value = local_counties_county['attributes.Deaths'].values.sum(),
    title = {"text": "Deaths"},
    domain = {'x': [0, 0.5], 'y': [0.6, 0.5]}), 1, 1)

fig.add_trace(go.Indicator(
    value = local_counties_county['attributes.TPositive'].values.sum(),
    title = {"text": "Total Positive Cases"},
    domain = {'x': [0.6, 1], 'y': [0, 1]}), 1, 2)

# Testing Chart
fig.add_trace(go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.TPositive'],
                     marker_color='crimson',
                     name='Positive'), 2, 1)
fig.add_trace(go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.TNegative'],
                     marker_color='green',
                     name='Negative'), 2, 1)
fig.add_trace(go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.Deaths'],
                     marker_color='grey',
                     name='Deaths'), 2, 1)

# Race Chart
fig.add_trace(go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.C_RaceWhite'],
                     marker_color='pink',
                     name='White'), 2, 2)
fig.add_trace(go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.C_RaceBlack'],
                     marker_color='black',
                     name='Black'), 2, 2)
fig.add_trace(go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.C_RaceOther'],
                     marker_color='orchid',
                     name='Other'), 2, 2)
fig.update_layout(height=800, width=800,
                  legend=dict(
                      yanchor="top",
                      y=.43,
                      xanchor="left",
                      x=1
                  )
                  )
st.plotly_chart(fig)
