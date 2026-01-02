"""
MOODIFY MINIMAL - Works without pygame/pillow
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import re
import json

class MoodifyMinimal:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Moodify Minimal")
        self.root.geometry("900x700")
        self.root.configure(bg="#2b2b2b")
        
        self.setup_gui()
        
    def setup_gui(self):
        # Header
        header = tk.Frame(self.root, bg="#3c3c3c", height=80)
        header.pack(fill=tk.X)
        
        title = tk.Label(header, text="🎵 MOODIFY", font=("Arial", 28, "bold"),
                        bg="#3c3c3c", fg="white")
        title.pack(pady=20)
        
        # Body
        body = tk.Frame(self.root, bg="#2b2b2b")
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Input
        left = tk.Frame(body, bg="#3c3c3c", relief=tk.RAISED, borderwidth=2)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left, text="Enter Song Details", font=("Arial", 14, "bold"),
                bg="#3c3c3c", fg="white").pack(pady=20)
        
        # Song input
        tk.Label(left, text="Song Title:", bg="#3c3c3c", fg="white").pack(anchor=tk.W, padx=20)
        self.song_entry = tk.Entry(left, bg="#4a4a4a", fg="white", 
                                  insertbackground="white", font=("Arial", 12))
        self.song_entry.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Artist input
        tk.Label(left, text="Artist (optional):", bg="#3c3c3c", fg="white").pack(anchor=tk.W, padx=20)
        self.artist_entry = tk.Entry(left, bg="#4a4a4a", fg="white",
                                    insertbackground="white", font=("Arial", 12))
        self.artist_entry.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Search button
        tk.Button(left, text="🔍 Find Lyrics & Analyze Mood", 
                 command=self.analyze_song, bg="#007acc", fg="white",
                 font=("Arial", 12, "bold"), height=2).pack(padx=20, pady=10, fill=tk.X)
        
        # Sample songs
        sample_frame = tk.Frame(left, bg="#3c3c3c")
        sample_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(sample_frame, text="Try these:", bg="#3c3c3c", fg="#aaa").pack(anchor=tk.W)
        
        samples = ["Bohemian Rhapsody - Queen", "Imagine - John Lennon", "Happy - Pharrell Williams"]
        for sample in samples:
            btn = tk.Button(sample_frame, text=sample, bg="#555", fg="white",
                           command=lambda s=sample: self.load_sample(s))
            btn.pack(fill=tk.X, pady=2)
        
        # Right panel - Results
        right = tk.Frame(body, bg="#3c3c3c", relief=tk.RAISED, borderwidth=2)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Mood display
        self.mood_frame = tk.Frame(right, bg="#3c3c3c")
        self.mood_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.mood_label = tk.Label(self.mood_frame, text="Mood: --", 
                                  font=("Arial", 16, "bold"), bg="#3c3c3c", fg="white")
        self.mood_label.pack(anchor=tk.W)
        
        self.mood_desc = tk.Label(self.mood_frame, text="", 
                                 bg="#3c3c3c", fg="#aaa")
        self.mood_desc.pack(anchor=tk.W)
        
        # Lyrics display
        tk.Label(right, text="📝 Lyrics", font=("Arial", 14, "bold"),
                bg="#3c3c3c", fg="white").pack(anchor=tk.W, padx=20, pady=(0, 5))
        
        self.lyrics_text = scrolledtext.ScrolledText(right, bg="#1e1e1e", fg="white",
                                                    font=("Courier", 10), wrap=tk.WORD)
        self.lyrics_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Status bar
        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN,
                              anchor=tk.W, bg="#007acc", fg="white")
        self.status.pack(fill=tk.X, side=tk.BOTTOM)
    
    def load_sample(self, sample):
        parts = sample.split(" - ")
        if len(parts) == 2:
            self.song_entry.delete(0, tk.END)
            self.artist_entry.delete(0, tk.END)
            self.song_entry.insert(0, parts[0])
            self.artist_entry.insert(0, parts[1])
    
    def analyze_song(self):
        song = self.song_entry.get().strip()
        artist = self.artist_entry.get().strip()
        
        if not song:
            messagebox.showerror("Error", "Please enter a song title!")
            return
        
        self.status.config(text=f"Searching for {song}...")
        self.root.update()
        
        # Get lyrics
        lyrics = self.get_lyrics(song, artist)
        
        if not lyrics:
            messagebox.showerror("Error", "Could not find lyrics for this song")
            self.status.config(text="Error: Lyrics not found")
            return
        
        # Display lyrics
        self.lyrics_text.delete(1.0, tk.END)
        self.lyrics_text.insert(tk.END, lyrics)
        
        # Analyze mood
        mood, keywords = self.analyze_mood(lyrics)
        
        # Update mood display
        colors = {
            'happy': '#FFD700',
            'sad': '#4169E1', 
            'romantic': '#FF69B4',
            'energetic': '#FF4500',
            'calm': '#32CD32',
            'neutral': '#808080'
        }
        
        color = colors.get(mood, '#808080')
        self.mood_label.config(text=f"Mood: {mood.upper()}", fg=color)
        self.mood_desc.config(text=f"Keywords: {', '.join(keywords[:5])}")
        
        self.status.config(text=f"✓ Found lyrics for {song} | Mood: {mood}")
    
    def get_lyrics(self, song, artist=""):
        """Get lyrics from API"""
        try:
            # Clean inputs
            song_clean = requests.utils.quote(song)
            artist_clean = requests.utils.quote(artist) if artist else "various"
            
            # Try lyrics.ovh
            url = f"https://api.lyrics.ovh/v1/{artist_clean}/{song_clean}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                lyrics = response.json().get('lyrics')
                if lyrics:
                    return lyrics
            
            # Try alternative without artist
            if artist:
                url2 = f"https://api.lyrics.ovh/v1/various/{song_clean}"
                response2 = requests.get(url2, timeout=5)
                if response2.status_code == 200:
                    lyrics = response2.json().get('lyrics')
                    return lyrics
        
        except Exception as e:
            print(f"Error getting lyrics: {e}")
        
        # Fallback lyrics for demo
        fallback_lyrics = {
            "bohemian rhapsody": """Is this the real life? Is this just fantasy?
