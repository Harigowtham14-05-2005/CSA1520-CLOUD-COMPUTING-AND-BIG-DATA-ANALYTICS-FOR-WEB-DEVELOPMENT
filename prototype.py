import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime, timezone
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from io import BytesIO

# Function to get current weather data from OpenWeatherMap API
def get_weather(city_name, country_code, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name},{country_code}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(complete_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        main = data['main']
        wind = data['wind']
        weather = data['weather'][0]
        sys = data['sys']
        visibility = data.get('visibility', 'N/A') / 1000  # Convert to kilometers
        clouds = data['clouds']['all']
        
        # Determine weather condition for dynamic background
        condition = weather['main'].lower()
        update_background(condition)
        
        # Build the weather report string
        weather_report = (
            f"City: {city_name}, {sys['country']}\n"
            f"Temperature: {main['temp']}°C\n"
            f"Feels Like: {main['feels_like']}°C\n"
            f"Min Temperature: {main['temp_min']}°C\n"
            f"Max Temperature: {main['temp_max']}°C\n"
            f"Humidity: {main['humidity']}%\n"
            f"Pressure: {main['pressure']} hPa\n"
            f"Wind Speed: {wind['speed']} m/s\n"
            f"Wind Direction: {wind['deg']}°\n"
            f"Weather: {weather['main']} ({weather['description']})\n"
            f"Visibility: {visibility} km\n"
            f"Cloudiness: {clouds}%\n"
            f"Sunrise: {format_time_with_timezone(sys['sunrise'])}\n"
            f"Sunset: {format_time_with_timezone(sys['sunset'])}"
        )
        return weather_report, weather['icon']
        
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return "City Not Found.", None
        elif response.status_code == 401:
            return "Invalid API Key.", None
        else:
            return f"HTTP error occurred: {http_err}", None
    except Exception as err:
        return f"An error occurred: {err}", None

# Function to get 5-day forecast data from OpenWeatherMap API
def get_forecast(city_name, country_code, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    complete_url = f"{base_url}q={city_name},{country_code}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()
        
        # Extract temperature and time data for plotting
        temps = [entry['main']['temp'] for entry in data['list']]
        times = [entry['dt'] for entry in data['list']]
        
        # Convert Unix timestamps to formatted time strings
        formatted_times = [datetime.fromtimestamp(t, timezone.utc).strftime('%Y-%m-%d %H:%M') for t in times]
        
        return temps, formatted_times
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return [], []
    except Exception as err:
        print(f"An error occurred: {err}")
        return [], []

# Function to format the time from Unix format using timezone-aware datetime objects
def format_time_with_timezone(unix_time):
    # Convert the unix timestamp to a timezone-aware datetime object
    utc_time = datetime.fromtimestamp(unix_time, timezone.utc)
    # Format the time in the desired format
    return utc_time.strftime('%Y-%m-%d %H:%M:%S')

# Function to show the weather icon in the GUI
def show_icon(icon_code):
    try:
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_image = Image.open(requests.get(icon_url, stream=True).raw)
        icon_photo = ImageTk.PhotoImage(icon_image)
        icon_label.config(image=icon_photo)
        icon_label.image = icon_photo
    except Exception as e:
        print(f"Error loading icon: {e}")

# Function to update the background color based on weather condition
def update_background(condition):
    if 'clear' in condition:
        root.config(bg='#87CEEB')  # Clear sky - light blue
    elif 'cloud' in condition:
        root.config(bg='#B0C4DE')  # Cloudy - light steel blue
    elif 'rain' in condition or 'drizzle' in condition:
        root.config(bg='#778899')  # Rainy - light slate gray
    elif 'snow' in condition:
        root.config(bg='#F0F8FF')  # Snowy - Alice blue
    else:
        root.config(bg='#708090')  # Default - slate gray

# Function to clear the inputs
def clear_input():
    city_entry.delete(0, tk.END)
    country_entry.delete(0, tk.END)
    root.config(bg=default_bg)
    icon_label.config(image='')

# Function to show the weather report
def show_weather():
    city_name = city_entry.get()
    country_code = country_entry.get().upper()  # Convert to uppercase for standardization
    if city_name and country_code:
        weather_report, icon_code = get_weather(city_name, country_code, api_key)
        if icon_code:
            show_icon(icon_code)
        messagebox.showinfo("Weather Report", weather_report)
    else:
        messagebox.showwarning("Input Error", "Please enter both a city and country code.")

# Function to plot temperature data
def plot_temperature():
    city_name = city_entry.get()
    country_code = country_entry.get().upper()
    if city_name and country_code:
        temps, times = get_forecast(city_name, country_code, api_key)
        if temps and times:
            plt.figure(figsize=(10, 6))
            plt.plot(times, temps, marker='o', linestyle='-', color='b')
            plt.title(f"5-Day Temperature Forecast for {city_name}, {country_code}")
            plt.xlabel('Date and Time')
            plt.ylabel('Temperature (°C)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showerror("Error", "Could not retrieve forecast data.")
    else:
        messagebox.showwarning("Input Error", "Please enter both a city and country code.")

# API Key (replace 'your_api_key_here' with your actual API key)
api_key = "a2361ffa0c07dcf3b94f9d6197fd0213"

# Creating the main window
root = tk.Tk()
root.title("Weather Monitoring System")
root.geometry("400x550")

# Default background color
default_bg = '#F5F5F5'
root.config(bg=default_bg)

# Display current date and time
current_time_label = ttk.Label(root, text=f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", background=default_bg)
current_time_label.pack(pady=5)

# Label for the country entry box
country_label = ttk.Label(root, text="Enter Country Code (e.g., US for United States):", background=default_bg)
country_label.pack(pady=10)

# Entry box for country code
country_entry = ttk.Entry(root)
country_entry.pack(pady=10)

# Label for the city entry box
city_label = ttk.Label(root, text="Enter City Name:", background=default_bg)
city_label.pack(pady=10)

# Entry box for city name
city_entry = ttk.Entry(root)
city_entry.pack(pady=10)

# Button to fetch and display weather
weather_button = ttk.Button(root, text="Show Weather", command=show_weather)
weather_button.pack(pady=10)

# Label to display weather icon
icon_label = ttk.Label(root, background=default_bg)
icon_label.pack(pady=10)

# Button to plot temperature graph
plot_button = ttk.Button(root, text="Plot Temperature", command=plot_temperature)
plot_button.pack(pady=10)

# Button to clear the input
clear_button = ttk.Button(root, text="Clear", command=clear_input)
clear_button.pack(pady=10)

# Running the GUI application
root.mainloop()
