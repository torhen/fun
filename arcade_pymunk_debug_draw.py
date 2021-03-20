import arcade
import pymunk
import math

space = pymunk.Space()
space.gravity = 0, -1000


class ArcadeOptions(pymunk.SpaceDebugDrawOptions):
    def __init__(self):
        super().__init__()

    def draw_circle(self, pos, angle, radius, outline_color, fill_color):
        arcade.draw_circle_outline(pos[0], pos[1], radius, color=arcade.color.WHITE)
        rx = pos.x + math.cos(angle) * radius
        ry = pos.y + math.sin(angle) * radius
        arcade.draw_line(pos.x, pos.y, rx, ry, color=arcade.color.WHITE)

    def draw_segment(self, a, b, color):
        arcade.draw_line(a[0], a[1], b[0], b[1], color=arcade.color.RED, line_width=10)

    def draw_fat_segment(self, a, b, radius, outline_color, fill_color):
        arcade.draw_line(a[0], a[1], b[0], b[1], color=arcade.color.WHITE)


options = ArcadeOptions()


class Ball:
    def __init__(self, x, y, r):
        self.body = pymunk.Body()
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, r)
        self.shape.density = 1
        self.shape.elasticity = 0.85
        self.shape.friction = 10
        space.add(self.body, self.shape)


class Plane:
    def __init__(self, x0, y0, x1, y1, r):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, (x0, y0), (x1, y1), r)
        self.shape.elasticity = 0.85
        self.shape.friction = 10
        space.add(self.body, self.shape)


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        self.ball = Ball(100, 500, 50)
        self.plane1 = Plane(0, 400, 400, 350, 5)
        self.plane1 = Plane(200, 150, 800, 250, 5)
        self.time = 0

    def on_draw(self):
        arcade.start_render()
        space.debug_draw(options)

    def on_update(self, dt):
        self.time += 1/60
        if self.time > 8:
            self.time = 0
            self.ball.body.position = 100, 500
            self.ball.body.velocity = 0, 0
            self.ball.body.angular_velocity = 0
            self.ball.body.angle = 0
        space.step(1/60)


game = Game()
arcade.run()
