from pathlib import Path
import pandas as pd
import streamlit as st
import sqlite3
import pandas.io.sql as psql
import pydeck as pdk
import os
import matplotlib.pyplot as plt
import numpy

@st.cache_data
def read_data():
    conn = sqlite3.connect('covid.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    query = "SELECT * FROM COVID"
    covid = psql.read_sql(query,conn)
    query = "SELECT * FROM GDP"
    gdp = psql.read_sql(query,conn)
    query = "SELECT * FROM POPULATION"
    pop = psql.read_sql(query,conn)
    conn.commit()
    conn.close()
    return (covid,gdp,pop)

covid,gdp,pop = read_data()
covid['date'] = pd.to_datetime(covid['date'], format='%Y-%m-%d')
covid_2021 = covid.loc[(covid['date'] >= '2021-01-01') & (covid['date'] <= '2021-12-31')]
covid_2022 = covid.loc[(covid['date'] >= '2022-01-01') & (covid['date'] <= '2022-12-31')]
covid_sum_2021 = covid_2021[['state','cases']].groupby(['state']).sum()
covid_sum_2022 = covid_2022[['state','cases']].groupby(['state']).sum()
covid_sum_2021 = covid_sum_2021.drop("MP")
covid_sum_2021 = covid_sum_2021.drop("PR")
covid_sum_2022 = covid_sum_2022.drop("MP")
covid_sum_2022 = covid_sum_2022.drop("PR")
pop.set_index('abbrev', inplace=True)
gdp.set_index('abbrev', inplace=True)
pop.reindex(covid_sum_2021.index)
gdp.reindex(covid_sum_2021.index)
covid_sum_2021['per_10k'] = covid_sum_2021['cases'] / (pop['pop'] / 10000)
covid_sum_2022['per_10k'] = covid_sum_2022['cases'] / (pop['pop'] / 10000)
gdp_one = []
for i in gdp['twenty_one']:
    if isinstance(i, str):
        gdp_one.append(int(i.replace(",","")))
    else:
        gdp_one.append(int(i))
gdp['one_per10k'] = gdp_one / (pop['pop'] / 10000)
gdp_two = []
for i in gdp['twenty_two']:
    if isinstance(i, str):
        gdp_two.append(int(i.replace(",","")))
    else:
        gdp_two.append(int(i))
gdp['two_per10k'] = gdp_two / (pop['pop'] / 10000)
one = pd.DataFrame({'cases': covid_sum_2021['per_10k'],'gdp': gdp['one_per10k']})
two = pd.DataFrame({'cases': covid_sum_2022['per_10k'],'gdp': gdp['two_per10k']})

main_tab, research_questions, dataframe = st.tabs(['Data and visualizations', 'Research Questions', 'Dataframe'])
with main_tab:
    st.header('Alan Xu', divider='violet')
    st.subheader('Please click through the tabs to look at questions or raw dataframe. The left bar can be used to look at the two years of interest.')
    st.subheader('The first bar graph shows the covid cases for 2021 and 2022 for each state. The second line graph shows relationship between gdp per 10k and covid cases per 10k.')
    st.header('COVID Cases Per State for 2021 & 2022', divider='violet')
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('2021 COVID Cases')
            st.dataframe(covid_sum_2021)
        with col2:
            st.subheader('2022 COVID Cases')
            st.dataframe(covid_sum_2022)
    with st.sidebar:
        year=st.selectbox(
            "Choose which year you would like to visualize COVID cases?",
            ("2021","2022")
        )
    if year=='2021':
        st.bar_chart(covid_sum_2021)
        st.line_chart(one, x="gdp", y="cases")
    else:
        st.bar_chart(covid_sum_2022)
        st.line_chart(two, x="gdp", y="cases")
with research_questions:
     st.markdown('''
        Your webapp should contain a writeup of what you learned doing the project.  On your main project page, you should have the following information:

        1. Your name

        2. An explanation of how to use your webapp: what interactivity there is, what the plots/charts mean, what your conclusions were, etc.

        3. Any major “gotchas” (i.e. things that don’t work, go slowly, could be improved, etc.)
        
        In addition, you’ll need to answer the following questions (they’ll go in a specific page in your webapp.  Don’t worry, we’ll learn how to do that!)

        1. What did you set out to study?  (i.e. what was the point of your project?  This should be close to your Milestone 1 assignment, but if you switched gears or changed things, note it here.)
        
        The goal is to see if there is any association between gdp per 10k population and covid cases per 10k population to assess whether healthcare investment
        affect covid cases number.
                 
        2. What did you Discover/what were your conclusions (i.e. what were your findings?  Were your original assumptions confirmed, etc.?)
        
        The relationship is dubious at best from the visualization. It seems like there may some correlation but the correlation is not strong at all.
                 
        3. What difficulties did you have in completing the project?
        
        Combining different datasets turn out to be more difficult than I thought. There are missing data fields that need to be remove in order to make everything work.
                 
        4. What skills did you wish you had while you were doing the project?
        
        Making maps with the population data and per 10k data would be a nice visualization but it was very hard to do that with streamlit.
                 
        5. What would you do “next” to expand or augment the project?
        
        I would probably use some statistical measure to assess whether the relationship is actually strong or not. A Pearson Correlation might work.
    '''
    )
with dataframe:
    st.dataframe(covid)
    st.dataframe(pop)
    st.dataframe(gdp)
    



    
