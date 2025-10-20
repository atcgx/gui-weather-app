import streamlit as st
import requests
from datetime import datetime


def get_coordinates(city):
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    response = requests.get(geocode_url)
    data = response.json()

    if "results" in data and data["results"]:
        result = data["results"][0]
        return result["latitude"], result["longitude"], result.get("country", "")
    else:
        return None, None, None


def get_weather_description(code):
    """Convert WMO weather code to description"""
    weather_codes = {
        0: "☀️ Clear sky",
        1: "🌤️ Mainly clear",
        2: "⛅ Partly cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Fog",
        48: "🌫️ Depositing rime fog",
        51: "🌦️ Light drizzle",
        53: "🌦️ Moderate drizzle",
        55: "🌧️ Dense drizzle",
        56: "🌧️ Light freezing drizzle",
        57: "🌧️ Dense freezing drizzle",
        61: "🌧️ Slight rain",
        63: "🌧️ Moderate rain",
        65: "🌧️ Heavy rain",
        66: "🌧️ Light freezing rain",
        67: "🌧️ Heavy freezing rain",
        71: "🌨️ Slight snow",
        73: "🌨️ Moderate snow",
        75: "❄️ Heavy snow",
        77: "🌨️ Snow grains",
        80: "🌦️ Slight rain showers",
        81: "🌧️ Moderate rain showers",
        82: "⛈️ Violent rain showers",
        85: "🌨️ Slight snow showers",
        86: "❄️ Heavy snow showers",
        95: "⛈️ Thunderstorm",
        96: "⛈️ Thunderstorm with slight hail",
        99: "⛈️ Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown")


def get_wind_direction(degrees):
    """Convert wind direction degrees to compass direction"""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]


st.set_page_config(page_title="Weather App", page_icon="🌤️", layout="wide")
st.title("🌤️ Comprehensive Weather App")

with st.form(key='weather_form'):
    city = st.text_input("Enter city name:", "Copenhagen")
    submit_button = st.form_submit_button("Get Weather")

if submit_button:
    lat, lon, country = get_coordinates(city)
    
    if lat and lon:
        weather_url = f"""https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,uv_index_max&timezone=auto"""
        
        weather_response = requests.get(weather_url).json()
        current = weather_response["current"]
        daily = weather_response["daily"]
        
        # Header with location
        st.header(f"📍 {city}, {country}")
        st.caption(f"Coordinates: {lat:.2f}°, {lon:.2f}°")
        
        # Current Weather Section
        st.subheader("🌡️ Current Weather")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Temperature", f"{current['temperature_2m']}°C")
            st.metric("Feels Like", f"{current['apparent_temperature']}°C")
        
        with col2:
            st.metric("Humidity", f"{current['relative_humidity_2m']}%")
            st.metric("Cloud Cover", f"{current['cloud_cover']}%")
        
        with col3:
            wind_dir = get_wind_direction(current['wind_direction_10m'])
            st.metric("Wind Speed", f"{current['wind_speed_10m']} km/h")
            st.metric("Wind Direction", f"{wind_dir} ({current['wind_direction_10m']}°)")
        
        with col4:
            st.metric("Wind Gusts", f"{current['wind_gusts_10m']} km/h")
            st.metric("Pressure", f"{current['pressure_msl']} hPa")
        
        # Weather Condition
        st.info(f"**Condition:** {get_weather_description(current['weather_code'])}")
        
        # Precipitation
        if current['precipitation'] > 0:
            st.warning(f"💧 **Precipitation:** {current['precipitation']} mm | **Rain:** {current['rain']} mm")
        
        st.divider()
        
        # 7-Day Forecast
        st.subheader("📅 7-Day Forecast")
        
        forecast_cols = st.columns(7)
        
        for i in range(7):
            with forecast_cols[i]:
                date = datetime.fromisoformat(daily['time'][i])
                st.markdown(f"**{date.strftime('%a %m/%d')}**")
                st.metric("High", f"{daily['temperature_2m_max'][i]}°C")
                st.metric("Low", f"{daily['temperature_2m_min'][i]}°C")
                
                if daily['precipitation_probability_max'][i]:
                    st.caption(f"💧 {daily['precipitation_probability_max'][i]}%")
                if daily['precipitation_sum'][i] > 0:
                    st.caption(f"🌧️ {daily['precipitation_sum'][i]} mm")
                
                st.caption(f"☀️ UV: {daily['uv_index_max'][i]}")
        
        st.divider()
        
        # Sun Times for Today
        st.subheader("🌅 Sun Times (Today)")
        sun_col1, sun_col2 = st.columns(2)
        
        with sun_col1:
            sunrise = datetime.fromisoformat(daily['sunrise'][0])
            st.metric("🌅 Sunrise", sunrise.strftime('%H:%M'))
        
        with sun_col2:
            sunset = datetime.fromisoformat(daily['sunset'][0])
            st.metric("🌇 Sunset", sunset.strftime('%H:%M'))
            
    else:
        st.error("❌ City not found. Please check the spelling.")
