import numpy as np
from matplotlib import pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import matplotlib

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.d = 0
        self.geometry('640x480')

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.cbar_is_created = False

        self.all_colormaps = sorted(matplotlib.colormaps, key=str.lower)
        self.cm_number = 0

        
        self.x0, self.y0 = -0.7436336929564845, 0.1319065795442757
        self.r = 2
        self.max_iterations = 100
        self.resx = 640 // 4
        self.resy = 480 // 4
       
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(expand=True, fill='both')
        # self.canvas.get_tk_widget().bind("<Button-1>", self.on_tk_click)
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.canvas.mpl_connect("key_press_event", self.on_key)

        self.calc()
    
    def on_click(self, e):
        if e.button == 1:
            self.x0, self.y0 = e.xdata, e.ydata
        if e.button == 3:
            self.x0, self.y0 = e.xdata, e.ydata
        self.calc()

    def on_scroll(self, e):
        # self.x0, self.y0 = e.xdata, e.ydata
        if e.button == 'up':
            self.r = self.r * 0.9
        if e.button == 'down':
            self.r = self.r * 1.1
        self.calc()

    def on_key(self, e):
        if e.key == " " or e.key == 'right':  # Space bar
            self.cm_number += 1
            if self.cm_number > len(self.all_colormaps):
                self.cm_number = 0

        if e.key == 'left':
            self.cm_number -= 1
            if self.cm_number < 0:
                self.cm_number = 0

        print(e.key)
        self.calc()

 
    def calc(self):
        start = time.time()
        x = np.linspace(self.x0 - self.r, self.x0 + self.r, self.resx, dtype=np.complex128)
        y = np.linspace(self.y0 - self.r, self.y0 + self.r, self.resy, dtype=np.complex128)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y

        Z = np.zeros_like(C, complex)
        I = np.zeros_like(C, int)


        x_min, x_max = X.min(), X.max()
        y_min, y_max = Y.min(), Y.max()

        for i in range(self.max_iterations):
            Z = Z * Z + C
            I = np.where(abs(Z) <100, i, I)

        self.ax.clear()

        cm = self.all_colormaps[self.cm_number]
        self.ax.contourf(X, Y, I, cmap=cm, vmin=0, vmax=self.max_iterations)
        # self.im = self.ax.imshow(I, extent=[x_min, x_max, y_min, y_max], cmap=cm, vmin=0, vmax=self.max_iterations)
        
        self.ax.set_title(f'{cm}')
        self.canvas.draw()
        print(f'{time.time() - start:.2f} sec ({self.x0}, {self.y0}, {self.r})')
app = App()
app.mainloop()
