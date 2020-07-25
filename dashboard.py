import streamlit as st
import pandas as pd
import requests
import json

import json

st.title('Local COVID-19 Tracker')

url = 'https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/Florida_COVID19_Case_Line_Data_NEW/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'

try:
    status = requests.get(url)
except:
    st.write('## **API DOWN!**')

query = requests.get(url)
query = query.json()['features']
query = pd.json_normalize(query)
st.write(query)







