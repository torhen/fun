import arcade
import random

class Star:
    def __init__(self, win):
        self.x = random.random() - 0.5
        self.y = random.random() - 0.5
        self.win = win

    def draw(self):
        x = self.win.width / 2 + self.x
        y = self.win.height / 2 + self.y
        r = self.x / 100
        arcade.draw_circle_filled(x, y, r, arcade.color.WHITE)

    def update(self):
        self.x = self.x * 1.05
        self.y = self.y * 1.05


class Win(arcade.Window):
    def __init__(self):
        super().__init__()
        self.time = 0
        self.starlist = []


    def on_draw(self):
        arcade.start_render()
        for star in self.starlist:
            star.draw()
        arcade.draw_text(str(len(self.starlist)), 0, 0, arcade.color.WHITE)


    def on_update(self, dt):
        self.time = self.time + dt
        if self.time > random.random()/20:
            self.time = 0
            star = Star(self)
            self.starlist.append(star)

        for star in self.starlist:
            star.update()

        self.starlist = [s for s in self.starlist if abs(s.x) < self.width]



win = Win()
arcade.run()