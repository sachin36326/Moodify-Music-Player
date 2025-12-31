"""
MOODIFY - AI-Powered Music Mood Player
A simple Python music player that detects emotions from song lyrics
"""

import os
import json
import random
import requests
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import pygame
from collections import Counter
import re

# Initialize pygame mixer for audio
pygame.mixer.init()

class MoodifyPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Moodify - AI Music Mood Player")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e2e")
        
        # Variables
        self.current_song = None
        self.is_playing = False
        self.song_list = []
        self.lyrics_cache = {}
        self.mood_colors = {
            'happy': '#FFD700',
            'sad': '#4169E1',
            'romantic': '#FF69B4',
            'energetic': '#FF4500',
            'calm': '#32CD32',
            'angry': '#DC143C',
            'neutral': '#808080'
        }
        
        # Setup GUI
        self.setup_gui()
        self.load_sample_songs()
        
    def setup_gui(self):
        """Create the user interface"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(main_frame, bg="#282a36")
        header.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header, text="🎵 MOODIFY", font=("Arial", 28, "bold"),
                        bg="#282a36", fg="#f8f8f2")
        title.pack(pady=10)
        
        subtitle = tk.Label(header, text="AI-Powered Music Mood Detection Player",
                           font=("Arial", 12), bg="#282a36", fg="#bd93f9")
        subtitle.pack(pady=(0, 10))
        
        # Body with two columns
        body_frame = tk.Frame(main_frame, bg="#1e1e2e")
        body_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Song controls
        left_panel = tk.Frame(body_frame, bg="#282a36", relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Song list
        song_list_label = tk.Label(left_panel, text="🎶 Song Library", 
                                  font=("Arial", 14, "bold"), bg="#282a36", fg="#f8f8f2")
        song_list_label.pack(pady=10)
        
        # Search box
        search_frame = tk.Frame(left_panel, bg="#282a36")
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(search_frame, text="Search:", bg="#282a36", fg="#f8f8f2").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_songs)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               bg="#44475a", fg="#f8f8f2", insertbackground="white")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(left_panel, bg="#282a36")
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.song_listbox = tk.Listbox(listbox_frame, bg="#44475a", fg="#f8f8f2",
                                      selectbackground="#6272a4", yscrollcommand=scrollbar.set,
                                      font=("Arial", 10), selectmode=tk.SINGLE)
        self.song_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.song_listbox.yview)
        
        # Control buttons
        control_frame = tk.Frame(left_panel, bg="#282a36")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        button_style = {"bg": "#44475a", "fg": "#f8f8f2", "activebackground": "#6272a4",
                       "font": ("Arial", 10), "relief": tk.RAISED, "borderwidth": 2}
        
        self.play_btn = tk.Button(control_frame, text="▶ Play", command=self.play_selected,
                                 **button_style)
        self.play_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.pause_btn = tk.Button(control_frame, text="⏸ Pause", command=self.pause_music,
                                  **button_style)
        self.pause_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.stop_btn = tk.Button(control_frame, text="⏹ Stop", command=self.stop_music,
                                 **button_style)
        self.stop_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Right panel - Lyrics and Mood
        right_panel = tk.Frame(body_frame, bg="#282a36", relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Now Playing section
        now_playing_frame = tk.Frame(right_panel, bg="#282a36")
        now_playing_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.now_playing_label = tk.Label(now_playing_frame, text="Now Playing: None",
                                         font=("Arial", 12, "bold"), bg="#282a36", fg="#50fa7b")
        self.now_playing_label.pack(anchor=tk.W)
        
        # Mood visualization
        mood_frame = tk.Frame(right_panel, bg="#282a36")
        mood_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.mood_label = tk.Label(mood_frame, text="Detected Mood: --",
                                  font=("Arial", 14, "bold"), bg="#282a36", fg="#ff79c6")
        self.mood_label.pack(anchor=tk.W)
        
        # Mood color bar
        self.mood_canvas = tk.Canvas(mood_frame, bg="#44475a", height=30, highlightthickness=0)
        self.mood_canvas.pack(fill=tk.X, pady=5)
        
        # Lyrics display
        lyrics_label = tk.Label(right_panel, text="📝 Lyrics", font=("Arial", 14, "bold"),
                               bg="#282a36", fg="#f8f8f2")
        lyrics_label.pack(pady=(10, 5))
        
        self.lyrics_text = scrolledtext.ScrolledText(right_panel, bg="#44475a", fg="#f8f8f2",
                                                    font=("Courier", 10), wrap=tk.WORD,
                                                    height=15)
        self.lyrics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Mood keywords
        keywords_frame = tk.Frame(right_panel, bg="#282a36")
        keywords_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.keywords_label = tk.Label(keywords_frame, text="Mood Keywords: --",
                                      bg="#282a36", fg="#f1fa8c")
        self.keywords_label.pack(anchor=tk.W)
        
        # Status bar
        self.status_bar = tk.Label(main_frame, text="Ready", bd=1, relief=tk.SUNKEN,
                                  anchor=tk.W, bg="#282a36", fg="#f8f8f2")
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def load_sample_songs(self):
        """Load sample songs (you can add your own MP3 files)"""
        self.song_list = [
            {"title": "Bohemian Rhapsody", "artist": "Queen", "file": "bohemian.mp3", "url": None},
            {"title": "Imagine", "artist": "John Lennon", "file": "imagine.mp3", "url": None},
            {"title": "Blinding Lights", "artist": "The Weeknd", "file": None, "url": "search"},
            {"title": "Perfect", "artist": "Ed Sheeran", "file": None, "url": "search"},
            {"title": "Shape of You", "artist": "Ed Sheeran", "file": None, "url": "search"},
            {"title": "Someone Like You", "artist": "Adele", "file": None, "url": "search"},
            {"title": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "file": None, "url": "search"},
            {"title": "Despacito", "artist": "Luis Fonsi", "file": None, "url": "search"},
            {"title": "See You Again", "artist": "Wiz Khalifa ft. Charlie Puth", "file": None, "url": "search"},
            {"title": "Happy", "artist": "Pharrell Williams", "file": None, "url": "search"},
        ]
        
        self.update_song_listbox()
    
    def update_song_listbox(self, filtered_list=None):
        """Update the song listbox"""
        self.song_listbox.delete(0, tk.END)
        
        songs_to_show = filtered_list if filtered_list else self.song_list
        
        for song in songs_to_show:
            display_text = f"{song['title']} - {song['artist']}"
            if song.get('file'):
                display_text += " 📁"
            self.song_listbox.insert(tk.END, display_text)
    
    def filter_songs(self, *args):
        """Filter songs based on search"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.update_song_listbox()
            return
        
        filtered = []
        for song in self.song_list:
            if (search_term in song['title'].lower() or 
                search_term in song['artist'].lower()):
                filtered.append(song)
        
        self.update_song_listbox(filtered)
    
    def play_selected(self):
        """Play selected song"""
        selection = self.song_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a song from the list")
            return
        
        # Get selected song
        index = selection[0]
        all_items = self.song_listbox.get(0, tk.END)
        
        # Find the actual song
        for song in self.song_list:
            if f"{song['title']} - {song['artist']}" == all_items[index]:
                self.current_song = song
                break
        
        if not self.current_song:
            return
        
        # Update UI
        self.now_playing_label.config(text=f"Now Playing: {self.current_song['title']}")
        self.status_bar.config(text=f"Loading {self.current_song['title']}...")
        
        # Get lyrics and analyze mood
        self.get_lyrics_and_analyze()
        
        # Simulate playback (in real app, you'd play actual audio)
        self.is_playing = True
        self.status_bar.config(text=f"Playing: {self.current_song['title']}")
        
        # Show message
        messagebox.showinfo("Playing Song", 
                          f"Now playing: {self.current_song['title']}\n"
                          f"Artist: {self.current_song['artist']}\n\n"
                          f"Note: This is a demo. Add MP3 files to 'songs' folder for actual playback.")
    
    def get_lyrics_and_analyze(self):
        """Get lyrics and analyze mood"""
        song = self.current_song
        
        # Clear previous
        self.lyrics_text.delete(1.0, tk.END)
        
        # Try to get lyrics
        lyrics = self.fetch_lyrics(song['title'], song['artist'])
        
        if lyrics:
            self.lyrics_text.insert(tk.END, lyrics)
            
            # Analyze mood
            mood, keywords = self.analyze_mood(lyrics)
            
            # Update mood display
            self.mood_label.config(text=f"Detected Mood: {mood.upper()}")
            self.keywords_label.config(text=f"Mood Keywords: {', '.join(keywords[:5])}")
            
            # Update mood color bar
            color = self.mood_colors.get(mood, '#808080')
            self.mood_canvas.delete("all")
            self.mood_canvas.create_rectangle(0, 0, 300, 30, fill=color, outline="")
            self.mood_canvas.create_text(150, 15, text=mood.upper(), 
                                        font=("Arial", 12, "bold"), fill="white")
        else:
            self.lyrics_text.insert(tk.END, "Lyrics not available for this song.")
            self.mood_label.config(text="Detected Mood: Unknown")
            self.keywords_label.config(text="Mood Keywords: None")
    
    def fetch_lyrics(self, title, artist):
        """Fetch lyrics from API"""
        # Cache check
        cache_key = f"{title}_{artist}"
        if cache_key in self.lyrics_cache:
            return self.lyrics_cache[cache_key]
        
        try:
            # Try lyrics.ovh API
            url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                lyrics = response.json().get('lyrics', '')
                if lyrics:
                    # Clean lyrics
                    lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Remove [Verse], [Chorus]
                    self.lyrics_cache[cache_key] = lyrics
                    return lyrics
            
            # Try alternative for popular songs
            popular_lyrics = {
                "Bohemian Rhapsody": """Is this the real life? Is this just fantasy?
Caught in a landslide, no escape from reality
Open your eyes, look up to the skies and see
I'm just a poor boy, I need no sympathy
Because I'm easy come, easy go, little high, little low
Any way the wind blows doesn't really matter to me, to me""",
                
                "Imagine": """Imagine there's no heaven
It's easy if you try
No hell below us
Above us only sky
Imagine all the people
Living for today""",
                
                "Happy": """It might seem crazy what I'm about to say
Sunshine she's here, you can take a break
I'm a hot air balloon that could go to space
With the air, like I don't care, baby, by the way"""
            }
            
            if title in popular_lyrics:
                return popular_lyrics[title]
                
        except Exception as e:
            print(f"Lyrics fetch error: {e}")
        
        return None
    
    def analyze_mood(self, lyrics):
        """Simple mood analysis from lyrics"""
        # Mood keywords mapping
        mood_keywords = {
            'happy': ['love', 'happy', 'joy', 'smile', 'sun', 'light', 'good', 'beautiful', 'wonderful'],
            'sad': ['sad', 'lonely', 'cry', 'tears', 'pain', 'hurt', 'alone', 'miss', 'goodbye'],
            'romantic': ['love', 'heart', 'kiss', 'hold', 'touch', 'darling', 'baby', 'sweet', 'forever'],
            'energetic': ['go', 'move', 'dance', 'jump', 'run', 'party', 'energy', 'wild', 'fire'],
            'calm': ['peace', 'calm', 'quiet', 'still', 'gentle', 'soft', 'easy', 'slow', 'dream'],
            'angry': ['hate', 'angry', 'rage', 'fight', 'war', 'kill', 'burn', 'break', 'mad']
        }
        
        lyrics_lower = lyrics.lower()
        scores = {}
        
        # Count keyword matches
        for mood, keywords in mood_keywords.items():
            count = 0
            for keyword in keywords:
                count += lyrics_lower.count(keyword)
            scores[mood] = count
        
        # Find dominant mood
        if sum(scores.values()) == 0:
            return 'neutral', []
        
        dominant_mood = max(scores, key=scores.get)
        
        # Get top keywords
        found_keywords = []
        for keyword in mood_keywords[dominant_mood]:
            if keyword in lyrics_lower:
                found_keywords.append(keyword)
        
        return dominant_mood, found_keywords[:5]
    
    def pause_music(self):
        """Pause/resume music"""
        if self.current_song:
            self.is_playing = not self.is_playing
            if self.is_playing:
                self.status_bar.config(text=f"Resumed: {self.current_song['title']}")
                self.pause_btn.config(text="⏸ Pause")
            else:
                self.status_bar.config(text=f"Paused: {self.current_song['title']}")
                self.pause_btn.config(text="▶ Resume")
    
    def stop_music(self):
        """Stop music"""
        if self.current_song:
            self.is_playing = False
            self.status_bar.config(text=f"Stopped: {self.current_song['title']}")
            self.now_playing_label.config(text="Now Playing: None")
            self.lyrics_text.delete(1.0, tk.END)
            self.mood_label.config(text="Detected Mood: --")
            self.keywords_label.config(text="Mood Keywords: --")
            self.mood_canvas.delete("all")

def main():
    """Main function"""
    root = tk.Tk()
    app = MoodifyPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("songs", exist_ok=True)
    os.makedirs("lyrics_data", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    
    # Check requirements
    try:
        import pygame
        import PIL
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.call(['pip', 'install', 'pygame', 'pillow', 'requests'])
        print("Please restart the application.")
    
    main()