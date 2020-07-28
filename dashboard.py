import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import geopandas as gpd

# Select box to switch between the two pages
view_picker = st.sidebar.selectbox('Change View', ('Risk Profile Survey', "Daily Risk Profile Survey", "Risk Profile",
                                                   'Local Covid Tracker'))
if view_picker == 'Risk Profile Survey':
    components.iframe(
        'https://docs.google.com/forms/d/e/1FAIpQLSdkgGD1FK7c6ZcGAQP4lavawr_yxczSdDAbpzXarZymPpJvLA/viewform?embedded=true',
        scrolling=True,
        height=800)
elif view_picker == 'Daily Risk Profile Survey':
    components.iframe(
        'https://docs.google.com/forms/d/e/1FAIpQLSe1RYfDpImWdoHulRn4uYVP5aLnfCxfTwyGBvsplZ4GFugfnQ/viewform?embedded=true',
        scrolling=True,
        height=800)
elif view_picker == 'Risk Profile':
    st.title('Risk Profile')
    # TODO: put the risk profile code here
    # TODO: need a way to view individual data, dont bother to make it secure; simple pid lookup should be fine
    # TODO: compare risk profiles by college, county, etc
    # TODO: WE GOT THIS!

    pass
elif view_picker == 'Local Covid Tracker':
    st.title('Local COVID-19 Tracker')
    st.subheader("Select \"State\" to view the entire State data")

    state_data_url = "https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/Florida_COVID19_Case_Line_Data_NEW/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
    county_geo_json_url = "https://opendata.arcgis.com/datasets/a7887f1940b34bf5a02c6f7f27a5cb2c_0.geojson"
    county_codes_url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'


    @st.cache
    def getData(api):
        with requests.get(api) as data:
            return data


    @st.cache(allow_output_mutation=True)
    def createGPD(api):
        data = gpd.read_file(api)

        # County Data Preprocessing
        data['COUNTY'] = data['COUNTY'].apply(lambda x: int(str('12') + str(x)))
        data['COUNTY'] = data['COUNTY'].replace([12025], 12086)
        return data


    # TODO: Remove state data if not used
    # Getting the data
    state_data = getData(state_data_url)
    county_data = createGPD(county_geo_json_url)
    counties = getData(county_codes_url).json()

    if county_data is None:
        st.write("API DOWN!")
        exit(0)

    # State Data Preprocessing
    state_data = state_data.json()['features']
    state_data = pd.json_normalize(state_data)
    state_data = state_data.drop(['attributes.Case1', 'attributes.EventDate', 'attributes.ChartDate',
                                  'attributes.ObjectId'], axis=1)

    # Multiselect box
    county_picker = st.sidebar.multiselect('Select County',
                                           list(county_data['County_1'].sort_values()),
                                           ['Dade', 'Broward', 'Monroe', 'Collier']
                                           )
    if "State" in county_picker:
        local_counties_county = pd.DataFrame()
        selected = county_data['County_1'] != 'State'
        local_counties_county = local_counties_county.append(county_data[selected], ignore_index=True)
    else:
        local_counties_county = pd.DataFrame()
        for x in county_picker:
            selected = county_data['County_1'] == x
            local_counties_county = local_counties_county.append(county_data[selected], ignore_index=True)

    # st.write(county_data) # TODO: Only for debugging; remove

    if not county_picker:
        st.write('## **Select a county**')
    else:
        fig = go.Figure()
        fig = make_subplots(rows=3, cols=2,
                            specs=[[{'type': 'domain'}, {'type': 'domain'}], [{'type': 'xy'}, {'type': 'xy'}],
                                   [{'type': 'xy', 'colspan': 2}, None]],
                            subplot_titles=('', '', 'Testing Results', 'Cases by Race'))

        # Indicator
        fig.add_trace(go.Indicator(
            value=local_counties_county['Deaths'].values.sum(),
            title={"text": "Deaths"},
            domain={'x': [0, 0.5], 'y': [0.6, 0.5]}), 1, 1)

        fig.add_trace(go.Indicator(
            value=local_counties_county['T_positive'].values.sum(),
            title={"text": "Total Positive Cases"},
            domain={'x': [0.8, 1], 'y': [0, 1]}), 1, 2)

        # Testing Chart
        fig.add_trace(
            go.Bar(x=local_counties_county['County_1'], y=local_counties_county['T_positive'],
                   marker_color='crimson',
                   name='Positive'), 2, 1)
        fig.add_trace(
            go.Bar(x=local_counties_county['County_1'], y=local_counties_county['T_negative'],
                   marker_color='green',
                   name='Negative'), 2, 1)
        fig.add_trace(go.Bar(x=local_counties_county['County_1'], y=local_counties_county['Deaths'],
                             marker_color='grey',
                             name='Deaths'), 2, 1)

        # Race Chart
        fig.add_trace(
            go.Bar(x=local_counties_county['County_1'], y=local_counties_county['C_RaceWhite'],
                   marker_color='pink',
                   name='White'), 2, 2)
        fig.add_trace(
            go.Bar(x=local_counties_county['County_1'], y=local_counties_county['C_RaceBlack'],
                   marker_color='black',
                   name='Black'), 2, 2)
        fig.add_trace(
            go.Bar(x=local_counties_county['County_1'], y=local_counties_county['C_RaceOther'],
                   marker_color='orchid',
                   name='Other'), 2, 2)
        # Median Age Chart
        fig.add_trace(
            go.Bar(x=local_counties_county['County_1'], y=local_counties_county['MedianAge'],
                   marker_color='darkturquoise',
                   name='Median Age'), 3, 1)
        fig.update_layout(height=800, width=800,
                          legend=dict(
                              yanchor="top",
                              y=.43,
                              xanchor="left",
                              x=1
                          )
                          )
        st.plotly_chart(fig)

        t1 = local_counties_county['Age_0_4'].sum()
        t2 = local_counties_county['Age_5_14'].sum()
        t3 = local_counties_county['Age_15_24'].sum()
        t4 = local_counties_county['Age_25_34'].sum()
        t5 = local_counties_county['Age_35_44'].sum()
        t6 = local_counties_county['Age_45_54'].sum()
        t7 = local_counties_county['Age_55_64'].sum()
        t8 = local_counties_county['Age_65_74'].sum()

        age = ['Age:0-4', 'Age:5-14', 'Age:15-24', 'Age:25-34', 'Age:35-44', 'Age:45-54', 'Age:55-64', 'Age:65-74']
        Cases_by_Age = pd.DataFrame({'Case_Totals': [t1, t2, t3, t4, t5, t6, t7, t8], 'Age_Group': age})
        colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen', 'skyblue', 'lightpurple']
        fig = px.pie(Cases_by_Age, values="Case_Totals", names='Age_Group', title='Cases by Age Group')
        fig.update_traces(hoverinfo='label', textinfo='percent', textfont_size=15,
                          marker=dict(colors=colors, line=dict(color='#000000', width=1)))
        st.plotly_chart(fig)

        map_data = st.selectbox("Map Select:", (
            'Deaths', "T_positive", "T_negative", "MedianAge", 'C_RaceWhite', 'C_RaceBlack', 'C_RaceOther'), 0)
        fig = px.choropleth(local_counties_county, geojson=counties, locations='COUNTY', color=map_data,
                            color_continuous_scale="Viridis", hover_name='COUNTYNAME',
                            hover_data=["T_positive", "T_negative"],
                            scope="usa",
                            title="Map View"
                            )
        fig.update_geos(
            projection={'scale': 6},
            center={'lat': 27.6648, 'lon': -81.5158},
            visible=False
        )
        st.plotly_chart(fig)
