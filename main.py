import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
from urllib.request import urlopen
import json
import plotly.express as px
import plotly

with st.echo(code_location='below'):
    @st.cache
    def get_data():
        '''
        Downloads Zillow data from https://www.zillow.com/research/data/ and counties geojson info for the USA.
        '''
        home_values_metro = pd.read_csv('https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')
        home_values_state = pd.read_csv('https://files.zillowstatic.com/research/public_csvs/zhvi/State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')
        home_values_county = pd.read_csv('https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')
        home_values_city = pd.read_csv('https://files.zillowstatic.com/research/public_csvs/zhvi/City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')
        home_values_zip = pd.read_csv('https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')
        home_rent_metro = pd.read_csv('https://files.zillowstatic.com/research/public_csvs/zori/Metro_ZORI_AllHomesPlusMultifamily_Smoothed.csv')
        home_rent_zip = pd.read_csv('https://files.zillowstatic.com/research/public_csvs/zori/Zip_ZORI_AllHomesPlusMultifamily_Smoothed.csv')
        with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
            counties = json.load(response)
        return [home_values_metro, home_values_state, home_values_county, home_values_city, home_values_zip, home_rent_metro, home_rent_zip, counties]

    home_values_metro, home_values_state, home_values_county, home_values_city, home_values_zip, home_rent_metro, home_rent_zip, counties = get_data()

    ### FROM: https://gist.githubusercontent.com/rugbyprof/76575b470b6772ce8fa0c49e23931d97/raw/eb731ce40f9c7c032f4db42e96889a3adbe54f8e/states.py
    abbr = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]
    states = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}
    ### END FROM
    states_inv = {state: abbr for abbr, state in states.items()}


    st.write('# Visualizing the US housing market')

    st.write('Zillow maintains a detailed database on the US housing market. Let\'s have a look at it.')

    st.write('## House values')



    year = st.slider('Select a year', 2000, 2022, 2022, key = 'state_value')
    data_key = str(year) + '-01-31'
    fig = px.choropleth(home_values_state, locationmode="USA-states",
                           locations = 'StateName',
                           color=data_key,
                           color_continuous_scale="Temps",
                           scope="usa",
                           hover_name = 'RegionName',
                           labels={data_key:'Price'},
                           title = f'House price index by state, {year}'
                          )
    st.plotly_chart(fig)

    home_values_county['FIPS'] = home_values_county['StateCodeFIPS'].map(str).str.zfill(2)+home_values_county['MunicipalCodeFIPS'].map(str).str.zfill(3)

    scale = st.radio(
     'Should the data be plotted on a logarithmic color scale?',
     ('Yes, show me the logarithmic version', 'No, show me the linear version'))

    if scale == 'Yes, show me the logarithmic version':
        year = st.slider('Select a year', 2000, 2022, 2022, key = 'county_value_log')
        data_key = str(year) + '-01-31'
        home_values_county_log = pd.DataFrame()
        home_values_county_log['FIPS'] = home_values_county['FIPS']
        home_values_county_log['RegionName'] = home_values_county['RegionName']
        home_values_county_log[data_key] = np.log(home_values_county[data_key])
        fig = px.choropleth(home_values_county_log, geojson=counties,
                               locations='FIPS',
                               color=data_key,
                               hover_data = ['RegionName'],
                               color_continuous_scale="Temps",
                               scope="usa",
                               labels={data_key:'ln(Price)'},
                               title = f'House price index by county, {year}, log'
                              )
        st.plotly_chart(fig)
    else:
        year = st.slider('Select a year', 2000, 2022, 2022, key = 'county_value_lin')
        data_key = str(year) + '-01-31'
        fig = px.choropleth(home_values_county, geojson=counties,
                               locations='FIPS',
                               color=data_key,
                               hover_data = ['RegionName'],
                               color_continuous_scale="Temps",
                               scope="usa",
                               labels={data_key:'Price'},
                               title = f'House price index by county, {year}, lin'
                              )
        st.plotly_chart(fig)


    @st.cache(allow_output_mutation=True)
    def get_timeseries_home_values_state():
        timeseries_home_values_state = home_values_state.T.drop(['RegionID', 'SizeRank', 'RegionType', 'StateName'], axis = 0)
        timeseries_home_values_state.columns = timeseries_home_values_state.iloc[0]
        timeseries_home_values_state = timeseries_home_values_state.drop('RegionName')
        return timeseries_home_values_state

    timeseries_home_values_state = get_timeseries_home_values_state()

    states_timeseries_plot = st.multiselect('Select states:', list(timeseries_home_values_state.columns))
    timeseries_home_values_state = timeseries_home_values_state[states_timeseries_plot].reset_index()
    timeseries_home_values_state['index'] = timeseries_home_values_state['index'].str[:4].astype(int)
    timeseries_home_values_state = timeseries_home_values_state.groupby('index').mean().reset_index()
    timeseries_home_values_state = timeseries_home_values_state.set_index('index')

    fig, ax = plt.subplots()
    sns.lineplot(data=timeseries_home_values_state, ax = ax)
    ax.set(xlabel='year')
    ax.set_title('House prices in selected states')
    st.pyplot(fig)

    state = st.selectbox('Select a state:', states_inv.keys(), key = 'hist_value_state')
    year = st.slider('Select a year', 2000, 2022, 2022, key = 'hist_value_year')
    data_key = str(year) + '-01-31'
    fig, ax = plt.subplots()
    sns.histplot(data=home_values_zip[home_values_zip['State'] == states_inv[state]][data_key], ax = ax, color = 'thistle')
    ax.set(xlabel='price')
    ax.set_title(f'Distribution of house prices by zip code in {state} in {year}')
    st.pyplot(fig)

    home_rent_zip['State'] = home_rent_zip['MsaName'].str[-2:]
    state = st.selectbox('Select a state:', states_inv.keys(), key = 'hist_rent_state')
    year = st.slider('Select a year', 2014, 2022, 2022, key = 'hist_rent_year')
    data_key = str(year) + '-01'
    fig, ax = plt.subplots()
    sns.histplot(data=home_rent_zip[home_rent_zip['State'] == states_inv[state]][data_key], ax = ax, color = 'thistle')
    ax.set(xlabel='price')
    ax.set_title(f'Distribution of rent by zip code in {state} in {year}')
    st.pyplot(fig)

    # regr between rent and price (by zip vs by state vs by city)
    # use altair
