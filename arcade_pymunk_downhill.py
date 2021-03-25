import arcade
import pymunk
import random

space = pymunk.Space()
space.gravity = 0, -1000

def add_ball(x, y, r):
    body = pymunk.Body()
    body.position = x, y
    shape = pymunk.Circle(body, r)
    shape.density = 1
    shape.elasticity = 0.2
    shape.friction = 1
    space.add(body, shape)
    return body

def add_plane():
    pt1 = pymunk.Vec2d(0, 0)
    for _ in range(500):
        pt2 = pt1 + (50, - random.randint(0, 30))
        shape = pymunk.Segment(space.static_body, pt1, pt2, 5)
        pt1 = pt2
        shape.elasticity = 0.2
        shape.friction = 1
        space.add(shape)


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        self.ball = add_ball(10, 100, 30)
        add_plane()

    def on_draw(self):
        arcade.start_render()
        ball_pos = self.ball.position
        vel = abs(self.ball.velocity)
        arcade.draw_text(f'velocity {round(vel)}',0, 0, arcade.color.WHITE)
        v = pymunk.Vec2d(self.width / 2, self.height / 2) - ball_pos
        for shape in space.shapes:
            if isinstance(shape, pymunk.Circle):  # pymunk.Circle
                pos = shape.body.position + v
                r = shape.radius
                ang = shape.body.angle
                arcade.draw_circle_outline(*pos, r, arcade.color.WHITE)
                rv = pymunk.Vec2d(0, r).rotated(ang)
                arcade.draw_line(*pos, *(pos + rv), arcade.color.WHITE)
            if isinstance(shape, pymunk.Segment):  # pymunk.Segment
                a = shape.a + v
                b = shape.b + v
                arcade.draw_line(*a, *b, arcade.color.WHITE)
                arcade.draw_circle_filled(*a, 3, arcade.color.WHITE)

    def on_update(self, dt):
        space.step(1/30)

    def on_key_press(self, symbol: int, modifiers: int):
        self.ball.apply_impulse_at_local_point((100000,0))


game = Game()
arcade.run()