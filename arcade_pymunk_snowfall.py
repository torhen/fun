import arcade
import pymunk
import random

space = pymunk.Space()
space.gravity = 0, -1000


def add_ball(x, y, r):
    body = pymunk.Body()
    body.position = x, y
    shape = pymunk.Circle(body, r)
    shape.elasticity = 0.5
    shape.friction = 10
    shape.density = 1
    space.add(body, shape)
    return body


def add_plane(x0, y0, x1, y1, r):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (x0, y0), (x1, y1), r)
    shape.elasticity = 0.5
    shape.friction = 10
    space.add(body, shape)


def delete_body(body):
    for shape in body.shapes:
        space.remove(shape)
    space.remove(body)


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        self.time = 0
        add_plane(0, 50, 800, 50, 20)

        self.ball_list = []
        ball = add_ball(300, 800, 10)
        self.ball_list.append(ball)

    def on_draw(self):
        arcade.start_render()
        for shape in space.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = shape.body.position
                r = shape.radius
                arcade.draw_circle_outline(pos.x, pos.y, r, arcade.color.WHITE)
            if isinstance(shape, pymunk.Segment): # pymunk.Segment
                a, b = shape.a, shape.b
                arcade.draw_line(a.x, a.y, b.x, b.y, arcade.color.WHITE)

    def on_update(self, dt):
        self.time = self.time + 1/60
        if self.time > 0.01:
            self.time = 0
            x = random.randint(0, self.width)
            ball = add_ball(x, 800, 10)
            self.ball_list.append(ball)
            if len(self.ball_list) > 500:
                delete_body(self.ball_list[0])
                self.ball_list = self.ball_list[1:]
        space.step(1/60)


game = Game()
arcade.run()