"""
ULTRA SIMPLE - No pip install needed!
"""
import tkinter as tk
from tkinter import scrolledtext

class UltraSimpleMoodify:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultra Simple Moodify")
        self.root.geometry("600x400")
        
        # Title
        tk.Label(root, text="🎵 ULTRA SIMPLE MOODIFY", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Instructions
        tk.Label(root, text="Enter lyrics below and see mood analysis").pack()
        
        # Lyrics input
        self.text = scrolledtext.ScrolledText(root, height=10)
        self.text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Buttons
        frame = tk.Frame(root)
        frame.pack()
        
        tk.Button(frame, text="Analyze Mood", command=self.analyze, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Clear", command=self.clear, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Result
        self.result = tk.Label(root, text="Mood: --", font=("Arial", 14, "bold"))
        self.result.pack(pady=10)
        
        # Sample button
        tk.Button(root, text="Load Sample", command=self.load_sample).pack()
    
    def load_sample(self):
        sample = """I'm happy today, the sun is shining
Love is in the air, everything's fine
Smiling all day, feeling so good
This joy in my heart, understood"""
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, sample)
    
    def clear(self):
        self.text.delete(1.0, tk.END)
        self.result.config(text="Mood: --")
    
    def analyze(self):
        lyrics = self.text.get(1.0, tk.END).lower()
        
        happy_words = ['happy', 'joy', 'smile', 'love', 'sun']
        sad_words = ['sad', 'cry', 'pain', 'hurt', 'alone']
        
        happy_count = sum(lyrics.count(word) for word in happy_words)
        sad_count = sum(lyrics.count(word) for word in sad_words)
        
        if happy_count > sad_count:
            mood = "HAPPY 😊"
            color = "green"
        elif sad_count > happy_count:
            mood = "SAD 😢"
            color = "blue"
        else:
            mood = "NEUTRAL 😐"
            color = "gray"
        
        self.result.config(text=f"Mood: {mood}", fg=color)

# Run it
root = tk.Tk()
app = UltraSimpleMoodify(root)
root.mainloop()