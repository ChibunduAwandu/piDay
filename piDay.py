import pygame
import sys
from random import randint, uniform, choice
import math
def iterative_f(n):
    result = 0
    for i in range(n, 0, -1):  # Start from n down to 1
        result += 1 / (i * (4 * i - 1) * (4 * i - 2))
    return result

def iterative_g(n):
    result = 0
    for i in range(n, 0, -1):  # Start from n down to 1
        result += 1 / (i * (4 * i + 1) * (4 * i + 2))
    return result

# Calculate the result for f(2024) and g(2024) using the iterative approach
F_iterative = iterative_f(2024)
G_iterative = iterative_g(2024)

# Calculate the final result
result = F_iterative + 3 - G_iterative
# Initialize Pygame
pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Pi Celebration with Fireworks')
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font_pi = pygame.font.SysFont('Arial', 144, bold=True)
font_result = pygame.font.SysFont('Arial', 48, bold=True)
vector2 = pygame.math.Vector2
trails = []
fade_p = []
# pop_sound = pygame.mixer.Sound("")
# general
GRAVITY_FIREWORK = vector2(0, 0.3)
GRAVITY_PARTICLE = vector2(0, 0.07)
DISPLAY_WIDTH = DISPLAY_HEIGHT = 800
BACKGROUND_COLOR = (20, 20, 30)
# firework
FIREWORK_SPEED_MIN = 17
FIREWORK_SPEED_MAX = 20
FIREWORK_SIZE = 5
# particle
PARTICLE_LIFESPAN = 70
X_SPREAD = 0.8
Y_SPREAD = 0.8
PARTICLE_SIZE = 4
MIN_PARTICLES = 100
MAX_PARTICLES = 200
X_WIGGLE_SCALE = 20  # higher -> less wiggle
Y_WIGGLE_SCALE = 10
EXPLOSION_RADIUS_MIN = 10
EXPLOSION_RADIUS_MAX = 25
COLORFUL = True
# trail
TRAIL_LIFESPAN = PARTICLE_LIFESPAN / 2
TRAIL_FREQUENCY = 10  # higher -> less trails
TRAILS = True
# Firework settings
# ... [Keep the firework class settings as they are]
class Firework:
    def __init__(self):
        self.colour = tuple(randint(0, 255) for _ in range(3))
        self.colours = tuple(tuple(randint(0, 255) for _ in range(3)) for _ in range(3))
        # Creates the firework particle
        self.firework = Particle(randint(0, DISPLAY_WIDTH), DISPLAY_HEIGHT, True, self.colour)
        self.exploded = False
        self.particles = []

    def update(self, win: pygame.Surface) -> None:
        # method called every frame
        if not self.exploded:
            self.firework.apply_force(GRAVITY_FIREWORK)
            self.firework.move()
            self.show(win)
            if self.firework.vel.y >= 0:
                self.exploded = True
                self.explode()
                # play the pop sound when the firework explodes
                # pop_sound.play()

        else:
            for particle in self.particles:
                particle.update()
                particle.show(win)

    def explode(self):
        # when the firework has entered a stand still, create the explosion particles
        amount = randint(MIN_PARTICLES, MAX_PARTICLES)
        if COLORFUL:
            self.particles = [Particle(self.firework.pos.x, self.firework.pos.y, False, choice(self.colours)) for _ in
                              range(amount)]
        else:
            self.particles = [Particle(self.firework.pos.x, self.firework.pos.y, False, self.colour) for _ in
                              range(amount)]

    def show(self, win: pygame.Surface) -> None:
        # draw the firework on the given surface
        x = int(self.firework.pos.x)
        y = int(self.firework.pos.y)
        pygame.draw.circle(win, self.colour, (x, y), self.firework.size)

    def remove(self) -> bool:
        if not self.exploded:
            return False

        for p in self.particles:
            if p.remove:
                self.particles.remove(p)

        # remove the firework object if all particles are gone
        return len(self.particles) == 0


