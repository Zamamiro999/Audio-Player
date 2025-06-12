import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pygame import mixer
import threading
import time

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Music Player")
        self.root.geometry("500x400")

        mixer.init()

        self.playlist = []
        self.current_index = 0
        self.folder_path = ''

        self.is_playing = False
        self.duration = 0
        self.updating_scale = False

        self.create_widgets()

        self.update_progress_bar_thread = threading.Thread(target=self.update_progress_bar, daemon=True)
        self.update_progress_bar_thread.start()

    def create_widgets(self):
        self.folder_btn = tk.Button(self.root, text="Pilih Folder Musik", command=self.load_folder)
        self.folder_btn.pack(pady=10)

        self.listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=60)
        self.listbox.pack(pady=20)

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.play_btn = tk.Button(control_frame, text="Play", command=self.play_music)
        self.play_btn.grid(row=0, column=0, padx=10)

        self.pause_btn = tk.Button(control_frame, text="Pause", command=self.pause_music)
        self.pause_btn.grid(row=0, column=1, padx=10)

        self.resume_btn = tk.Button(control_frame, text="Resume", command=self.resume_music)
        self.resume_btn.grid(row=0, column=2, padx=10)

        self.stop_btn = tk.Button(control_frame, text="Stop", command=self.stop_music)
        self.stop_btn.grid(row=0, column=3, padx=10)

        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)

        self.prev_btn = tk.Button(nav_frame, text="<< Prev", command=self.prev_music)
        self.prev_btn.grid(row=0, column=0, padx=10)

        self.next_btn = tk.Button(nav_frame, text="Next >>", command=self.next_music)
        self.next_btn.grid(row=0, column=1, padx=10)

        # Volume bar
        volume_frame = tk.Frame(self.root)
        volume_frame.pack(pady=5)
        tk.Label(volume_frame, text="Volume").pack(side=tk.LEFT)
        self.volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume, length=150)
        self.volume_scale.set(70)
        self.volume_scale.pack(side=tk.LEFT)
        mixer.music.set_volume(0.7)

        # Progress bar
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=5)
        tk.Label(progress_frame, text="Durasi").pack(side=tk.LEFT)
        self.progress_scale = tk.Scale(progress_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=300, showvalue=0, command=self.seek_music)
        self.progress_scale.pack(side=tk.LEFT)
        self.progress_label = tk.Label(progress_frame, text="00:00 / 00:00")
        self.progress_label.pack(side=tk.LEFT)

    def set_volume(self, val):
        volume = int(val) / 100
        mixer.music.set_volume(volume)

    def play_music(self):
        try:
            selected = self.listbox.curselection()
            if selected:
                self.current_index = selected[0]
            song_path = os.path.join(self.folder_path, self.playlist[self.current_index])
            mixer.music.load(song_path)
            mixer.music.play()
            self.is_playing = True
            self.duration = self.get_song_length(song_path)
            self.progress_scale.config(to=int(self.duration))
            self.progress_label.config(text=f"00:00 / {self.format_time(self.duration)}")
        except IndexError:
            messagebox.showerror("Error", "Tidak ada lagu yang dipilih atau ditemukan.")

    def pause_music(self):
        mixer.music.pause()
        self.is_playing = False

    def resume_music(self):
        mixer.music.unpause()
        self.is_playing = True

    def stop_music(self):
        mixer.music.stop()
        self.is_playing = False
        self.progress_scale.set(0)
        self.progress_label.config(text=f"00:00 / {self.format_time(self.duration)}")

    def seek_music(self, val):
        if not self.updating_scale and self.duration > 0:
            pos = int(val)
            was_playing = self.is_playing
            mixer.music.pause()
            mixer.music.play(start=pos)
            if not was_playing:
                mixer.music.pause()
            else:
                self.is_playing = True

    def update_progress_bar(self):
        while True:
            if self.is_playing and self.duration > 0:
                try:
                    pos = mixer.music.get_pos() // 1000
                    if pos < 0: pos = 0
                    if pos > self.duration: pos = self.duration
                    self.updating_scale = True
                    self.progress_scale.set(pos)
                    self.progress_label.config(text=f"{self.format_time(pos)} / {self.format_time(self.duration)}")
                    self.updating_scale = False
                except:
                    pass
            time.sleep(1)

    def get_song_length(self, song_path):
        try:
            from mutagen.mp3 import MP3
            from mutagen.wave import WAVE
            if song_path.lower().endswith('.mp3'):
                audio = MP3(song_path)
                return int(audio.info.length)
            elif song_path.lower().endswith('.wav'):
                audio = WAVE(song_path)
                return int(audio.info.length)
        except Exception:
            return 0

    def format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def load_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.playlist = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('.mp3', '.wav'))]
            self.playlist.sort()
            self.listbox.delete(0, tk.END)
            for song in self.playlist:
                self.listbox.insert(tk.END, song)

    def prev_music(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(self.current_index)
            self.play_music()

    def next_music(self):
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(self.current_index)
            self.play_music()

if __name__ == '__main__':
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
