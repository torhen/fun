import arcade
import pymunk

space = pymunk.Space()
space.gravity = 0, -1000


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
        for shape in space.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = shape.body.position
                r = shape.radius
                ang = shape.body.angle
                offset = shape.offset
                offset = offset.rotated(ang)
                pos = pos + offset
                arcade.draw_circle_outline(pos.x, pos.y, r, arcade.color.WHITE)
                peri = pymunk.Vec2d(0, r).rotated(ang)
                arcade.draw_line(pos.x, pos.y, pos.x + peri.x, pos.y + peri.y, arcade.color.WHITE)

            if isinstance(shape, pymunk.Segment):
                a, b = shape.a, shape.b
                arcade.draw_line(a.x, a.y, b.x, b.y, arcade.color.WHITE)

    def on_update(self, dt):
        self.time += 1/60
        if self.time > 9:
            self.time = 0
            self.ball.position = 100, 500
            self.ball.velocity = 0, 0
            self.ball.angular_velocity = 0
            self.ball.angle = 0
        space.step(1/60)


game = Game()
arcade.run()
