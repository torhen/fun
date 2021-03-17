import arcade
import pymunk
import math


space = pymunk.Space()
space.gravity = 0, -800


class Ball:
    def __init__(self, space, x, y):
        self.body = pymunk.Body(1, 1666)
        self.body.position = x, y

        # self.shape = pymunk.Circle(self.body, 20)
        self.shape = pymunk.Poly.create_box(self.body, size=(50, 50))
        self.shape.elasticity = 0.83
        self.shape.friction = 100
        space.add(self.body, self.shape)

    def draw(self):
        x, y = self.body.position
        r = self.shape.radius
        arcade.draw_circle_outline(x, y, r, color=arcade.color.WHITE)
        dx = r * math.cos(self.body.angle)
        dy = r * math.sin(self.body.angle)
        ang = self.body.angle
        #arcade.draw_line(x, y, x + dx, y + dy, color=arcade.color.WHITE)
        arcade.draw_rectangle_outline(x, y, 50, 50, color=arcade.color.WHITE,tilt_angle=ang * 180 / math.pi)

    def set_pos(self, x, y):
        self.body.position = x, y


class Plane:
    def __init__(self, space, x0, y0, x1, y1):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, (x0, y0), (x1, y1), 5)
        self.shape.elasticity = 0.83
        self.shape.friction = 100
        space.add(self.body, self.shape)

    def draw(self):
        arcade.draw_line(self.x0, self.y0, self.x1, self.y1, color=arcade.color.WHITE)


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

        self.ball = Ball(space, 50, 500)
        self.plane1 = Plane(space, 0, 120, 300, 50)
        self.plane2 = Plane(space, 300, 50, 800, 50)

    def on_draw(self):
        arcade.start_render()
        self.ball.draw()
        self.plane1.draw()
        self.plane2.draw()

    def on_update(self, delta_time):
        space.step(delta_time)
        x, y = self.ball.body.position
        vel = self.ball.body.velocity
        if x > 1000 or x < -100 or y < 70 or (abs(vel) < 0.01 and y < 300):
            self.ball.body.position = 50, 500
            self.ball.body.velocity = 0, 0



game = Game()
arcade.run()