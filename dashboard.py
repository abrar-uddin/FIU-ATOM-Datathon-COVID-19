import streamlit as st
import pandas as pd
import requests
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

county_picker = st.sidebar.selectbox('Select County',
                                     ("Dade", 'Broward', 'Collier', 'All')
                                     )

st.title('Local COVID-19 Tracker')

url = 'https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/Florida_COVID19_Cases/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'

try:
    status = requests.get(url)
    raw_data = requests.get(url)
except:
    st.write('## **API DOWN!**')

raw_data = raw_data.json()['features']
raw_data = pd.json_normalize(raw_data)
raw_data = raw_data.drop(['attributes.OBJECTID', 'attributes.OBJECTID_12_13', 'attributes.State',
                          'attributes.COUNTYNAME', 'attributes.DEPCODE', 'attributes.COUNTY',
                          'geometry.rings', 'attributes.Shape__Length', 'attributes.Shape__Area'], axis=1)

if county_picker != "All":
    selected_county = raw_data['attributes.County_1'] == county_picker
    local_counties = raw_data[selected_county]
else:
    broward = raw_data['attributes.County_1'] == 'Broward'
    dade = raw_data['attributes.County_1'] == 'Dade'
    collier = raw_data['attributes.County_1'] == 'Collier'
    local_counties = raw_data[broward]
    local_counties = local_counties.append(raw_data[dade])
    local_counties = local_counties.append(raw_data[collier])

st.write(local_counties)

fig = go.Figure()
fig = make_subplots(rows=1, cols=2,
                    specs=[[{'type': 'xy'}, {'type': 'xy'}]])
# Testing Chart
fig.add_trace(go.Bar(x=local_counties['attributes.County_1'], y=local_counties['attributes.TPositive'],
                marker_color='crimson',
                name='Positive'), 1, 1)
fig.add_trace(go.Bar(x=local_counties['attributes.County_1'], y=local_counties['attributes.TNegative'],
                marker_color='green',
                name='Negative'), 1, 1)
fig.add_trace(go.Bar(x=local_counties['attributes.County_1'], y=local_counties['attributes.Deaths'],
                marker_color='grey',
                name='Deaths'), 1, 1)

# Race Chart
fig.add_trace(go.Bar(x=local_counties['attributes.County_1'], y=local_counties['attributes.C_RaceWhite'],
                marker_color='pink',
                name='White'), 1, 2)
fig.add_trace(go.Bar(x=local_counties['attributes.County_1'], y=local_counties['attributes.C_RaceBlack'],
                marker_color='black',
                name='Black'), 1, 2)


fig.update_layout()
st.plotly_chart(fig)
