import streamlit as st
import requests


def get_coordinates(city):
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    response = requests.get(geocode_url)
    data = response.json()

    if "results" in data and data["results"]:
        result = data["results"][0]
        return result["latitude"], result["longitude"], result.get("country", "")
    else:
        return None, None, None


st.title("Weather App (Auto Coordinates)")

with st.form(key='weather_form'):
    city = st.text_input("Enter city name:", "Copenhagen")
    submit_button = st.form_submit_button("Get Weather")

if submit_button:
    lat, lon, country = get_coordinates(city)
    if lat and lon:
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
        weather_response = requests.get(weather_url).json()
        current = weather_response["current"]

        st.write(f"Location: {city}, {country}")
        st.metric("Temperature", f"{current['temperature_2m']}°C")
        st.metric("Wind Speed", f"{current['wind_speed_10m']} km/h")
    else:
        st.error("City not found. Please check the spelling.")
