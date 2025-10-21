import gradio as gr
import requests
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


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
    weather_codes = {
        0: "☀️ Clear sky", 1: "🌤️ Mainly clear", 2: "⛅ Partly cloudy", 3: "☁️ Overcast",
        45: "🌫️ Fog", 48: "🌫️ Depositing rime fog",
        51: "🌦️ Light drizzle", 53: "🌦️ Moderate drizzle", 55: "🌧️ Dense drizzle",
        56: "🌧️ Light freezing drizzle", 57: "🌧️ Dense freezing drizzle",
        61: "🌧️ Slight rain", 63: "🌧️ Moderate rain", 65: "🌧️ Heavy rain",
        66: "🌧️ Light freezing rain", 67: "🌧️ Heavy freezing rain",
        71: "🌨️ Slight snow", 73: "🌨️ Moderate snow", 75: "❄️ Heavy snow", 77: "🌨️ Snow grains",
        80: "🌦️ Slight rain showers", 81: "🌧️ Moderate rain showers", 82: "⛈️ Violent rain showers",
        85: "🌨️ Slight snow showers", 86: "❄️ Heavy snow showers",
        95: "⛈️ Thunderstorm", 96: "⛈️ Thunderstorm with slight hail", 99: "⛈️ Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown")


def get_wind_direction(degrees):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]


