import arcade
import pymunk

space = pymunk.Space()
space.gravity = 0, -1000


class Ball:
    def __init__(self, space, x, y):
        self.body = pymunk.Body(1, 1000)
        self.body.position = x, y

        self.shape = pymunk.Circle(self.body, 20)
        self.shape.elasticity = 0.83
        space.add(self.body, self.shape)

    def draw(self):
        x, y = self.body.position
        r = self.shape.radius
        arcade.draw_circle_outline(x, y, r, color=arcade.color.WHITE)

    def set_pos(self, x, y):
        self.body.position = x, y


class Plane:
    def __init__(self, space, x0, y0, x1, y1):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, (x0, y0), (x1, y1), 5)
        self.shape.elasticity = 0.83
        space.add(self.body, self.shape)

    def draw(self):
        arcade.draw_line(self.x0, self.y0, self.x1, self.y1, color=arcade.color.WHITE)


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

        self.ball = Ball(space, 50, 600)
        self.plane1 = Plane(space, 0, 100, 800, 50)
        self.plane2 = Plane(space, 0, 50, 800, 85)

    def on_draw(self):
        arcade.start_render()
        self.ball.draw()
        self.plane1.draw()
        self.plane2.draw()

    def on_update(self, delta_time):
        space.step(delta_time)
        x, y = self.ball.body.position
        if x > 800:
            self.ball.body.position = 50, 600
            self.ball.body.velocity = 0, 0



game = Game()
arcade.run()