Caught in a landslide, no escape from reality
Open your eyes, look up to the skies and see
I'm just a poor boy, I need no sympathy""",
            
            "imagine": """Imagine there's no heaven
It's easy if you try
No hell below us
Above us only sky
Imagine all the people
Living for today""",
            
            "happy": """It might seem crazy what I'm about to say
Sunshine she's here, you can take a break
I'm a hot air balloon that could go to space
With the air, like I don't care baby by the way"""
        }
        
        for key, value in fallback_lyrics.items():
            if key in song.lower():
                return value
        
        return None
    
    def analyze_mood(self, lyrics):
        """Simple mood analysis"""
        lyrics_lower = lyrics.lower()
        
        mood_words = {
            'happy': ['happy', 'joy', 'smile', 'love', 'sun', 'bright', 'good', 'beautiful'],
            'sad': ['sad', 'lonely', 'cry', 'tears', 'pain', 'hurt', 'alone', 'miss'],
            'romantic': ['love', 'heart', 'kiss', 'hold', 'touch', 'darling', 'sweet'],
            'energetic': ['go', 'move', 'dance', 'jump', 'run', 'party', 'energy', 'fire'],
            'calm': ['peace', 'calm', 'quiet', 'still', 'gentle', 'soft', 'easy']
        }
        
        scores = {}
        found_keywords = []
        
        for mood, words in mood_words.items():
            count = 0
            for word in words:
                if word in lyrics_lower:
                    count += 1
                    found_keywords.append(word)
            scores[mood] = count
        
        # Get dominant mood
        if not scores:
            return 'neutral', []
        
        dominant = max(scores, key=scores.get)
        
        # Filter keywords for dominant mood
        final_keywords = [kw for kw in found_keywords if kw in mood_words[dominant]]
        
        return dominant, final_keywords[:5]

def check_and_install():
    """Check if requests is installed, install if not"""
    try:
        import requests
        print("✅ requests is already installed")
        return True
    except ImportError:
        print("⚠️ Installing requests module...")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            print("✅ requests installed successfully")
            return True
        except:
            print("❌ Failed to install requests")
            return False

if __name__ == "__main__":
    # Check for requests
    if check_and_install():
        root = tk.Tk()
        app = MoodifyMinimal(root)
        root.mainloop()
    else:
        input("Press Enter to exit...")