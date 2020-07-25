import streamlit as st
import pandas as pd
import requests
import json

import json

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
                          'attributes.County_1','attributes.DEPCODE', 'attributes.COUNTY',
                          'geometry.rings', 'attributes.Shape__Length', 'attributes.Shape__Area'], axis=1)


broward = raw_data['attributes.COUNTYNAME'] == 'BROWARD'
dade = raw_data['attributes.COUNTYNAME'] == 'DADE'
collier = raw_data['attributes.COUNTYNAME'] == 'COLLIER'
local_counties = raw_data[broward]
local_counties = local_counties.append(raw_data[dade])
local_counties = local_counties.append(raw_data[collier])
st.write(local_counties)








