import tkinter as tk
from tkinter import filedialog
import subprocess
from pydub import AudioSegment
import os

root = tk.Tk()
root.title("Audio analyzer")

def select_file():
    file_path = filedialog.askopenfilename()
    result_text.config(state=tk.NORMAL)  # Enable the text widget
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, "Selected file: {}\n".format(os.path.basename(file_path)))
    start_times = process_file(file_path)
    # Display results as a list in vertical fashion
    result_text.insert(tk.END, "Start times:\n{}".format("\n".join([format_time(t) for t in start_times])))
    result_text.config(state=tk.DISABLED)  # Disable the text widget
    # Update the scrollbar
    result_scrollbar.set(0.0, 1.0)

def process_file(file_path):
    # Remove old temp.wav file if it exists
    if os.path.exists('temp.wav'):
        os.remove('temp.wav')
    # Extract audio stream from MP4 file and save as WAV file
    subprocess.run(['ffmpeg', '-i', file_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '48000', '-ac', '2', 'temp.wav'])

    # Read WAV file and analyze audio wave
    audio = AudioSegment.from_wav('temp.wav')
    start_times = []
    start = None
    thresholds = [-3, -2, -1, 0]
    for threshold in thresholds:
        for i in range(len(audio)):
            if audio[i].dBFS >= threshold:
                if start is None:
                    start = i - 1000
            elif start is not None and i - start > 3000:
                start_times.append(start / 1000)
                start = None
            elif start is not None and i == len(audio) - 1:
                start_times.append(start / 1000)
        if start is not None and len(audio) - start > 3000:
            start_times.append(start / 1000)

    # Return the list of start times
    return start_times

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

select_button = tk.Button(root, text="Select MP4 file", command=select_file)
select_button.pack(pady=20)
root.geometry("400x200")

# Create a scrollbar
result_scrollbar = tk.Scrollbar(root)
result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a text widget for displaying results
result_text = tk.Text(root, wrap=tk.WORD, yscrollcommand=result_scrollbar.set)
result_text.pack(expand=tk.YES, fill=tk.BOTH)

# Configure the scrollbar
result_scrollbar.config(command=result_text.yview)

root.mainloop()
