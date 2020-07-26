import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import geopandas as gpd

view_picker = st.sidebar.selectbox('Change View', ("Risk Profile", 'Local Covid Tracker'))

if view_picker == 'Risk Profile':
    st.title('Risk Profile')
    # TODO: put the risk profile code here
    # TODO: need a way to view individual data, dont bother to make it secure; simple pid lookup should be fine
    # TODO: compare risk profiles by college, county, etc
    # TODO: WE GOT THIS!
    pass
else:
    st.title('Local COVID-19 Tracker')
    county_picker = st.sidebar.selectbox('Select County',
                                         ("Dade", 'Broward', 'Collier', 'Monroe', 'All')
                                         )

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
                                    'attributes.Shape__Length', 'attributes.Shape__Area'], axis=1)

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
        monroe = county_data['attributes.County_1'] == 'Monroe'
        local_counties_county = pd.DataFrame()
        local_counties_county = local_counties_county.append(county_data[broward], ignore_index=True)
        local_counties_county = local_counties_county.append(county_data[dade], ignore_index=True)
        local_counties_county = local_counties_county.append(county_data[collier], ignore_index=True)
        local_counties_county = local_counties_county.append(county_data[monroe], ignore_index=True)

    # st.write(local_counties_county) # TODO: Only for debugging; remove

    fig = go.Figure()
    fig = make_subplots(rows=2, cols=2,
                        specs=[[{'type': 'domain'}, {'type': 'domain'}], [{'type': 'xy'}, {'type': 'xy'}]])

    fig.add_trace(go.Indicator(
        value=local_counties_county['attributes.Deaths'].values.sum(),
        title={"text": "Deaths"},
        domain={'x': [0, 0.5], 'y': [0.6, 0.5]}), 1, 1)

    fig.add_trace(go.Indicator(
        value=local_counties_county['attributes.TPositive'].values.sum(),
        title={"text": "Total Positive Cases"},
        domain={'x': [0.6, 1], 'y': [0, 1]}), 1, 2)

    # Testing Chart
    fig.add_trace(
        go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.TPositive'],
               marker_color='crimson',
               name='Positive'), 2, 1)
    fig.add_trace(
        go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.TNegative'],
               marker_color='green',
               name='Negative'), 2, 1)
    fig.add_trace(go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.Deaths'],
                         marker_color='grey',
                         name='Deaths'), 2, 1)

    # Race Chart
    fig.add_trace(
        go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.C_RaceWhite'],
               marker_color='pink',
               name='White'), 2, 2)
    fig.add_trace(
        go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.C_RaceBlack'],
               marker_color='black',
               name='Black'), 2, 2)
    fig.add_trace(
        go.Bar(x=local_counties_county['attributes.County_1'], y=local_counties_county['attributes.C_RaceOther'],
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


geo_json_url = "https://opendata.arcgis.com/datasets/a7887f1940b34bf5a02c6f7f27a5cb2c_0.geojson"
geo_json_data = gpd.read_file(geo_json_url)
geo_json_data['COUNTY'] = geo_json_data['COUNTY'].apply(lambda x: int(str('12') + str(x)))
geo_json_data['COUNTY'] = geo_json_data['COUNTY'].replace([12025],12086)

broward = geo_json_data['County_1'] == 'Broward'
dade = geo_json_data['County_1'] == 'Dade'
collier = geo_json_data['County_1'] == 'Collier'
monroe = geo_json_data['County_1'] == 'Monroe'
local_counties_county = pd.DataFrame()
local_counties_county = local_counties_county.append(geo_json_data[broward], ignore_index=True)
local_counties_county = local_counties_county.append(geo_json_data[dade], ignore_index=True)
local_counties_county = local_counties_county.append(geo_json_data[collier], ignore_index=True)
local_counties_county = local_counties_county.append(geo_json_data[monroe], ignore_index=True)

fig = px.choropleth(local_counties_county, geojson=counties, locations='COUNTY', color='Deaths',
                           color_continuous_scale="Viridis", hover_name='COUNTYNAME',
                           hover_data=["T_positive", "T_negative"],
                           range_color=(0, 1000),
                           scope="usa"
                          )
fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0}
)
fig.update_geos(
    projection={'scale':8},
    center={'lat': 27.6648, 'lon': -81.5158},
    visible=False
)
fig.show()