def get_weather(city):
    lat, lon, country = get_coordinates(city)
    
    if not lat or not lon:
        error_msg = "❌ City not found. Please check the spelling."
        return (error_msg, None, None, None, None, None, None, 
                "", "", "", "", "", "", "", "", "", 
                *[""] * 7, "", "")
    
    weather_url = f"""https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,uv_index_max&hourly=temperature_2m,precipitation_probability,wind_speed_10m&timezone=auto"""
    
    weather_response = requests.get(weather_url).json()
    current = weather_response["current"]
    daily = weather_response["daily"]
    hourly = weather_response["hourly"]
    
    location_header = f"# 📍 {city}, {country}\n\nCoordinates: {lat:.2f}°, {lon:.2f}°"
    
    # Create visualizations
    dates = [datetime.fromisoformat(d).strftime('%a %m/%d') for d in daily['time'][:7]]
    
    # Temperature Forecast Chart
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=dates, y=daily['temperature_2m_max'][:7],
        mode='lines+markers',
        name='High',
        line=dict(color='#ff7043', width=3),
        marker=dict(size=10)
    ))
    fig_temp.add_trace(go.Scatter(
        x=dates, y=daily['temperature_2m_min'][:7],
        mode='lines+markers',
        name='Low',
        line=dict(color='#42a5f5', width=3),
        marker=dict(size=10),
        fill='tonexty',
        fillcolor='rgba(100, 149, 237, 0.2)'
    ))
    fig_temp.update_layout(
        title='7-Day Temperature Forecast',
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        hovermode='x unified',
        height=400
    )
    
    # Precipitation Probability Chart
    fig_precip = go.Figure()
    fig_precip.add_trace(go.Bar(
        x=dates,
        y=daily['precipitation_probability_max'][:7],
        marker=dict(
            color=daily['precipitation_probability_max'][:7],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Probability %")
        ),
        text=[f"{p}%" for p in daily['precipitation_probability_max'][:7]],
        textposition='outside'
    ))
    fig_precip.update_layout(
        title='Rain Probability (7 Days)',
        xaxis_title='Date',
        yaxis_title='Probability (%)',
        height=400
    )
    
    # UV Index Chart
    fig_uv = go.Figure()
    colors = ['#4caf50' if uv <= 2 else '#ffeb3b' if uv <= 5 else '#ff9800' if uv <= 7 else '#f44336' 
             for uv in daily['uv_index_max'][:7]]
    fig_uv.add_trace(go.Bar(
        x=dates,
        y=daily['uv_index_max'][:7],
        marker=dict(color=colors),
        text=daily['uv_index_max'][:7],
        textposition='outside'
    ))
    fig_uv.update_layout(
        title='UV Index (7 Days)',
        xaxis_title='Date',
        yaxis_title='UV Index',
        height=400
    )
    
    # 24-Hour Hourly Forecast
    hourly_times = [datetime.fromisoformat(t).strftime('%H:%M') for t in hourly['time'][:24]]
    
    fig_hourly = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Temperature (Next 24 Hours)', 'Wind Speed (Next 24 Hours)'),
        vertical_spacing=0.15
    )
    
    fig_hourly.add_trace(go.Scatter(
        x=hourly_times,
        y=hourly['temperature_2m'][:24],
        mode='lines',
        name='Temperature',
        line=dict(color='#ff6b6b', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 107, 0.2)'
    ), row=1, col=1)
    
    fig_hourly.add_trace(go.Scatter(
        x=hourly_times,
        y=hourly['wind_speed_10m'][:24],
        mode='lines',
        name='Wind Speed',
        line=dict(color='#4ecdc4', width=2),
        fill='tozeroy',
        fillcolor='rgba(78, 205, 196, 0.2)'
    ), row=2, col=1)
    
    fig_hourly.update_xaxes(title_text="Time", row=2, col=1)
    fig_hourly.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig_hourly.update_yaxes(title_text="Wind Speed (km/h)", row=2, col=1)
    fig_hourly.update_layout(height=600, showlegend=False)
    
    # Wind Rose
    fig_wind = go.Figure()
    fig_wind.add_trace(go.Barpolar(
        r=[current['wind_speed_10m']],
        theta=[current['wind_direction_10m']],
        marker=dict(color='#00bcd4', line=dict(color='#006064', width=2)),
        width=[20],
        name='Wind'
    ))
    fig_wind.update_layout(
        title='Current Wind Direction & Speed',
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(current['wind_speed_10m'] * 1.5, 20)]),
            angularaxis=dict(direction='clockwise', rotation=90)
        ),
        height=400
    )
    
    # Current weather data
    temp = f"{current['temperature_2m']}°C"
    feels_like = f"{current['apparent_temperature']}°C"
    humidity = f"{current['relative_humidity_2m']}%"
    cloud_cover = f"{current['cloud_cover']}%"
    
    wind_dir = get_wind_direction(current['wind_direction_10m'])
    wind_speed = f"{current['wind_speed_10m']} km/h"
    wind_direction = f"{wind_dir} ({current['wind_direction_10m']}°)"
    wind_gusts = f"{current['wind_gusts_10m']} km/h"
    pressure = f"{current['pressure_msl']} hPa"
    
    condition = f"**Condition:** {get_weather_description(current['weather_code'])}"
    
    precipitation_info = ""
    if current['precipitation'] > 0:
        precipitation_info = f"💧 **Precipitation:** {current['precipitation']} mm | **Rain:** {current['rain']} mm"
    
    # 7-day forecast
    forecast_days = []
    for i in range(7):
        date = datetime.fromisoformat(daily['time'][i])
        day_text = f"**{date.strftime('%a %m/%d')}**\n\n"
        day_text += f"High: **{daily['temperature_2m_max'][i]}°C**\n\n"
        day_text += f"Low: **{daily['temperature_2m_min'][i]}°C**\n\n"
        
        if daily['precipitation_probability_max'][i]:
            day_text += f"💧 {daily['precipitation_probability_max'][i]}%\n\n"
        if daily['precipitation_sum'][i] > 0:
            day_text += f"🌧️ {daily['precipitation_sum'][i]} mm\n\n"
        
        day_text += f"☀️ UV: {daily['uv_index_max'][i]}"
        forecast_days.append(day_text)
    
    sunrise = datetime.fromisoformat(daily['sunrise'][0])
    sunset = datetime.fromisoformat(daily['sunset'][0])
    sunrise_time = sunrise.strftime('%H:%M')
    sunset_time = sunset.strftime('%H:%M')
    
    return (location_header, fig_temp, fig_precip, fig_uv, fig_hourly, fig_wind, None,
            temp, feels_like, humidity, cloud_cover, 
            wind_speed, wind_direction, wind_gusts, pressure, condition, 
            precipitation_info, *forecast_days, sunrise_time, sunset_time)


