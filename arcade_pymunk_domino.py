import arcade
import pymunk

class ArcadeOptions(pymunk.SpaceDebugDrawOptions):
    def __init__(self):
        self.arcade = arcade
        super().__init__()

    def draw_circle(self, pos, angle, radius, outline_color, fill_color):
        arcade.draw_circle_outline(*pos, radius, color=arcade.color.WHITE)
        v = pymunk.Vec2d(radius, 0).rotated(angle)
        arcade.draw_line(pos.x, pos.y, pos.x + v.x, pos.y + v.y, arcade.color.WHITE)

    def draw_segment(self, a, b, color):
        arcade.draw_line(a.x, a.y, b.x, b.y, color=arcade.color.BLUE)

    def draw_fat_segment(self, a, b, radius, outline_color, fill_color):
        arcade.draw_line(a[0], a[1], b[0], b[1], color=arcade.color.WHITE)

    def draw_dot(self, size, pos, color):
        arcade.draw_circle_filled(*pos, size, arcade.color.RED)

    def draw_polygon(self, verts, radious, color1, color2):
        arcade.draw_polygon_outline(verts, arcade.color.WHITE)



options = ArcadeOptions()

space = pymunk.Space()
space.gravity = 0, -1000


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
    shape = pymunk.Segment(space.static_body, (x0, y0), (x1, y1), r)
    shape.elasticity = 0.9
    shape.friction = 3
    space.add(shape)

def add_rect(pos, wh, r):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Poly.create_box(body, wh, r)
    shape.density = 1
    shape.friction = 3
    space.add(shape, body)


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        add_plane(0, 50, 1000, 50, 5)
        add_plane(0, 150, 100, 150, 5)
        self.ball = add_ball(80, 220, 20)
        for x in range(200, 800, 105):
            add_rect(pos=(x, 100), wh=(15, 200), r=5)


    def on_draw(self):
        arcade.start_render()
        space.debug_draw(options)


    def on_key_press(self, symbol, modifiers):
        self.ball.velocity = 200, 150

    def on_update(self, dt):
        space.step(1 / 60)


game = Game()
arcade.run()