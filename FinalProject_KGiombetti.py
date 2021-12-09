"""
Name: Kaitlynn Giombetti
CS230: Section 5
Data: Boston Crime Data (also uses Police Districts) from Analyze Boston
URL:
Description: This program acts as an interactive website for users to explore using data from Analyze Boston
regarding Boston Crime and Boston Police Districts. The queries allow users to explore the number of shootings
per police district with a bar chart display, a breakdown of the crime per each day of the week with a bar chart
and pie chart for comparison, and finally a map that populates the locations of the crimes based off the chosen
district, month, and day the user chooses.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import pprint as pp
import streamlit as st
import os
import webbrowser
import folium
import pydeck as pdk
import mapbox

def main():
    st.title('Boston Crime Data 2021')
    st.write("Welcome to the 2021 Boston Crime Data Website!")
    st.sidebar.write("Choose your criteria to show your chosen data!")

# read data
def read_crimedata():
    df_BostonCrime = pd.read_csv('bostoncrime2021_7000_sample.csv').set_index("INCIDENT_NUMBER")
    df_BostonCrime.drop(columns=["UCR_PART"])
    return df_BostonCrime

def read_districtdata():
    df_BostonPoliceDistricts = pd.read_csv('BostonPoliceDistricts.csv')
    df_BostonPoliceDistricts.sort_values(by='District', ascending=True)
    return df_BostonPoliceDistricts

# filter data
def filter_data(select_district, select_day, select_month):
    df_BostonCrime = read_crimedata()
    df_BostonCrime = df_BostonCrime.loc[
        df_BostonCrime['DISTRICT'].isin([select_district]) & df_BostonCrime['DAY_OF_WEEK'].isin([select_day]) &
        df_BostonCrime['MONTH'].isin([select_month])]
    return df_BostonCrime

main()
st.write('Hope you enjoy!')

# Query 1 - Police districts and their number of shootings in 2021
st.sidebar.write('Number of Shootings by Police District:\n')

# user chooses police district from radio button
df_DistrictData = read_districtdata()
df_BostonCrime = read_crimedata()
district_shooting = st.sidebar.radio("Please select a district:", df_DistrictData['District'])

# number of shootings chosen district had in 2021 populates
shootingsInDistrict = df_BostonCrime.loc[df_BostonCrime['DISTRICT'].isin([district_shooting])]
print('\n')
st.write(f"The number of shootings in District {district_shooting} is {len(shootingsInDistrict)}.")
print(len(shootingsInDistrict))

# graph that displays number of shootings in each district
for district in df_DistrictData['District']:
    abc = df_BostonCrime.loc[df_BostonCrime['DISTRICT'].isin([district])]
    plt.bar(district, int(len(abc)))
plt.xlabel("District")
plt.ylabel("Number of Shootings")
plt.title("Number of Shootings Per District")
st.pyplot(plt)

# Query 2 - Breakdown of crime per day of the week
print('\n')
st.sidebar.write('\n Crime Data According to Weekday:')

# user enters the day of the week from selection box
days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
crime_days = st.sidebar.selectbox("Please select a day of the week:", days)
df_BostonCrime = read_crimedata()
crimes = df_BostonCrime.loc[df_BostonCrime['DAY_OF_WEEK'].isin([crime_days])]
st.write(f"The number of crimes instances on {crime_days}'s was {len(crimes):,}.")

# data represented in bar chart
plt.clf()
for day in days:
    crime_count = df_BostonCrime.loc[df_BostonCrime['DAY_OF_WEEK'].isin([day])]
    plt.bar(day, len(crime_count))
plt.xlabel("Day of Week")
plt.ylabel("Crime Count")
plt.title("Crime Breakdown per Week")
st.pyplot(plt)

# pie chart with percentages of each particular day’s crime compared to total crime
plt.clf()
pie_crimes = []
crime_labels = []
for day in days:
    crime_count = df_BostonCrime.loc[df_BostonCrime['DAY_OF_WEEK'].isin([day])]
    pie_crimes.append(len(crime_count))
    crime_labels.append(day)
plt.pie(x=pie_crimes, labels=crime_labels, autopct='%1.1f%%')
st.pyplot(plt)

# Query 3 - Locations of the crimes
st.sidebar.write('\n Crime Locations:')

# user selects district, month, and day from single selection box
df_DistrictData = read_districtdata()
df_BostonCrime = read_crimedata()
select_district = st.sidebar.selectbox("Please select a district:", df_DistrictData.sort_values(['District']))
select_month = st.sidebar.selectbox("Please select a month:", [i for i in range(1, 13)])
select_day = st.sidebar.selectbox("Please select a day:", days)
filtered_data = filter_data(select_district, select_day, select_month)

# map populates showing where the crimes occurred according to that Offense Code
st.write('Look at the map of the crime locations!')

def generate_map(df_BostonCrime):
    BostonCrimeMap_df = df_BostonCrime.filter(['OFFENSE_CODE', 'Lat', 'Long'])

    view_state = pdk.ViewState(latitude=BostonCrimeMap_df["Lat"].mean(),
                               longitude=BostonCrimeMap_df["Long"].mean(),
                               zoom=10)
    layer = pdk.Layer('ScatterplotLayer',
                      data=BostonCrimeMap_df,
                      get_position='[Long, Lat]',
                      get_radius=50,
                      get_color=[250, 50, 100])
    tool_tip = {'html': 'listing:<br><b>{name}</b>', 'style': {'backgroundColor': 'black', 'color': 'white'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)
    st.pydeck_chart(map)
generate_map(filtered_data)
