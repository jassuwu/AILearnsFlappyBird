# Import the modules of use
import pygame
import neat
import time
import os
import random


# VALUES TO PLAY AROUND WITH
CLOCK_TICKS = 60
PIPE_GAP = 200
GENERATION_COUNT = 10

# Window size
WIN_WIDTH = 600
WIN_HEIGHT = 900

# FONTS
pygame.font.init()
STAT_FONT = pygame.font.SysFont("consolas", 50)

# MIXER
pygame.mixer.init()
audio_path = os.path.join(os.path.dirname(__file__), "audio")
# pygame.mixer.music.load(os.path.join(audio_path, "ambience.mp3"))
POINT_SOUND = pygame.mixer.Sound(os.path.join(audio_path, "point.mp3"))
# pygame.mixer.music.set_volume(0.05)

# Initialze the pygame display
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("FlappyAI")


# Import the images with pygame
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird1.png"))),
               pygame.transform.scale2x(pygame.image.load(
                   os.path.join("images", "bird2.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird3.png")))]

PIPE_IMAGE = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "base.png")))
BG_IMAGE = pygame.transform.scale(pygame.image.load(
    os.path.join("images", "bg.png")).convert_alpha(), (600, 900))


class Bird:
    # Constants
    IMAGES = BIRD_IMAGES
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    # =============================================================================

    def __init__(self, x, y):
        self.x = x   # Position of the bird
        self.y = y  # Position of the bird
        self.tilt = 0  # Rotation of the bird
        self.tick_count = 0  # Equivalent of time
        self.vel = 0  # Velocity
        self.height = self.y  # For the displacement arc
        self.img_count = 0  # For the animation of the bird
        self.img = self.IMAGES[0]  # For the animation

    # =============================================================================
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    # =============================================================================
    def move(self):
        self.tick_count += 1

        # For the displacement arc (parabolic movement)
        # s = ut + 1/2at^2
        displacement = self.vel * (self.tick_count) + \
            1.5 * (self.tick_count)**2

        # Terminal velocity
        if displacement >= 16:
            displacement = 16

        # For the jump
        if displacement < 0:
            displacement -= 2

        # For displacing to the new y position
        self.y = self.y + displacement

        # For the rotation of the bird
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    # =============================================================================
    def draw(self, win):
        self.img_count += 1

        # For the animation of the bird (flapping wings)
        self.img = self.IMAGES[self.img_count // self.ANIMATION_TIME]
        self.img_count = self.img_count % len(self.IMAGES)

        # For the rotation of the bird (tilt)
        if self.tilt <= -80:
            self.img = self.IMAGES[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # =============================================================================
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

# =================================================================================


class Pipe:
    # Constants
    GAP = PIPE_GAP
    VEL = 5

    # =================================================================================
    def __init__(self, x):
        self.x = x  # Position of the pipe
        self.height = 0  # Height of the pipe
        self.gap = 100  # Gap between the pipes

        self.top = 0  # Top pipe
        self.bottom = 0  # Bottom pipe
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGE

        self.passed = False  # For the collision of the bird with the pipes
        self.set_height()

    # =================================================================================
    def set_height(self):
        self.height = random.randrange(50, 450)  # Height of the pipe
        self.top = self.height - self.PIPE_TOP.get_height()  # Top pipe
        self.bottom = self.height + self.GAP  # Bottom pipe

    # =================================================================================
    def move(self):
        # Reducing the x coordinate of the pipe based on the velocity of the pipe
        self.x -= self.VEL

    # =================================================================================
    def draw(self, win):
        # For the top pipe
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # For the bottom pipe
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # =================================================================================
    def collide(self, bird):
        # Collision of the bird with the pipes with pygame masks
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Point of collision of the bird with the bottom pipe
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        # Point of collision of the bird with the top pipe
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False

    # =================================================================================


class Base:
    # Constants
    VEL = 5
    WIDTH = BASE_IMAGE.get_width()
    IMG = BASE_IMAGE

    # =================================================================================
    def __init__(self, y):
        self.y = y  # Position of the base
        self.x1 = 0  # For the movement of the base
        self.x2 = self.WIDTH  # For the movement of the base

    # =================================================================================
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # For the movement of the base
        # We draw the base image twice and move it to the left
        # If the first image of the base is out of the screen then we move the second image to the front
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # =================================================================================
    def draw(self, win):
        # For the first image of the base
        win.blit(self.IMG, (self.x1, self.y))
        # For the second image of the base
        win.blit(self.IMG, (self.x2, self.y))

    # =================================================================================


def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMAGE, (0, 0))  # For the background image

    for pipe in pipes:  # For the pipes that come in as a list
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)  # For the base

    # For the birds that come in as a list
    for bird in birds:
        bird.draw(win)

    pygame.display.update()


def eval_genomes(genomes, config):

    # Start the music
    # pygame.mixer.music.play()

    # For the neural network
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    # Initial positions of the bird, and the base. The list of pipes.
    base = Base(730)  # For the initial position of the base (y)
    pipes = [Pipe(700)]  # For the initial position of the pipes (x)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    # For the score
    score = 0

    run = True
    while run:
        clock.tick(CLOCK_TICKS)  # 30 frames per second
        # pygame event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # For the bird to differentiate between the pipes
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break
        # Movement of the birds
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            # For the neural network output
            output = nets[x].activate((bird.y, abs(
                bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False  # For the addition of the pipes
        rem = []  # For the pipes that are out of the screen
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            # Check if the pipe is out of the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()

        if add_pipe:
            score += 1
            # Adding the fitness to all the birds when they pass the pipe
            pygame.mixer.Sound.play(POINT_SOUND)
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()

        # Draw after movement
        draw_window(win, birds, pipes, base, score)
    pygame.mixer.music.stop()


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, GENERATION_COUNT)

    print("Best genome: {0}".format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