class Particle(object):
    def __init__(self, x, y, firework, colour):
        self.firework = firework
        self.pos = vector2(x, y)
        self.origin = vector2(x, y)
        self.acc = vector2(0, 0)
        self.remove = False
        self.explosion_radius = randint(EXPLOSION_RADIUS_MIN, EXPLOSION_RADIUS_MAX)
        self.life = 0
        self.colour = colour
        self.trail_frequency = TRAIL_FREQUENCY + randint(-3, 3)

        if self.firework:
            self.vel = vector2(0, -randint(FIREWORK_SPEED_MIN, FIREWORK_SPEED_MAX))
            self.size = FIREWORK_SIZE
        else:
            # set random position of particle
            self.vel = vector2(uniform(-1, 1), uniform(-1, 1))
            self.vel.x *= randint(7, self.explosion_radius + 2)
            self.vel.y *= randint(7, self.explosion_radius + 2)
            self.size = randint(PARTICLE_SIZE - 1, PARTICLE_SIZE + 1)
            # update pos and remove particle if outside radius
            self.move()
            self.outside_spawn_radius()

    def update(self):
        if self.remove:
            return

        # update particle position
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        # check if particle is out of screen
        if self.pos.y > DISPLAY_HEIGHT:
            self.remove = True

        # add particle to trails list
        if TRAILS and self.life % self.trail_frequency == 0:
            trails.append((int(self.pos.x), int(self.pos.y)))

        # add particle to faded particles list
        if self.life > PARTICLE_LIFESPAN // 2:
            fade_p.append((int(self.pos.x), int(self.pos.y), self.colour, self.size))

        self.life += 1

    def apply_force(self, force: pygame.math.Vector2) -> None:
        self.acc += force

    def outside_spawn_radius(self) -> bool:
        # if the particle spawned is outside of the radius that creates the circular firework, remov it
        distance = math.sqrt((self.pos.x - self.origin.x) ** 2 + (self.pos.y - self.origin.y) ** 2)
        return distance > self.explosion_radius

    def move(self) -> None:
        # called every frame, moves the particle
        if not self.firework:
            self.vel.x *= X_SPREAD
            self.vel.y *= Y_SPREAD

        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        self.decay()

    def show(self, win: pygame.Surface) -> None:
        # draw the particle on to the surface
        x = int(self.pos.x)
        y = int(self.pos.y)
        pygame.draw.circle(win, self.colour, (x, y), self.size)

    def decay(self) -> None:
        # random decay of the particles
        if self.life > PARTICLE_LIFESPAN:
            if randint(0, 15) == 0:
                self.remove = True
        # if too old, begone
        if not self.remove and self.life > PARTICLE_LIFESPAN * 1.5:
            self.remove = True


class Trail(Particle):
    def __init__(self, x, y, is_firework, colour, parent_size):
        Particle.__init__(self, x, y, is_firework, colour)
        self.size = parent_size - 1

    def decay(self) -> bool:
        # decay also changes the color on the trails
        # returns true if to be removed, else false
        self.life += 1
        if self.life % 100 == 0:
            self.size -= 1

        self.size = max(0, self.size)
        # static yellow-ish colour self.colour = (255, 255, 220)
        self.colour = (min(self.colour[0] + 5, 255), min(self.colour[1] + 5, 255), min(self.colour[2] + 5, 255))

        if self.life > TRAIL_LIFESPAN:
            ran = randint(0, 15)
            if ran == 0:
                return True
        # if too old, begone
        if not self.remove and self.life > TRAIL_LIFESPAN * 1.5:
            return True

        return False


def update(win: pygame.Surface, fireworks: list, trails: list) -> None:
    if TRAILS:
        for t in trails:
            t.show(win)
            if t.decay():
                trails.remove(t)

    for fw in fireworks:
        fw.update(win)
        if fw.remove():
            fireworks.remove(fw)

    pygame.display.update()
# Function to render the Pi symbol with changing colors
# ...

# Function to render the Pi symbol with changing colors
def render_pi(font, screen):
    pi_symbol = 'π'
    color = (randint(0, 255), randint(0, 255), randint(0, 255))
    text_surface = font.render(pi_symbol, True, color)
    rect = text_surface.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 40))
    screen.blit(text_surface, rect)

# Function to render the approximation of Pi
def render_result(text, font, screen):
    text_surface = font.render(text, True, (255, 255, 255))
    rect = text_surface.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 40))
    screen.blit(text_surface, rect)

# ...

# Main function to run the fireworks show and display Pi
def main():
    fireworks = [Firework() for _ in range(1)]
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)

        # Update and draw fireworks
        for fw in fireworks:
            fw.update(screen)
            if fw.remove():
                fireworks.remove(fw)

        if randint(0, 70) == 1:  # Random chance to create a new firework
            fireworks.append(Firework())

        # Render the Pi symbol and result at the center of the screen
        render_pi(font_pi, screen)
        render_result(f'Approximation of Pi: {result:.10f}', font_result, screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

# Run the program
main()

