from dash import Dash, html, dcc, Input, Output, State

app = Dash(__name__)
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

app.layout = html.Div([
    html.H1("Weather App (Auto Coordinates)"),
    
    dcc.Input(
        id='city-input',
        type='text',
        value='Copenhagen',
        placeholder='Enter city name:',
        style={'marginRight': '10px', 'padding': '5px'}
    ),
    
    html.Button('Get Weather', id='weather-button', n_clicks=0),
    
    html.Div(id='weather-output', style={'marginTop': '20px'})
])

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
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
        weather_response = requests.get(weather_url).json()
        current = weather_response["current"]
        
        return html.Div([
            html.P(f"Location: {city}, {country}", style={'fontSize': '18px'}),
            html.Div([
                html.Strong("Temperature: "),
                html.Span(f"{current['temperature_2m']}°C", style={'fontSize': '24px', 'color': '#1f77b4'})
            ], style={'margin': '10px 0'}),
            html.Div([
                html.Strong("Wind Speed: "),
                html.Span(f"{current['wind_speed_10m']} km/h", style={'fontSize': '24px', 'color': '#ff7f0e'})
            ], style={'margin': '10px 0'})
        ])
    else:
        return html.Div("City not found. Please check the spelling.", 
                       style={'color': 'red', 'fontSize': '16px'})

if __name__ == '__main__':
    app.run(debug=True)
