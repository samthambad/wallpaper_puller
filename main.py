import requests
import os
from PIL import Image, ImageTk
import ctypes
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from io import BytesIO
import customtkinter

# Function to fetch wallpapers from Wallhaven
def fetch_wallpapers(query, image_frame):
    wallhaven_api_url = "https://wallhaven.cc/api/v1/search"
    api_key = os.getenv("API_KEY")
    print("query:", query) 
    params = {
        "apikey": api_key,
        "q": query,  # Search query, change it to your preferred search term
        "purity": "100",  # Safe for work (SFW) content
        "categories": "111",  # All categories
        "sorting": "random",
        "order": "desc",
        "page": 1
    }
    
    response = requests.get(wallhaven_api_url, params=params)
    response.raise_for_status()
    response = response.json()["data"]
    display_wallpapers(response, image_frame)
    

# Function to set the wallpaper
def set_wallpaper(path):
    # This works for Windows
    ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

# Function to download and set the wallpaper
def download_and_set_wallpaper(wallpaper_url):
    wallpaper_path = os.path.join(os.path.expanduser("~"), "Pictures", "wallhaven_wallpaper.jpg")
    
    response = requests.get(wallpaper_url)
    response.raise_for_status()
    
    with open(wallpaper_path, "wb") as file:
        file.write(response.content)
    
    set_wallpaper(wallpaper_path)
    messagebox.showinfo("Success", "Wallpaper set successfully!")

# Function to create the GUI
def create_gui_new():
    root = ctk.CTk()
    ctk.set_appearance_mode("System")
    root.geometry("1280x720")
    root.title("Wallpaper puller")
    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)
    query = ctk.CTkEntry(master=frame, placeholder_text="Enter query...")
    query.pack(padx=10, pady=12)
    image_frame = ctk.CTkFrame(master=frame)
    search_button = ctk.CTkButton(master=frame, text="Search", command=lambda: fetch_wallpapers(query.get(), image_frame))
    search_button.pack(padx=10, pady=12)
    image_frame.pack(padx=10, pady=12, fill="both", expand=True)
    root.mainloop()

def display_wallpapers(wallpapers, image_frame):
    # Clear previous images
    for widget in image_frame.winfo_children():
        widget.destroy()
    
    # Configure grid layout
    image_frame.grid_columnconfigure((0, 1), weight=1)
    image_frame.grid_rowconfigure((0, 1), weight=1)
    for i, wallpaper in enumerate(wallpapers[:4]): # Display first 4 wallpapers
        image_url = wallpaper['thumbs']['small']
        response = requests.get(image_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((400, 300), Image.Resampling.LANCZOS)
        img = Image.open(BytesIO(img_data))
        ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 300))
        
        img_button = ctk.CTkButton(master=image_frame, image=ctk_image, text="", width=400, height=300, 
                                fg_color="transparent", hover_color="gray75",
                                command=lambda w=wallpaper: apply_wallpaper(w['path']))
        img_button.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")

def apply_wallpaper(wallpaper_url):
    print("wallpaper url:", wallpaper_url)
    response = requests.get(wallpaper_url)
    response.raise_for_status()
    img_data = response.content
    
    # Save the image in the user's Pictures folder
    pictures_folder = os.path.join(os.path.expanduser("~"), "Pictures")
    wallpaper_file = os.path.join(pictures_folder, "current_wallpaper.jpg")
    
    with open(wallpaper_file, "wb") as file:
        file.write(img_data)
    
    # Convert the path to a wide string (needed for Windows API)
    wallpaper_path = ctypes.c_wchar_p(wallpaper_file)

    # Windows API constants
    SPI_SETDESKWALLPAPER = 0x0014
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02

    # Change the wallpaper
    if not ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE):
        print(f"Failed to set wallpaper. Error code: {ctypes.get_last_error()}")
    else:
        print(f"Wallpaper applied successfully: {wallpaper_file}")

# Fetch wallpapers and create the GUI
create_gui_new()
