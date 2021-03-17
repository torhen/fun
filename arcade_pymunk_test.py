import arcade
import pymunk

space = pymunk.Space()      # Create a Space which contain the simulation
space.gravity = 0, -1000     # Set its gravity

body = pymunk.Body(1, 1666)  # Create a Body with mass and moment
body.position = 100, 500      # Set the position of the body

shape = pymunk.Circle(body, 20) # Create a box shape and attach to body
shape.elasticity = 0.8
space.add(body, shape)       # Add both body and shape to the simulation

segment_body = pymunk.Body(body_type=pymunk.Body.STATIC)
segment_shape = pymunk.Segment(segment_body, (0, 100), (800, 50), 5)
segment_shape.elasticity = 0.8
space.add(segment_body, segment_shape)


class Game(arcade.Window):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.LIGHT_GRAY)
        self.x = 0
        self.y = 0

    def on_draw(self):
        arcade.start_render()
        arcade.draw_circle_filled(self.x, self.y, 20, color=arcade.color.RED)
        arcade.draw_line(0, 100, 800, 50, color=arcade.color.BLUE)

    def on_update(self, delta_time):
        space.step(delta_time)
        pos = body.position
        self.x = pos.x
        self.y = pos.y


game = Game()
arcade.run()