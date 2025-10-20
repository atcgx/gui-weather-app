from dash import Dash, html, dcc, Input, Output, State
import requests
from datetime import datetime

app = Dash(__name__)

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
    """Convert wind direction degrees to compass direction"""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]

app.layout = html.Div([
    html.H1("🌤️ Comprehensive Weather App", style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    html.Div([
        dcc.Input(
            id='city-input',
            type='text',
            value='Copenhagen',
            placeholder='Enter city name:',
            style={'padding': '10px', 'fontSize': '16px', 'width': '300px', 'marginRight': '10px'}
        ),
        html.Button('Get Weather', id='weather-button', n_clicks=0, 
                   style={'padding': '10px 20px', 'fontSize': '16px', 'cursor': 'pointer'})
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    html.Div(id='weather-output', style={'padding': '20px', 'maxWidth': '1400px', 'margin': '0 auto'})
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'})

@app.callback(
    Output('weather-output', 'children'),
    Input('weather-button', 'n_clicks'),
    Input('city-input', 'n_submit'),
    State('city-input', 'value')
)
def update_weather(n_clicks, n_submit, city):
    if n_clicks == 0 and n_submit is None:
        return ""
    
    lat, lon, country = get_coordinates(city)
    
    if lat and lon:
        weather_url = f"""https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,uv_index_max&timezone=auto"""
        
        weather_response = requests.get(weather_url).json()
        current = weather_response["current"]
        daily = weather_response["daily"]
        
        # Header
        header = html.Div([
            html.H2(f"📍 {city}, {country}", style={'marginBottom': '5px'}),
            html.P(f"Coordinates: {lat:.2f}°, {lon:.2f}°", style={'color': '#666', 'fontSize': '14px'})
        ])
        
        # Current Weather Section
        current_weather = html.Div([
            html.H3("🌡️ Current Weather", style={'marginTop': '30px', 'marginBottom': '20px'}),
            
            # 4 column grid for current weather
            html.Div([
                # Column 1
                html.Div([
                    html.Div([
                        html.Strong("Temperature"),
                        html.Div(f"{current['temperature_2m']}°C", 
                                style={'fontSize': '32px', 'color': '#1f77b4', 'fontWeight': 'bold'})
                    ], style={'marginBottom': '20px'}),
                    html.Div([
                        html.Strong("Feels Like"),
                        html.Div(f"{current['apparent_temperature']}°C", 
                                style={'fontSize': '24px', 'color': '#666'})
                    ])
                ], style={'flex': '1', 'padding': '10px'}),
                
                # Column 2
                html.Div([
                    html.Div([
                        html.Strong("Humidity"),
                        html.Div(f"{current['relative_humidity_2m']}%", 
                                style={'fontSize': '32px', 'color': '#2ca02c', 'fontWeight': 'bold'})
                    ], style={'marginBottom': '20px'}),
                    html.Div([
                        html.Strong("Cloud Cover"),
                        html.Div(f"{current['cloud_cover']}%", 
                                style={'fontSize': '24px', 'color': '#666'})
                    ])
                ], style={'flex': '1', 'padding': '10px'}),
                
                # Column 3
                html.Div([
                    html.Div([
                        html.Strong("Wind Speed"),
                        html.Div(f"{current['wind_speed_10m']} km/h", 
                                style={'fontSize': '32px', 'color': '#ff7f0e', 'fontWeight': 'bold'})
                    ], style={'marginBottom': '20px'}),
                    html.Div([
                        html.Strong("Wind Direction"),
                        html.Div(f"{get_wind_direction(current['wind_direction_10m'])} ({current['wind_direction_10m']}°)", 
                                style={'fontSize': '24px', 'color': '#666'})
                    ])
                ], style={'flex': '1', 'padding': '10px'}),
                
                # Column 4
                html.Div([
                    html.Div([
                        html.Strong("Wind Gusts"),
                        html.Div(f"{current['wind_gusts_10m']} km/h", 
                                style={'fontSize': '32px', 'color': '#d62728', 'fontWeight': 'bold'})
                    ], style={'marginBottom': '20px'}),
                    html.Div([
                        html.Strong("Pressure"),
                        html.Div(f"{current['pressure_msl']} hPa", 
                                style={'fontSize': '24px', 'color': '#666'})
                    ])
                ], style={'flex': '1', 'padding': '10px'})
            ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),
            
            # Weather condition
            html.Div(
                f"Condition: {get_weather_description(current['weather_code'])}",
                style={'padding': '15px', 'backgroundColor': '#e3f2fd', 'borderRadius': '5px', 
                       'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '10px'}
            ),
            
            # Precipitation warning if any
            html.Div(
                f"💧 Precipitation: {current['precipitation']} mm | Rain: {current['rain']} mm",
                style={'padding': '15px', 'backgroundColor': '#fff3cd', 'borderRadius': '5px', 
                       'fontSize': '16px', 'marginBottom': '20px'} if current['precipitation'] > 0 else {'display': 'none'}
            )
        ])
        
        # 7-Day Forecast
        forecast_days = []
        for i in range(7):
            date = datetime.fromisoformat(daily['time'][i])
            day_card = html.Div([
                html.Strong(date.strftime('%a %m/%d'), style={'fontSize': '16px', 'marginBottom': '10px', 'display': 'block'}),
                html.Div([
                    html.Div("High", style={'fontSize': '12px', 'color': '#666'}),
                    html.Div(f"{daily['temperature_2m_max'][i]}°C", 
                            style={'fontSize': '24px', 'color': '#d62728', 'fontWeight': 'bold'})
                ], style={'marginBottom': '10px'}),
                html.Div([
                    html.Div("Low", style={'fontSize': '12px', 'color': '#666'}),
                    html.Div(f"{daily['temperature_2m_min'][i]}°C", 
                            style={'fontSize': '24px', 'color': '#1f77b4', 'fontWeight': 'bold'})
                ], style={'marginBottom': '10px'}),
                html.Div(f"💧 {daily['precipitation_probability_max'][i]}%" if daily['precipitation_probability_max'][i] else "", 
                        style={'fontSize': '12px', 'marginBottom': '5px'}),
                html.Div(f"🌧️ {daily['precipitation_sum'][i]} mm" if daily['precipitation_sum'][i] > 0 else "", 
                        style={'fontSize': '12px', 'marginBottom': '5px'}),
                html.Div(f"☀️ UV: {daily['uv_index_max'][i]}", 
                        style={'fontSize': '12px', 'color': '#666'})
            ], style={'flex': '1', 'padding': '15px', 'border': '1px solid #ddd', 
                     'borderRadius': '5px', 'backgroundColor': '#f9f9f9', 'minWidth': '120px'})
            forecast_days.append(day_card)
        
        forecast_section = html.Div([
            html.Hr(style={'margin': '30px 0'}),
            html.H3("📅 7-Day Forecast", style={'marginBottom': '20px'}),
            html.Div(forecast_days, style={'display': 'flex', 'gap': '15px', 'overflowX': 'auto'})
        ])
        
        # Sun Times
        sunrise = datetime.fromisoformat(daily['sunrise'][0])
        sunset = datetime.fromisoformat(daily['sunset'][0])
        
        sun_times = html.Div([
            html.Hr(style={'margin': '30px 0'}),
            html.H3("🌅 Sun Times (Today)", style={'marginBottom': '20px'}),
            html.Div([
                html.Div([
                    html.Strong("🌅 Sunrise"),
                    html.Div(sunrise.strftime('%H:%M'), 
                            style={'fontSize': '32px', 'color': '#ff9800', 'fontWeight': 'bold'})
                ], style={'flex': '1', 'padding': '20px', 'border': '1px solid #ddd', 
                         'borderRadius': '5px', 'backgroundColor': '#fff8e1'}),
                html.Div([
                    html.Strong("🌇 Sunset"),
                    html.Div(sunset.strftime('%H:%M'), 
                            style={'fontSize': '32px', 'color': '#e91e63', 'fontWeight': 'bold'})
                ], style={'flex': '1', 'padding': '20px', 'border': '1px solid #ddd', 
                         'borderRadius': '5px', 'backgroundColor': '#fce4ec'})
            ], style={'display': 'flex', 'gap': '20px'})
        ])
        
        return html.Div([header, current_weather, forecast_section, sun_times])
    else:
        return html.Div("❌ City not found. Please check the spelling.", 
                       style={'color': 'red', 'fontSize': '18px', 'textAlign': 'center', 
                              'padding': '20px', 'backgroundColor': '#ffebee', 'borderRadius': '5px'})

if __name__ == '__main__':
    app.run(debug=True)
