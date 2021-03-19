import arcade
import pymunk
import random

space = pymunk.Space()
space.gravity = 0, 0


class Ball:
    def __init__(self, x, y, r):
        self.x, self.y, self.r = x, y, r
        self.color = arcade.color.WHITE
        self.body = pymunk.Body(1, 16666)
        self.body.position = self.x, self.y
        self.body.velocity = random.randint(-500, 500), random.randint(-500, 500)

        self.shape = pymunk.Circle(self.body, self.r)
        self.shape.elasticity = 1

        space.add(self.body, self.shape)

    def draw(self):
        self.x, self.y = self.body.position
        arcade.draw_circle_outline(self.x, self.y, self.r, color=self.color)


class Plane:
    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.r = 10
        self.color = arcade.color.WHITE

        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)

        self.shape = pymunk.Segment(self.body, (self.x0, self.y0), (self.x1, self.y1), self.r)
        self.shape.elasticity = 1

        space.add(self.body, self.shape)

    def draw(self):
        arcade.draw_line(self.x0, self.y0, self.x1, self.y1, color=self.color)


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        self.elements = []

        for _ in range(100):
            x = random.randint(100, 500)
            y = random.randint(100, 500)
            self.elements.append( Ball(x, y, 10) )

        self.elements.append( Plane(50, 50, 750, 50) )
        self.elements.append( Plane(50, 50, 50, 550) )
        self.elements.append( Plane(50, 550, 750, 550) )
        self.elements.append( Plane(750, 550, 750, 50) )

    def on_draw(self):
        arcade.start_render()
        for elem in self.elements:
            elem.draw()

    def on_update(self, dt):
        space.step(dt)


game = Game()
arcade.run()