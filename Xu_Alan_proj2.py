import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

# US State Abbreviation and Full Name Dictionary
# Credit To: https://gist.github.com/rogerallen/1583593
# added District of Columbia
us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
    "District Of Columbia": "DC"
}

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
    soup = BeautifulSoup(r.content, features='lxml')
    return soup

def extract_state_data():
    soup = get_state_data(2021)
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
    df = pd.DataFrame(list(zip(state,gdp)), columns=['state','2021_gdp'])
    soup = get_state_data(2022)
    i = 5
    gdp = []
    while i < len(soup.find_all('td')):
        gdp.append(soup.find_all('td')[i].text.strip())
        i += 4
    df.insert(2, "2022_gdp", gdp, True)
    state_abbrev = []
    for i in range(len(df)):
        state_abbrev.append(us_state_to_abbrev[df.iloc[i,0]])
    df.insert(1, "state_abbrev", state_abbrev, True)
    return(df)

def state_gdp_sql(df):
    conn = sqlite3.connect('covid.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS GDP')
    cur.execute("CREATE TABLE GDP (state TEXT, abbrev TEXT PRIMARY KEY, twenty_one INTEGER, twenty_two INTEGER)")
    for i in range(len(df)):
        cur.execute(
            "INSERT INTO GDP VALUES (?,?,?,?)",
            (df.iloc[i,0], df.iloc[i,1], df.iloc[i,2], df.iloc[i,3])
        )
    conn.commit()
    conn.close()

gdp_df = extract_state_data()
state_gdp_sql(gdp_df)

def read_population():
    df = pd.read_csv('2019_census.csv')
    state_abbrev = []
    for i in range(len(df)):
        state_abbrev.append(us_state_to_abbrev[df.iloc[i,0]])
    df.insert(1, "state_abbrev", state_abbrev, True)
    return df
population_df = read_population()

def population_sql(df):
    conn = sqlite3.connect('covid.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS POPULATION')
    cur.execute("CREATE TABLE POPULATION (state TEXT, abbrev TEXT PRIMARY KEY, pop INTEGER, lat REAL, long REAL)")
    for i in range(len(df)):
        cur.execute(
            "INSERT INTO POPULATION VALUES (?,?,?,?,?)",
            (df.iloc[i,0], df.iloc[i,1], int(df.iloc[i,2]), df.iloc[i,3], df.iloc[i,4])
        )
    conn.commit()
    conn.close()
population_sql(population_df)