with gr.Blocks(title="🌤️ Comprehensive Weather App", css=".primary-btn {background-color: #ec4899 !important;}") as demo:
    
    gr.Markdown("# 🌤️ Comprehensive Weather App")
    
    with gr.Row():
        city_input = gr.Textbox(
            label="Enter city name:",
            value="Copenhagen",
            placeholder="Enter city name"
        )
    
    submit_btn = gr.Button("Get Weather", variant="primary", elem_classes="primary-btn")
    
    location_output = gr.Markdown()
    
    gr.Markdown("## 📊 Weather Visualizations")
    
    temp_chart = gr.Plot()
    
    with gr.Row():
        precip_chart = gr.Plot()
        uv_chart = gr.Plot()
    
    hourly_chart = gr.Plot()
    wind_chart = gr.Plot()
    
    gr.Markdown("---")
    
    gr.Markdown("## 🌡️ Current Weather")
    
    with gr.Row():
        with gr.Column(min_width=200):
            temp_output = gr.Textbox(label="Temperature", interactive=False)
            feels_like_output = gr.Textbox(label="Feels Like", interactive=False)
        
        with gr.Column(min_width=200):
            humidity_output = gr.Textbox(label="Humidity", interactive=False)
            cloud_output = gr.Textbox(label="Cloud Cover", interactive=False)
        
        with gr.Column(min_width=200):
            wind_speed_output = gr.Textbox(label="Wind Speed", interactive=False)
            wind_dir_output = gr.Textbox(label="Wind Direction", interactive=False)
        
        with gr.Column(min_width=200):
            wind_gusts_output = gr.Textbox(label="Wind Gusts", interactive=False)
            pressure_output = gr.Textbox(label="Pressure", interactive=False)
    
    condition_output = gr.Markdown()
    precipitation_output = gr.Markdown()
    
    gr.Markdown("---")
    
    gr.Markdown("## 📅 7-Day Forecast")
    
    with gr.Row():
        day1_output = gr.Markdown()
        day2_output = gr.Markdown()
        day3_output = gr.Markdown()
        day4_output = gr.Markdown()
        day5_output = gr.Markdown()
        day6_output = gr.Markdown()
        day7_output = gr.Markdown()
    
    gr.Markdown("---")
    
    gr.Markdown("## 🌅 Sun Times (Today)")
    
    with gr.Row():
        with gr.Column():
            sunrise_output = gr.Textbox(label="🌅 Sunrise", interactive=False)
        
        with gr.Column():
            sunset_output = gr.Textbox(label="🌇 Sunset", interactive=False)
    
    submit_btn.click(
        fn=get_weather,
        inputs=city_input,
        outputs=[
            location_output,
            temp_chart,
            precip_chart,
            uv_chart,
            hourly_chart,
            wind_chart,
            gr.Textbox(visible=False),
            temp_output,
            feels_like_output,
            humidity_output,
            cloud_output,
            wind_speed_output,
            wind_dir_output,
            wind_gusts_output,
            pressure_output,
            condition_output,
            precipitation_output,
            day1_output,
            day2_output,
            day3_output,
            day4_output,
            day5_output,
            day6_output,
            day7_output,
            sunrise_output,
            sunset_output
        ]
    )
    
    city_input.submit(
        fn=get_weather,
        inputs=city_input,
        outputs=[
            location_output,
            temp_chart,
            precip_chart,
            uv_chart,
            hourly_chart,
            wind_chart,
            gr.Textbox(visible=False),
            temp_output,
            feels_like_output,
            humidity_output,
            cloud_output,
            wind_speed_output,
            wind_dir_output,
            wind_gusts_output,
            pressure_output,
            condition_output,
            precipitation_output,
            day1_output,
            day2_output,
            day3_output,
            day4_output,
            day5_output,
            day6_output,
            day7_output,
            sunrise_output,
            sunset_output
        ]
    )

if __name__ == "__main__":
    demo.launch()
