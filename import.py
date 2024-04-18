import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

def get_covid_data():
    url = "https://api.covidactnow.org/v2/states.timeseries.csv?apiKey=008bdf8389d94615b0696d4ff363b0e3"
    try:
        r=requests.get(url)
    except:
        raise Exception("Failed to access API") 
    r_content = r.content
    with open("covid.csv", 'wb') as file:
        file.write(r_content)
        file.close()
    return pd.read_csv('covid.csv')

def covid_sql(df):
    conn = sqlite3.connect('covid.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS COVID')
    cur.execute("CREATE TABLE COVID (date DATE, state TEXT, cases INTEGER)")
    for i in range(len(df)):
        cur.execute(
            "INSERT INTO COVID VALUES (?,?,?)",
            (df.iloc[i,0], df.iloc[i,1], df.iloc[i,2])
        )
    conn.commit()
    conn.close()

df = get_covid_data()
# for now i am only interested in these three columns
df = df.loc[:,['date','state','actuals.cases']]
covid_sql(df)

def get_state_data(year):
    url = f"https://fred.stlouisfed.org/release/tables?rid=455&eid=821184&od={year}-10-01#"
    try:
        r=requests.get(url)
    except:
        raise Exception("Failed to access webpage") 
    soup = BeautifulSoup(r.content)
    return soup

def extract_state_data():
    for y in (2021,2022):
        soup = get_state_data(y)
        i = 9
        state = []
        while i < len(soup.find_all('th')):
            state.append(soup.find_all('th')[i].text.strip())
            i += 1
        gdp = []
        i = 5
        while i < len(soup.find_all('td')):
            gdp.append(soup.find_all('td')[i].text.strip())
            i += 4
        result = {}
        


extract_state_data()
