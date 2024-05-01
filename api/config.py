import socket
import os

HOST = os.getenv('HOST', '0.0.0.0')
PORT = 8080
FAMILY = socket.AF_UNSPEC
FLAGS = 0
BUFFER_SIZE = 4096
SERVER_ADDRESS = '::'
SERVER_PORT = 8080
STANDARD_SIZES = [
    ("Instagram (320x320)", "320x320"),
    ("Facebook Desktop (170x170)", "170x170"),
    ("LinkedIn/Twitter (400x400)", "400x400"),
    ("Pinterest (165x165)", "165x165"),
    ("Twitter Post (1024x512)", "1024x512"),
    ("Facebook Post (1200x630)", "1200x630"),
    ("Instagram Story (1080x1920)", "1080x1920"),
    ("YouTube Thumbnail (1280x720)", "1280x720"),
    ("LinkedIn Post Square (1200x1200)", "1200x1200"),
    ("LinkedIn Post Portrait (1080x1350)", "1080x1350"),
    ("Web Banner (468x60)", "468x60"),
    ("Web Leaderboard (728x90)", "728x90"),
    ("Medium Rectangle (300x250)", "300x250"),
    ("Large Rectangle (336x280)", "336x280"),
    ("Skyscraper (120x600)", "120x600"),
    ("Smartphone (1170x2532)", "1170x2532"),
    ("Tablet (1620x2160)", "1620x2160"),
    ("Desktop Wallpaper HD (1920x1080)", "1920x1080"),
    ("Desktop Wallpaper 4K (3840x2160)", "3840x2160"),
    ("Business Card (1050x600)", "1050x600"),
    ("Postcard (1800x1200)", "1800x1200"),
    ("Flyer (2550x3300)", "2550x3300"),
    ("Poster (7200x10800)", "7200x10800"),
    ("Photography Small (640x480)", "640x480"),
    ("Photography Medium (800x600)", "800x600"),
    ("Photography Large (1024x768)", "1024x768"),
    ("Full-Size (2048x1536)", "2048x1536")
]