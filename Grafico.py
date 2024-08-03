#developed by Luciano
#date 08/02/2023

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import sounddevice as sd
import queue

class RealTimeSoundGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gráfico de Som em Tempo Real")

        self.sample_rate = 44100
        self.chunk_size = 1024

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.subplot = self.figure.add_subplot(1, 1, 1)
        self.line, = self.subplot.plot([], [])
        self.subplot.set_title("Gráfico de Som em Tempo Real")
        self.subplot.set_xlabel("Tempo (s)")
        self.subplot.set_ylabel("Amplitude")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=self.sample_rate)
        self.queue = queue.Queue()

        self.start_button = ttk.Button(root, text="Iniciar Captura", command=self.start_capture)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(root, text="Parar Captura", command=self.stop_capture)
        self.stop_button.pack(pady=10)

    def start_capture(self):
        self.stream.start()

    def stop_capture(self):
        self.stream.stop()

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)

        self.queue.put(indata.copy())

        if self.queue.qsize() > 10:
            self.queue.get_nowait()

        self.update_plot()

    def update_plot(self):
        try:
            data = np.concatenate(list(self.queue.queue), axis=0)
            t = np.arange(0, len(data) / self.sample_rate, 1 / self.sample_rate)
            self.line.set_data(t, data)
            self.subplot.relim()
            self.subplot.autoscale_view()
            self.canvas.draw()
        except queue.Empty:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimeSoundGraphApp(root)
    root.mainloop()
