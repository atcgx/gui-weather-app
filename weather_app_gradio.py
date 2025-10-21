import gradio as gr
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


def get_weather(city):
    lat, lon, country = get_coordinates(city)
    
    if lat and lon:
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
        weather_response = requests.get(weather_url).json()
        current = weather_response["current"]
        
        location = f"Location: {city}, {country}"
        temperature = f"{current['temperature_2m']}°C"
        wind_speed = f"{current['wind_speed_10m']} km/h"
        
        return location, temperature, wind_speed
    else:
        return "City not found. Please check the spelling.", "", ""


with gr.Blocks(title="Weather App (Auto Coordinates)") as demo:
    gr.Markdown("# Weather App (Auto Coordinates)")
    
    with gr.Row():
        city_input = gr.Textbox(
            label="Enter city name:",
            value="Copenhagen",
            placeholder="Enter city name"
        )
    
    submit_btn = gr.Button("Get Weather", variant="primary")
    
    location_output = gr.Textbox(label="Location", interactive=False)
    temperature_output = gr.Textbox(label="Temperature", interactive=False)
    wind_output = gr.Textbox(label="Wind Speed", interactive=False)
    
    submit_btn.click(
        fn=get_weather,
        inputs=city_input,
        outputs=[location_output, temperature_output, wind_output]
    )
    
    city_input.submit(
        fn=get_weather,
        inputs=city_input,
        outputs=[location_output, temperature_output, wind_output]
    )

if __name__ == "__main__":
    demo.launch()
