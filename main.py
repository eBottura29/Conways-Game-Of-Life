import pygame, random
from settings import *
from colors import *
from threading import Timer

# PyGame Setup
pygame.init()

SCREEN = (
    pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)
    if FULLSCREEN
    else pygame.display.set_mode(RESOLUTION)
)
pygame.display.set_caption(WINDOW_NAME)
clock = pygame.time.Clock()

# Font setup
roboto = pygame.font.SysFont("arial", 32)

# Grid and Simulation variables
squares = [[False for _ in range(GRID_X)] for _ in range(GRID_Y)]
generation_history = []
paused = True
sim_speed = 24
generation = 0
population = 0

color_scheme = "dark"


class Text:
    def __init__(
        self,
        text,
        font,
        color,
        position,
        anti_aliasing,
        background=False,
        bg_color=(0, 0, 0),
    ):
        self.text = text
        self.font = font
        self.color = color
        self.position = position
        self.anti_aliasing = anti_aliasing
        self.background = background
        self.bg_color = bg_color

    def draw(self, pos):
        rendered_text = (
            self.font.render(self.text, self.anti_aliasing, self.color, self.bg_color)
            if self.background
            else self.font.render(self.text, self.anti_aliasing, self.color)
        )
        text_rect = rendered_text.get_rect()
        setattr(text_rect, pos.lower(), self.position)
        SCREEN.blit(rendered_text, text_rect)


def draw_on_click(mouse_pos):
    grid_pos = mouse_pos[0] // GRID_SIZE, mouse_pos[1] // GRID_SIZE
    squares[grid_pos[1]][grid_pos[0]] = not squares[grid_pos[1]][grid_pos[0]]


def grid(color):
    for y in range(GRID_Y):
        for x in range(GRID_X):
            pygame.draw.rect(
                SCREEN,
                color,
                pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                GRID_WIDTH,
            )


def draw_squares(color):
    for y in range(GRID_Y):
        for x in range(GRID_X):
            if squares[y][x]:
                pygame.draw.rect(
                    SCREEN,
                    color,
                    pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                )


def check_neighbours(x, y):
    neighbours = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_X and 0 <= ny < GRID_Y and squares[ny][nx]:
                neighbours += 1
    return neighbours


def step_sim():
    global squares, generation_history
    new_squares = [[squares[y][x] for x in range(GRID_X)] for y in range(GRID_Y)]

    for y in range(GRID_Y):
        for x in range(GRID_X):
            alive = squares[y][x]
            neighbours = check_neighbours(x, y)

            if alive:
                new_squares[y][x] = 2 <= neighbours <= 3
            else:
                new_squares[y][x] = neighbours == 3

    generation_history.append(squares)  # Save the current state to history
    squares = new_squares


def revert_sim():
    global squares, generation, generation_history
    if generation_history:
        squares = generation_history.pop()  # Restore the last saved state
        generation -= 1


def advance_sim():
    global generation
    if not paused:
        generation += 1
        Timer(1 / sim_speed, advance_sim).start()
        step_sim()


def draw():
    if color_scheme.lower() == "dark":
        SCREEN.fill(BLACK)
        draw_squares(WHITE)
        grid((32, 32, 32))

        generation_text = Text(
            f"GENERATION: {generation}", roboto, WHITE, (30, 30), True, True
        )
        population_text = Text(
            f"POPULATION: {population}", roboto, WHITE, (30, 80), True, True
        )
    if color_scheme.lower() == "light":
        SCREEN.fill(WHITE)
        draw_squares(BLACK)
        grid((32, 32, 32))

        generation_text = Text(
            f"GENERATION: {generation}", roboto, BLACK, (30, 30), True, True, WHITE
        )
        population_text = Text(
            f"POPULATION: {population}", roboto, WHITE, (30, 80), True, True
        )

    generation_text.draw("topleft")
    population_text.draw("topleft")

    pygame.display.flip()


def main():
    global paused, generation, squares, population, generation_history

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    if not paused:
                        advance_sim()
                elif event.key == pygame.K_RIGHT:
                    generation += 1
                    step_sim()
                elif event.key == pygame.K_LEFT:
                    revert_sim()
                elif event.key == pygame.K_r:
                    squares = [
                        [random.choice([False, True]) for _ in range(GRID_X)]
                        for _ in range(GRID_Y)
                    ]
                elif event.key == pygame.K_c or event.key == pygame.K_BACKSPACE:
                    generation = 0
                    generation_history = []
                    squares = [[False for _ in range(GRID_X)] for _ in range(GRID_Y)]
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                draw_on_click(pygame.mouse.get_pos())

        population = 0
        for x in range(GRID_X):
            for y in range(GRID_Y):
                if squares[y][x]:
                    population += 1

        draw()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
