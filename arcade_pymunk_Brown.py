import arcade
import pymunk
import random

space = pymunk.Space()
space.gravity = 0, 0


class Ball:
    def __init__(self, x, y, r):

        self.body = pymunk.Body()
        self.body.position = x, y
        self.body.velocity = random.randint(-500, 500), random.randint(-500, 500)

        self.shape = pymunk.Circle(self.body, r)
        self.shape.density = 1
        self.shape.elasticity = 1

        space.add(self.body, self.shape)

    def draw(self):
        x, y = self.body.position
        r = self.shape.radius
        arcade.draw_circle_outline(x, y, r, arcade.color.WHITE)


class Plane:
    def __init__(self, x0, y0, x1, y1):

        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)

        self.shape = pymunk.Segment(self.body, (x0, y0), (x1, y1), radius=10)
        self.shape.elasticity = 1

        space.add(self.body, self.shape)

    def draw(self):
        x0, y0 = self.shape.a
        x1, y1 = self.shape.b
        arcade.draw_line(x0, y0, x1, y1, color=arcade.color.WHITE)


class Game(arcade.Window):
    def __init__(self):
        super().__init__(resizable=True)
        w, h = self.width, self.height
        self.elements = []

        for _ in range(200):
            x = random.randint(100, 500)
            y = random.randint(100, 500)

            self.elements.append( Ball(x, y, 7) )

        self.elements.append(Ball(w/2, h/2, 30))   # big ball

        self.elements.append( Plane(50, 50, w-50, 50) )
        self.elements.append( Plane(50, 50, 50, h-50) )
        self.elements.append( Plane(50, h-50, w-50, h-50) )
        self.elements.append( Plane(w-50, h-50, w-50, 50) )

    def on_draw(self):
        arcade.start_render()
        for elem in self.elements:
            elem.draw()

    def on_update(self, dt):
        space.step(1/60/2)



game = Game()
arcade.run()