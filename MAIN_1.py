import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime
import threading
import csv # Added for CSV operations

class ModernWeatherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.setup_ui()
        
        # Variables
        self.weather_icon_photo = None # To hold the PhotoImage object
        self.api_key = "38580d3697cf0d37b4745f1a4f297fb0" # Your OpenWeatherMap API Key
        self.csv_file_path = r"D:\My Files\weather_data.csv" # Path for the CSV file
        
    def setup_window(self):
        """Setup main window"""
        self.root.title("🌤️ Modern Weather Dashboard")
        self.root.geometry("500x700")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f'500x700+{x}+{y}')
        
    def setup_styles(self):
        """Setup modern styles"""
        self.colors = {
            'primary': '#16213e',
            'secondary': '#0f3460',
            'accent': '#e94560',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0',
            'success': '#4caf50',
            'error': '#f44336',
            'warning': '#ff9800'
        }
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure treeview
        style.configure("Custom.Treeview", 
                       background='#16213e',
                       foreground='white',
                       fieldbackground='#16213e',
                       borderwidth=0,
                       relief='flat')
        
        style.configure("Custom.Treeview.Heading",
                       background='#0f3460',
                       foreground='white',
                       borderwidth=1,
                       relief='flat')
        
        style.map("Custom.Treeview",
                 background=[('selected', '#e94560')])
        
        # Configure scrollbar
        style.configure("TScrollbar",
                        troughcolor=self.colors['primary'],
                        background=self.colors['secondary'],
                        bordercolor=self.colors['secondary'],
                        arrowcolor=self.colors['text'])
        style.map("TScrollbar",
                  background=[('active', self.colors['accent'])])

    def create_modern_frame(self, parent, bg_color, relief='flat', bd=0):
        """Create modern looking frame"""
        frame = tk.Frame(parent, bg=bg_color, relief=relief, bd=bd)
        return frame
        
    def create_modern_button(self, parent, text, command, bg_color='#e94560', 
                           fg_color='white', font_size=12, width=15):
        """Create modern button with hover effect"""
        button = tk.Button(
            parent, 
            text=text, 
            command=command,
            bg=bg_color,
            fg=fg_color,
            font=('Arial', font_size, 'bold'),
            relief='flat',
            bd=0,
            width=width,
            cursor='hand2'
        )
        
        # Hover effects
        def on_enter(e):
            button.config(bg=self.lighten_color(bg_color))
            
        def on_leave(e):
            button.config(bg=bg_color)
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
        
    def lighten_color(self, color):
        """Lighten a color for hover effect"""
        color_map = {
            '#e94560': '#ff5577',
            '#4caf50': '#66bb6a',
            '#f44336': '#ff5544'
        }
        return color_map.get(color, color)
        
    def setup_ui(self):
        """Setup user interface"""
        # Main container
        main_frame = self.create_modern_frame(self.root, '#1a1a2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🌍 Weather Dashboard",
            bg='#1a1a2e',
            fg='#ffffff',
            font=('Arial', 24, 'bold')
        )
        title_label.pack(pady=(0, 30))
        
        # Search frame
        search_frame = self.create_modern_frame(main_frame, '#16213e')
        search_frame.pack(fill='x', pady=(0, 20))
        
        # City input
        input_frame = self.create_modern_frame(search_frame, '#16213e')
        input_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(input_frame, text="City:", bg='#16213e', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.city_entry = tk.Entry(
            input_frame,
            font=('Arial', 14),
            bg='#0f3460',
            fg='#ffffff',
            relief='flat',
            bd=10,
            insertbackground='#ffffff'
        )
        self.city_entry.pack(fill='x', pady=(0, 10))
        self.city_entry.bind('<Return>', lambda e: self.get_weather_threaded())
        
        # Search button
        self.search_btn = self.create_modern_button(
            input_frame, 
            "🔍 Get Weather", 
            self.get_weather_threaded,
            width=20
        )
        self.search_btn.pack(pady=(0, 10))
        
        # Status label
        self.status_label = tk.Label(
            input_frame,
            text="Enter a city name to get weather information",
            bg='#16213e',
            fg='#a0a0a0',
            font=('Arial', 10)
        )
        self.status_label.pack()
        
        # Weather display frame
        weather_frame = self.create_modern_frame(main_frame, '#16213e')
        weather_frame.pack(fill='both', expand=True)
        
        # Weather icon
        self.icon_label = tk.Label(
            weather_frame,
            text="🌤️", # Default emoji
            bg='#16213e',
            fg='#ffffff',
            font=('Arial', 48)
        )
        self.icon_label.pack(pady=(20, 10))
        
        # Weather data treeview
        tree_frame = self.create_modern_frame(weather_frame, '#16213e')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, style="TScrollbar")
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        self.treeview = ttk.Treeview(
            tree_frame,
            columns=("Label", "Value"),
            show="headings",
            height=10,
            style="Custom.Treeview",
            yscrollcommand=scrollbar.set
        )
        
        scrollbar.config(command=self.treeview.yview)
        
        self.treeview.heading("Label", text="📊 Data")
        self.treeview.heading("Value", text="📈 Value")
        
        self.treeview.column("Label", width=180, anchor="w")
        self.treeview.column("Value", width=200, anchor="center")
        
        self.treeview.pack(fill='both', expand=True)

    def get_weather_threaded(self):
        """Starts weather fetching in a separate thread to keep UI responsive."""
        city = self.city_entry.get()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        self.status_label.config(text="Fetching weather...", fg=self.colors['warning'])
        self.search_btn.config(state=tk.DISABLED) # Disable button while loading
        
        # Clear previous data
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        self.icon_label.config(image='', text='🌤️') # Reset icon/emoji

        threading.Thread(target=self._fetch_weather_data, args=(city,)).start()

    def _fetch_weather_data(self, city):
        """Fetches weather data from API."""
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            data = response.json()
            
            # Update UI on the main thread
            self.root.after(0, self._update_weather_ui, data)

        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err} - City not found or API issue."
            self.root.after(0, self._show_error, error_message)
        except requests.exceptions.ConnectionError as conn_err:
            error_message = f"Connection error occurred: {conn_err} - Check your internet connection."
            self.root.after(0, self._show_error, error_message)
        except requests.exceptions.Timeout as timeout_err:
            error_message = f"Timeout error occurred: {timeout_err} - Request timed out."
            self.root.after(0, self._show_error, error_message)
        except requests.exceptions.RequestException as req_err:
            error_message = f"An error occurred: {req_err}"
            self.root.after(0, self._show_error, error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            self.root.after(0, self._show_error, error_message)
        finally:
            self.root.after(0, lambda: self.search_btn.config(state=tk.NORMAL)) # Re-enable button

    def _update_weather_ui(self, data):
        """Updates the UI with fetched weather data and saves to CSV."""
        self.status_label.config(text="Weather data updated!", fg=self.colors['success'])
        
        # Clear existing data in treeview
        for i in self.treeview.get_children():
            self.treeview.delete(i)

        # Basic weather info
        city_name = data['name']
        country = data['sys']['country']
        location = f"{city_name}, {country}"
        temperature = round(data['main']['temp'])
        feels_like = round(data['main']['feels_like'])
        description = data['weather'][0]['description'].capitalize()
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        pressure = data['main']['pressure']
        wind_deg = data['wind'].get('deg', 'N/A') # Get wind direction, default to N/A if not present
        
        sunrise_time = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
        sunset_time = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')

        # Insert data into treeview
        self.treeview.insert("", "end", values=("Location", location))
        self.treeview.insert("", "end", values=("Temperature", f"{temperature}°C"))
        self.treeview.insert("", "end", values=("Feels Like", f"{feels_like}°C"))
        self.treeview.insert("", "end", values=("Description", description))
        self.treeview.insert("", "end", values=("Humidity", f"{humidity}%"))
        self.treeview.insert("", "end", values=("Wind Speed", f"{wind_speed} m/s"))
        self.treeview.insert("", "end", values=("Pressure", f"{pressure} hPa"))
        self.treeview.insert("", "end", values=("Wind Direction", f"{wind_deg}°")) # Added wind direction to UI
        self.treeview.insert("", "end", values=("Sunrise", sunrise_time))
        self.treeview.insert("", "end", values=("Sunset", sunset_time))

        # Update weather icon/emoji
        icon_code = data['weather'][0]['icon']
        self.update_weather_icon(icon_code)

        # Save data to CSV
        self._save_to_csv(
            city_name,
            temperature,
            feels_like,
            humidity,
            pressure,
            description,
            wind_speed,
            wind_deg
        )

    def update_weather_icon(self, icon_code):
        """Updates the weather icon based on OpenWeatherMap icon code."""
        emoji_map = {
            '01d': '☀️', '01n': '🌙', # Clear sky
            '02d': '🌤️', '02n': '☁️', # Few clouds
            '03d': '☁️', '03n': '☁️', # Scattered clouds
            '04d': '☁️', '04n': '☁️', # Broken clouds
            '09d': '🌧️', '09n': '🌧️', # Shower rain
            '10d': '🌦️', '10n': '🌧️', # Rain
            '11d': '⛈️', '11n': '⛈️', # Thunderstorm
            '13d': '❄️', '13n': '❄️', # Snow
            '50d': '🌫️', '50n': '🌫️', # Mist/Fog
        }
        
        # Fetch actual images (requires Pillow):
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        try:
            response = requests.get(icon_url)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((100, 100), Image.LANCZOS)
            self.weather_icon_photo = ImageTk.PhotoImage(img)
            self.icon_label.config(image=self.weather_icon_photo, text='')
        except Exception as e:
            print(f"Error loading icon: {e}")
            self.icon_label.config(text=emoji_map.get(icon_code, '❓'), image='')

    def _save_to_csv(self, city_name, temperature, feels_like, humidity, pressure, weather_description, wind_speed, wind_deg):
        """
        Saves weather data to a CSV file.
        Checks if the city already exists in the CSV to avoid duplicates.
        """
        try:
            existing_cities = set()

            # Read existing cities from the CSV file
            try:
                with open(self.csv_file_path, mode="r", newline="", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    next(reader, None)  # Skip header row
                    for row in reader:
                        if row: # Ensure row is not empty
                            existing_cities.add(row[0])  # First column is city name
            except FileNotFoundError:
                pass  # File doesn't exist yet, it will be created

            # Check if the city is already recorded
            if city_name in existing_cities:
                print(f"{city_name} is already recorded in CSV. Skipping save.")
                return

            # If not existing, append the new data
            with open(self.csv_file_path, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                # Write header only if the file is new/empty
                if file.tell() == 0:
                    writer.writerow(["City", "Temperature", "Feels Like", "Humidity", "Pressure", "Weather", "Wind Speed", "Wind Direction"])
                writer.writerow([
                    city_name,
                    f"{temperature}°C",
                    f"{feels_like}°C",
                    f"{humidity}%",
                    f"{pressure} hPa",
                    weather_description,
                    f"{wind_speed} m/s",
                    f"{wind_deg}°",
                ])
            print(f"Successfully saved weather data for: {city_name} to CSV.")
        except Exception as e:
            print("Error saving CSV:", e)
            # You might want to show a messagebox here for the user
            # messagebox.showerror("CSV Save Error", f"Failed to save data to CSV: {e}")


    def _show_error(self, message):
        """Displays an error message to the user."""
        self.status_label.config(text=message, fg=self.colors['error'])
        messagebox.showerror("Weather Error", message)

    def run(self):
        """Starts the Tkinter event loop."""
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernWeatherApp()
    app.run()
