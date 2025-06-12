import os
import time
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen.wave import WAVE


class MusicPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pemutar Musik")
        self.root.geometry("600x550")

        mixer.init()

        self.folder_path = ''
        self.playlist = []
        self.current_index = 0
        self.current_song_length = 0
        self.play_start_time = 0
        self.pause_offset = 0
        self.seeking = False
        self.shuffle_mode = False
        self.repeat_mode = False
        self.mode = "light"

        self.build_ui()

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.theme_label = tk.Label(top_frame, text="Mode: Light", font=("Arial", 12))
        self.theme_label.pack(side="left", padx=10)

        self.theme_button = ttk.Button(top_frame, text="Switch to Dark Mode", command=self.toggle_theme)
        self.theme_button.pack(side="left")

        self.folder_btn = tk.Button(self.root, text="Pilih Folder Musik", command=self.load_folder)
        self.folder_btn.pack(pady=10)

        self.listbox = tk.Listbox(self.root, width=60)
        self.listbox.pack(pady=10)

        control_frame = tk.Frame(self.root)
        control_frame.pack()

        self.play_btn = tk.Button(control_frame, text="Play", command=self.play_music)
        self.play_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(control_frame, text="Pause", command=self.pause_music)
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.resume_btn = tk.Button(control_frame, text="Resume", command=self.resume_music)
        self.resume_btn.grid(row=0, column=2, padx=5)

        self.stop_btn = tk.Button(control_frame, text="Stop", command=self.stop_music)
        self.stop_btn.grid(row=0, column=3, padx=5)

        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)

        self.prev_btn = tk.Button(nav_frame, text="<< Prev", command=self.prev_music)
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.next_btn = tk.Button(nav_frame, text="Next >>", command=self.next_music)
        self.next_btn.grid(row=0, column=1, padx=5)

        self.shuffle_btn = tk.Button(nav_frame, text="Shuffle: Off", command=self.toggle_shuffle)
        self.shuffle_btn.grid(row=0, column=2, padx=5)

        self.repeat_btn = tk.Button(nav_frame, text="Repeat: Off", command=self.toggle_repeat)
        self.repeat_btn.grid(row=0, column=3, padx=5)

        volume_frame = tk.Frame(self.root)
        volume_frame.pack(pady=10)

        tk.Label(volume_frame, text="Volume").pack(side="left", padx=5)
        self.volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume_slider.set(70)
        self.volume_slider.pack(side="left")

        duration_frame = tk.Frame(self.root)
        duration_frame.pack(pady=10)

        self.duration_label = tk.Label(duration_frame, text="00:00 / 00:00", font=("Arial", 10))
        self.duration_label.pack()

        self.duration_slider = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, length=500)
        self.duration_slider.pack()

        self.duration_slider.bind("<ButtonPress-1>", self.start_seeking)
        self.duration_slider.bind("<ButtonRelease-1>", self.stop_seeking)

        self.toggle_theme()

    def toggle_theme(self):
        if self.mode == "light":
            bg = "#2e2e2e"
            fg = "white"
            self.mode = "dark"
            self.theme_button.config(text="Switch to Light Mode")
        else:
            bg = "white"
            fg = "black"
            self.mode = "light"
            self.theme_button.config(text="Switch to Dark Mode")

        self.root.configure(bg=bg)
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=bg, fg=fg)
            except:
                pass

        self.theme_label.configure(text=f"Mode: {self.mode.capitalize()}", bg=bg, fg=fg)
        self.duration_label.configure(bg=bg, fg=fg)

    def load_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.playlist = [f for f in os.listdir(self.folder_path)
                             if f.lower().endswith(('.mp3', '.wav'))]
            self.playlist.sort()
            self.listbox.delete(0, tk.END)
            for song in self.playlist:
                self.listbox.insert(tk.END, song)

    def play_music(self):
        try:
            selected = self.listbox.curselection()
            if selected:
                self.current_index = selected[0]
            song = self.playlist[self.current_index]
            song_path = os.path.join(self.folder_path, song)
            mixer.music.load(song_path)
            mixer.music.play()
            self.set_volume(self.volume_slider.get())

            if song.lower().endswith(".mp3"):
                audio = MP3(song_path)
                self.current_song_length = int(audio.info.length)
            elif song.lower().endswith(".wav"):
                audio = WAVE(song_path)
                self.current_song_length = int(audio.info.length)

            self.duration_slider.config(to=self.current_song_length)

            self.play_start_time = time.time()
            self.pause_offset = 0
            self.update_slider()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def pause_music(self):
        mixer.music.pause()
        self.pause_offset += time.time() - self.play_start_time

    def resume_music(self):
        mixer.music.unpause()
        self.play_start_time = time.time()
        self.update_slider()

    def stop_music(self):
        mixer.music.stop()
        self.duration_slider.set(0)
        self.duration_label.config(text="00:00 / " + self.format_time(self.current_song_length))

    def prev_music(self):
        if self.current_index > 0:
            self.current_index -= 1
        elif self.repeat_mode:
            pass
        else:
            return
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(self.current_index)
        self.play_music()

    def next_music(self):
        if self.shuffle_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        elif self.current_index < len(self.playlist) - 1:
            self.current_index += 1
        elif self.repeat_mode:
            pass
        else:
            return
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(self.current_index)
        self.play_music()

    def toggle_shuffle(self):
        self.shuffle_mode = not self.shuffle_mode
        status = "On" if self.shuffle_mode else "Off"
        self.shuffle_btn.config(text=f"Shuffle: {status}")

    def toggle_repeat(self):
        self.repeat_mode = not self.repeat_mode
        status = "On" if self.repeat_mode else "Off"
        self.repeat_btn.config(text=f"Repeat: {status}")

    def set_volume(self, val):
        mixer.music.set_volume(int(val) / 100)

    def start_seeking(self, event):
        self.seeking = True

    def stop_seeking(self, event):
        self.seeking = False
        self.seek_position(self.duration_slider.get())

    def seek_position(self, val):
        pos = int(val)
        mixer.music.play(start=pos)
        self.set_volume(self.volume_slider.get())
        self.play_start_time = time.time() - pos
        self.pause_offset = 0
        self.update_slider()

    def update_slider(self):
        if not self.seeking and mixer.music.get_busy():
            elapsed = int(time.time() - self.play_start_time + self.pause_offset)
            if elapsed <= self.current_song_length:
                self.duration_slider.set(elapsed)
                self.duration_label.config(
                    text=f"{self.format_time(elapsed)} / {self.format_time(self.current_song_length)}"
                )
            else:
                self.duration_slider.set(self.current_song_length)
                self.duration_label.config(
                    text=f"{self.format_time(self.current_song_length)} / {self.format_time(self.current_song_length)}"
                )
                if self.repeat_mode:
                    self.play_music()
                else:
                    self.next_music()
        self.root.after(500, self.update_slider)

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes):02}:{int(secs):02}"


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayerApp(root)
    root.mainloop()
