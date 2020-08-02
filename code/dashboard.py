import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

import requests
from PIL import Image

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

import geopandas as gpd
import geoplot as gplt

# Select box to switch between the two pages
view_picker = st.sidebar.selectbox('Change View', ('Local COVID-19 Cases Analysis',
                                                   "Risk Profile Dashboard",
                                                   'Risk Profile Survey',
                                                   "Daily Risk Profile Survey"
                                                   )
                                   )

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
elif view_picker == 'Risk Profile Dashboard':
    st.title('Risk Profile Dashboard')
    components.iframe(
        'https://public.tableau.com/views/Risk_Profile2_0/Dashboard1?:showVizHome=no&:embed=true',
        scrolling=True,
        height=900,
        width=1000)
    '''
    # Daily
    '''
    components.iframe(
        'https://public.tableau.com/views/New_Daily/DailyProfile?:showVizHome=no&:embed=true',
        scrolling=True,
        height=900,
        width=1000)
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
    fdoh_data = pd.read_csv('../data/fdoh-data.csv')
    fdoh_data = fdoh_data.drop([0]).rename(columns={'Unnamed: 0': 'County', 'Unnamed: 1': "FIPS"})
    df = county_data[['County_1', 'SHAPE_Length', 'SHAPE_Area', 'geometry']].rename(
        columns={'County_1': 'County'})
    fdoh_data = pd.merge(fdoh_data, df, on='County')
    fdoh_data['FIPS'] = fdoh_data['FIPS'].apply(lambda x: x.replace('-', ''))

    '''
    # Objective
    
    Our goal as a team is to identify how can students and FIU partner together to help safely open
    the campus for classes.
    # Assumptions
    
    In our analysis we will be looking at county level data to see how prevalent the risk factors
    as announced by the CDC are in our community. Factors such as:
    - Age
    - Ethnicity
    - Respiratory Diseases
    - Risky Behavior
    - Current Situation
    '''

    '''
    # Age

    Most public health organizations have stated that age is a key indicator of how sick a patient may get from 
    COVID-19. 60 up tends to be the general age where COVID can pose a high life threatening issue. '''

    gplt.choropleth(
        fl_demo, hue='TotalPopul',
        cmap='Reds', figsize=(14, 5),
        legend=True,
        edgecolor='white'
    )
    plt.title('Total Population')
    st.pyplot()

    '''
    Dade and Broward are the most populated areas in Florida as such we would expect the spread to be 
    centered around these two counties.
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
    From this chart we can see that the two counties near FIU Broward and Dade also has the largest 
    population of people over the age of 65. One thing to note is that the data used was collected 
    5 years ago.
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
    From the data we can see that the largest age range that has tested positive for COVID-19 is 25 
    up but more importantly the area around FIU is a hot spot. As such taking age in to consideration
    people older than 60 should remain in quarantine with schools opening we will see an influx in 
    cases starting at a much younger age which could have unforeseen consequences. The risk index for
    anyone above the age of 60 would be high and depending on underlying health conditions younger
    individuals will need to be classified. 

    # Ethnicity

    According to the CDC there does exist an inequality in the system which puts minorities at a 
    higher risk for contracting the virus. This can be due to multiple reasons such as discrimination, 
    health care access, occupation, education, housing or all of the above.
    '''

    minority = county_data['C_RaceBlack'] + county_data['C_HispanicYES'] + county_data['C_RaceOther']

    sns.barplot(x=['White', 'Black', 'Hispanic', 'Other', 'Combined Minority'],
                y=[county_data['C_RaceWhite'].sum(),
                   county_data['C_RaceBlack'].sum(), county_data['C_HispanicYES'].sum(),
                   county_data['C_RaceOther'].sum(), minority.sum()])
    plt.title('COVID Cases by Race')
    st.pyplot()

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
    We can see from the map that the cases for minorities near FIU is the highest in the State. With FIU 
    serving primarily minorities this puts our campus at a higher risk of being a hot spot for the 
    spread of the virus if proper precautions are not taken. As we will be seeing students coming 
    from Miami-Dade and Broward which are the largest hot spots in Florida.

    # Respiratory Diseases
    
    Various underlying health issues can increase the risk factor for an individual significantly we will
    take a look at the respiratory disease as a base line for its the one that aligns most closely with
    the symptoms of the virus.    
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

    '''
    The concentration of respiratory illness taken from 2018 data as shown above is centered around 
    Dade and Broward areas. The number of ER room visits should be looked at with a bit of skepticism 
    however taking a look at the hospitalizations we can see that there is a high probability that a 
    person who has a respiratory illness is in the Dade and Broward areas which significantly increases 
    their risk index from COVID.
    '''

    '''
    # Risky Behaviors
    
    We will be referencing this [report](https://www.gstatic.com/covid19/mobility/2020-07-27_US_Florida_Mobility_Report_en.pdf)
    released by google for this section.
    
    Taking a look at this report from Google on how these two communities have coped with the virus
    we can see that people are actively trying to avoid places such as transit stations, parks and
    following mandated work from home policies. However it's interesting that from the baseline we are
    seeing only a minor decrease to retail & recreation. We know that the virus is spreading in these
    two communities and as such we can infer that the hot spot for these transmissions are currently
    retail & recreation activities and grocery & pharmacy stores. After which it may spread within
    the household with increased contact.    
    '''
    dade = Image.open('../image/dade-mobility.PNG')
    broward = Image.open('../image/broward-mobility.PNG')

    st.image(dade, caption='Dade Mobility Report',
             use_column_width=True)

    st.image(broward, caption='Broward Mobility Report',
             use_column_width=True)

    '''
    The concentration of respiratory illness taken from 2018 data as shown above is centered around 
    Dade and Broward areas. The number of ER room visits should be looked at with a bit of skepticism 
    however taking a look at the hospitalizations we can see that there is a high probability that a 
    person who has a respiratory illness is in the Dade and Broward areas which significantly increases 
    their risk index from COVID.
    '''

    '''
    # Current Situation
    
    Below is a quick snapshot of the current COVID-19 data.
    '''
    st.info("Select \"State\" to view the entire State data")
    fig = go.Figure()
    fig = make_subplots(rows=3, cols=2,
                        specs=[[{'type': 'domain', 'colspan': 2}, None], [{'type': 'xy'}, {'type': 'xy'}],
                               [{'type': 'xy', 'colspan': 2}, None]],
                        subplot_titles=('', 'Testing Results', 'Cases by Race', "Median Age"))

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
            go.Bar(x=local_counties_county['County_1'],
                   y=local_counties_county['C_RaceWhite'],
                   marker_color='pink',
                   name='White'), 2, 2)
        fig.add_trace(
            go.Bar(x=local_counties_county['County_1'], y=local_counties_county['C_RaceBlack'],
                   marker_color='black',
                   name='Black'), 2, 2)
        fig.add_trace(
            go.Bar(x=local_counties_county['County_1'], y=local_counties_county['C_HispanicYES'],
                   marker_color='orchid',
                   name='Hispanic'), 2, 2)
        fig.add_trace(
            go.Bar(x=local_counties_county['County_1'], y=local_counties_county['C_RaceOther'],
                   marker_color='yellow',
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

        '''
        From the charts above we can see that there is a significant amount of positive test cases
        in the area. With schools reopening this Fall this is concerning news that should be taken in to
        consideration. What is concerning is from the data we have seen that the largest age group is that
        has been affected are adults above the age of 25 years old. Which indicates that school aged
        individuals have not been exposed to the virus due to quarantine efforts. We may see a change in this
        trend if schools are not prepared to handle large amounts of on campus students.
        '''
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

        cases_by_zip = Image.open('../image/cases_zip.PNG')
        st.image(cases_by_zip, caption='Positive Cases by Zip')

    '''
    # Conclusion
    
    From the data we know that South Florida more precisely the Dade and Broward are the two most infected
    communities. We know that the number of cases is increasing and with schools reopening in a few weeks
    we need to prepare for how to handle on campus students. As such our solution is to create a monitoring
    tool which will allow students to track the risk factor of attending classes. This tool will gather 
    data anonymously and aggregate a risk monitoring dashboard which students may view. The risk factor
    will be generated the using students personal factors combined with community risk factors. The detail at which
    administrators would like this dashboard to be would depend on the granularity of the data collected. 
    We have created a proof of concept of what we think such an application might look like. With the goal
    that administration can use this data as a guide for campus safety and students for risk management.  
    '''

    '''
    # Reference
    
    - https://dai-global-digital.com/covid-19-data-analysis-part-1-demography-behavior-and-environment.html#Factor-1:-Age
    - https://dai-global-digital.com/covid-19-data-analysis-part-2-health-capacity-and-preparedness.html
    - https://catalyst.nejm.org/doi/full/10.1056/CAT.20.0116
    - https://www.cdc.gov/coronavirus/2019-ncov/community/health-equity/race-ethnicity.html

    # Data Source

    - https://hub.arcgis.com/datasets/61a30fb3ea4c43e4854fbb4c1be57394_0    
    - https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data/geoservice
    - https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-cases-by-county
    - https://www.floridatracking.com/healthtracking/mapview.htm?i=5250&g=3&t=2018&ta=0&it=1
    - https://www.gstatic.com/covid19/mobility/2020-07-27_US_Florida_Mobility_Report_en.pdf
    '''
