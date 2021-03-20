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


def ball(x, y, r):
    body = pymunk.Body()
    body.position = x, y

    shape1 = pymunk.Circle(body, r)
    shape1.density = 1
    shape1.elasticity = 0.85
    shape1.friction = 10

    shape2 = pymunk.Circle(body, 0.9*r, offset=(30,0))
    shape2.density = 1
    shape2.elasticity = 0.85
    shape2.friction = 10
    space.add(body, shape1, shape2)
    return body


def plane(x0, y0, x1, y1, r):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (x0, y0), (x1, y1), r)
    shape.elasticity = 0.85
    shape.friction = 10
    space.add(body, shape)
    return body


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        self.time = 0
        self.ball = ball(100, 500, 50)
        self.plane1 = plane(0, 450, 500, 350, 5)
        self.plane1 = plane(0, 50, 800, 200, 5)

    def on_draw(self):
        arcade.start_render()
        space.debug_draw(options)

    def on_update(self, dt):
        self.time += 1/60
        if self.time > 9:
            self.time = 0
            self.ball.body.position = 100, 500
            self.ball.body.velocity = 0, 0
            self.ball.body.angular_velocity = 0
            self.ball.body.angle = 0
        space.step(1/60)


game = Game()
arcade.run()
