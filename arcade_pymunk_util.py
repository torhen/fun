import pymunk
import arcade

class ArcadeOptions(pymunk.SpaceDebugDrawOptions):
    def __init__(self):
        self.arcade = arcade
        super().__init__()

    def draw_circle(self, pos, angle, radius, outline_color, fill_color):
        arcade.draw_circle_outline(*pos, radius, color=arcade.color.WHITE)
        v = pymunk.Vec2d(radius, 0).rotated(angle)
        arcade.draw_line(pos.x, pos.y, pos.x + v.x, pos.y + v.y, arcade.color.WHITE)

    def draw_segment(self, a, b, color):
        arcade.draw_line(a[0], a[1], b[0], b[1], color=arcade.color.RED, line_width=10)

    def draw_fat_segment(self, a, b, radius, outline_color, fill_color):
        arcade.draw_line(a[0], a[1], b[0], b[1], color=arcade.color.WHITE)


class App(arcade.Window):
    def __init__(self):
        super().__init__()
        self.options = ArcadeOptions()

    def on_draw(self):
        arcade.start_render()
        space.debug_draw(self.options)  # pymunk.Space

    def on_update(self, dt):
        space.step(dt)


def main():
    global space
    space = pymunk.Space()
    space.gravity = 0, -500

    body = pymunk.Body()
    body.position = 100, 300
    shape = pymunk.Circle(body, radius=50)
    shape.density = 1
    shape.friction = 3
    shape.elasticity = 0.9
    space.add(body, shape)

    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (0, 100), (800, 50), 5)
    shape.elasticity = 0.9
    shape.friction = 3
    space.add(body, shape)

    app = App()
    arcade.run()


if __name__ == '__main__':
    main()