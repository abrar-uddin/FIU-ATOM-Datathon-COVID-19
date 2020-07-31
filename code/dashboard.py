import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import geopandas as gpd
import datetime

import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

import geoplot as gplt

# Select box to switch between the two pages
view_picker = st.sidebar.selectbox('Change View', ('Risk Profile Survey', "Daily Risk Profile Survey", "Risk Profile",
                                                   'Local COVID-19 Cases Analysis'))

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
    panther_id = st.sidebar.text_input("Panther ID:")
    components.iframe(
        'https://public.tableau.com/views/FarenetAnomalies/AnomaliesDashboard?:showVizHome=no&:embed=true',
        scrolling=True,
        height=900,
        width=1500)
elif view_picker == 'Local COVID-19 Cases Analysis':
    st.title('Local COVID-19 Cases Analysis')

    county_geo_json_url = "https://opendata.arcgis.com/datasets/a7887f1940b34bf5a02c6f7f27a5cb2c_0.geojson"
    county_codes_url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
    fl_demo_url = 'https://opendata.arcgis.com/datasets/61a30fb3ea4c43e4854fbb4c1be57394_0.geojson'


    def api_check(url):
        with requests.get(url) as test:
            test = test

        if test.status_code != 200:
            st.error("API DOWN!")
            exit(0)


    api_check(county_geo_json_url)
    api_check(county_codes_url)
    api_check(fl_demo_url)


    @st.cache
    def getData(api):
        with requests.get(api) as data:
            return data


    @st.cache(allow_output_mutation=True)
    def createGPD(api):

        data = gpd.read_file(api)

        if api is county_geo_json_url:
            # County Data Preprocessing
            data['COUNTY'] = data['COUNTY'].apply(lambda x: int(str('12') + str(x)))
            data['COUNTY'] = data['COUNTY'].replace([12025], 12086)

        return data


    @st.cache
    def make_map():
        pass


    # Getting the data
    county_data = createGPD(county_geo_json_url)
    counties = getData(county_codes_url).json()
    fl_demo = createGPD(fl_demo_url)

    # Environmental/Disease Data
    fdoh_data = pd.read_csv('C:/Users/uddin/Downloads/FIU-ATOM-Datathon-COVID-19/data/fdoh-data.csv')
    fdoh_data = fdoh_data.drop([0]).rename(columns={'Unnamed: 0': 'County', 'Unnamed: 1': "FIPS"})
    df = county_data[['County_1', 'SHAPE_Length', 'SHAPE_Area', 'geometry']].rename(
        columns={'County_1': 'County'})
    fdoh_data = pd.merge(fdoh_data, df, on='County')
    fdoh_data['FIPS'] = fdoh_data['FIPS'].apply(lambda x: x.replace('-', ''))

    # fl_demo.head(2)
    #
    # county_data.head(2)
    #
    # fdoh_data.head(2)

    '''
        # Assumptions

        Dade and Broward are the most populated areas in Flordia as such we need to take that in to account as we analyze our data.
        '''

    gplt.choropleth(
        fl_demo, hue='TotalPopul',
        cmap='Reds', figsize=(14, 5),
        legend=True,
        edgecolor='white'
    )
    plt.title('Total Population')
    st.pyplot()
    '''
    # Age

    Most public health organizations have stated that age is a key indicator of how sick a paitient may get from COVID-19. 60 up tends to be the general age where COVID can pose a high life threatening issue.
    '''

    gplt.choropleth(
        fl_demo, hue='Pop_65andO',
        cmap='Blues', figsize=(14, 5),
        legend=True,
        edgecolor='white'
    )
    plt.title('Population Over the Age of 65')
    st.pyplot()

    '''
    From this chart we can see that the two counties near FIU Broward and Dade have the largest population of people over the age of 65. One thing to note is that the data used was collected 5 years ago.
    '''

    sns.barplot(x=['0-4', '5-14', '15-24', '25-34', '35-44', '45-54', '55-64', '65-74', '85plus'],
                y=[county_data['Age_0_4'].sum(), county_data['Age_5_14'].sum(), county_data['Age_15_24'].sum(),
                   county_data['Age_25_34'].sum(), county_data['Age_35_44'].sum(), county_data['Age_45_54'].sum(),
                   county_data['Age_55_64'].sum(), county_data['Age_65_74'].sum(), county_data['Age_85plus'].sum()])
    plt.title('Covid Cases by Age')
    st.pyplot()

    fig = px.choropleth(county_data, geojson=counties, locations='COUNTY', color='T_positive',
                        color_continuous_scale="Viridis", hover_name='COUNTYNAME',
                        hover_data=['Age_0_4', 'Age_5_14', 'Age_25_34', 'Age_35_44', 'Age_45_54', 'Age_55_64',
                                    'Age_65_74', 'Age_85plus'],
                        scope="usa",
                        title="Positive Test Cases",
                        range_color=(0, 10000)
                        )
    fig.update_geos(
        projection={'scale': 4},
        center={'lat': 27.6648, 'lon': -81.5158},
        visible=False
    )
    st.plotly_chart(fig)

    '''
    From the data we can see that the largest age range that has tested positive for COVID-19 is 25 up but more importantly the area aroud FIU is a hotspot. As such taking age in to considerations people older that 60 should remain in quarantine with schools opening we will see an influx in cases starting at a much younger age which could have unforeseen consequences.

    # Ethnicity

    According to the CDC there does exist a inequality in the system which puts minorities at a higher risk for contracting the virus. This can be due to multiple reasons such as discrimination, healthcare access, occupation, education, housing or all of the above.
    '''

    sns.barplot(x=['White', 'Black', 'Hispanic', 'Other'],
                y=[county_data['C_RaceWhite'].sum() - county_data['C_HispanicYES'].sum(),
                   county_data['C_RaceBlack'].sum(), county_data['C_HispanicYES'].sum(),
                   county_data['C_RaceOther'].sum()])
    plt.title('Covid Cases by Race')
    st.pyplot()

    minority = county_data['C_RaceBlack'] + county_data['C_HispanicYES'] + county_data['C_RaceOther']
    county_data['Minority'] = minority

    fig = px.choropleth(county_data, geojson=counties, locations='COUNTY', color='Minority',
                        color_continuous_scale="Viridis", hover_name='COUNTYNAME',
                        hover_data=['T_positive'],
                        scope="usa",
                        title="Minority Cases",
                        range_color=(0, 20000)
                        )
    fig.update_geos(
        projection={'scale': 4},
        center={'lat': 27.6648, 'lon': -81.5158},
        visible=False
    )
    st.plotly_chart(fig)

    '''
    We can see from the map that the minority cases near FIU is the highest in the State. With FIU serving primarily minorities this puts our campus at a higher risk of being hot spot for the spread of the virus if proper precautions are not taken. With the cases of Miami-Dade and Broward with the highest concentration.

    # Respiratory Diseases
    '''

    fig = px.choropleth(fdoh_data, geojson=counties, locations='FIPS', color='Number of COPD Hospitalizations',
                        color_continuous_scale="Viridis", hover_name='County',
                        hover_data=[],
                        scope="usa",
                        title='Number of COPD Hospitalizations',
                        labels={'Number of COPD Hospitalizations': 'COPD Cases'}
                        )
    fig.update_geos(
        projection={'scale': 4},
        center={'lat': 27.6648, 'lon': -81.5158},
        visible=False
    )
    st.plotly_chart(fig)
    st.write("*Chronic obstructive pulmonary disease (COPD)")

    fig = px.choropleth(fdoh_data, geojson=counties, locations='FIPS',
                        color='Number of Asthma Emergency Department Visits',
                        color_continuous_scale="Viridis", hover_name='County',
                        hover_data=[],
                        scope="usa",
                        title='Number of Asthma Emergency Department Visits',
                        labels={'Number of Asthma Emergency Department Visits': 'Asthma Cases'}
                        )
    fig.update_geos(
        projection={'scale': 4},
        center={'lat': 27.6648, 'lon': -81.5158},
        visible=False
    )
    st.plotly_chart(fig)

    fig = px.choropleth(fdoh_data, geojson=counties, locations='FIPS', color='Number of Asthma Hospitalizations',
                        color_continuous_scale="Viridis", hover_name='County',
                        hover_data=[],
                        scope="usa",
                        title='Number of Asthma Hospitalizations',
                        labels={'Number of Asthma Hospitalizations': 'Asthma Cases'}
                        )
    fig.update_geos(
        projection={'scale': 4},
        center={'lat': 27.6648, 'lon': -81.5158},
        visible=False
    )
    st.plotly_chart(fig)

    fig = go.Figure()
    fig = make_subplots(rows=3, cols=2,
                        specs=[[{'type': 'domain', 'colspan': 2}, None], [{'type': 'xy'}, {'type': 'xy'}],
                               [{'type': 'xy', 'colspan': 2}, None]],
                        subplot_titles=('', '', 'Testing Results', 'Cases by Race', "Median Age"))

    st.info("Select \"State\" to view the entire State data")
    # Multiselect box
    county_picker = st.multiselect('Select County',
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

    if not county_picker:
        st.write('## **Select a county**')
    else:
        ########
        # Indicator
        fig.add_trace(go.Indicator(
            value=local_counties_county['T_positive'].values.sum(),
            title={"text": "Total Positive Cases"},
            domain={'x': [0.8, 1], 'y': [0, 1]}), 1, 1)

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

        "From the charts above we can see that there is a significant amount of positive test cases" \
        " in the area. With schools reopening this Fall this is concerning news that should be taken in to " \
        " consideration. What is concerning is from the data we have seen that the largest age group is that" \
        " has been affected are adults above the age of 25 years old. Which indicates that school aged" \
        " indivuals have not been exposed to the virus due to quarentine efforts. We may see a change in this" \
        " trend if schools are not prepared to handle large amounts of on campus students."

        # Age group pie chart
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

    '''
    The concentration of respitatory illness taken from 2018 data as shown above is centered around Dade and Broward areas. The number of ER room visits should be looked at with a bit of skepticism however taking a look at the hospitalizations we can see that there is a high probability that a person who has a respiratory illness is in the Dade and Broward areas which significantly increases their risk index from COVID.
    '''

    '''
    # Conclusion
    '''

    '''
    # Reference
    
    https://dai-global-digital.com/covid-19-data-analysis-part-1-demography-behavior-and-environment.html#Factor-1:-Age
    https://dai-global-digital.com/covid-19-data-analysis-part-2-health-capacity-and-preparedness.html
    https://catalyst.nejm.org/doi/full/10.1056/CAT.20.0116
    https://www.cdc.gov/coronavirus/2019-ncov/community/health-equity/race-ethnicity.html
    https://www.floridatracking.com/healthtracking/mapview.htm?i=5250&g=3&t=2018&ta=0&it=1

    # Data Source

    ### Data API
    https://hub.arcgis.com/datasets/61a30fb3ea4c43e4854fbb4c1be57394_0
    https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data/geoservice
    https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-cases-by-county
    '''
