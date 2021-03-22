import arcade
import pymunk

space = pymunk.Space()
space.gravity = 0, -500


def add_ball(x, y, r):
    body = pymunk.Body()
    body.position = x, y
    shape = pymunk.Circle(body, r)
    shape.density = 1
    shape.elasticity = 0.9
    shape.friction = 3
    space.add(body, shape)
    return body


def add_plane(x0, y0, x1, y1, r):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (x0, y0), (x1, y1), r)
    shape.elasticity = 0.9
    shape.friction = 3
    space.add(body, shape)
    return body

def add_pendel(plane, ball_pos, pin_pos):
    ball = add_ball(*ball_pos, 20)
    con = pymunk.constraints.PinJoint(plane, ball, pin_pos)
    space.add(con)


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        self.time = 0
        self.ball = add_ball(200, 500, 50)
        self.plane = add_plane(0, 80, 800, 50, 5)
        add_pendel(self.plane, (400, 250), (400, 350))

    def on_draw(self):
        arcade.start_render()
        for shape in space.shapes:
            if isinstance(shape, pymunk.Circle): # pymunk.Circle
                pos = shape.body.position  # pymunk.Circle
                ang = shape.body.angle
                r = shape.radius
                arcade.draw_circle_outline(*pos, r, arcade.color.WHITE)
                vec = pymunk.Vec2d(r, 0).rotated(ang)
                arcade.draw_line(*pos, *(pos + vec), arcade.color.WHITE)
            if isinstance(shape, pymunk.Segment): # pymunk.Segment
                a = shape.a
                b = shape.b
                arcade.draw_line(*a, *b, arcade.color.WHITE)

        for con in space.constraints:
            if isinstance(con, pymunk.constraints.PinJoint):  # pymunk.constraints.PinJoint
                anchor = con.anchor_a
                pos = con.b.position
                arcade.draw_line(*anchor, *pos, color=arcade.color.WHITE)

    def on_update(self, delta_time: float):
        self.time += delta_time
        space.step(1/60)
        if self.time > 15:
            self.time = 0
            self.ball.position = 200, 500
            self.ball.velocity = 0, 0


game = Game()
arcade.run()