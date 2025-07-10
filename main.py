import pygame
import sys
import os

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 1000, 600
FPS = 60
PLAYER_SPEED = 4
BALL_SPEED = 4
SCORE_LIMIT = 1
BALL_FRICTION = 1.00
BOUNCE_FACTOR = 1.00
GOAL_WIDTH = 100

# --- Screen ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2-Player Soccer Pong")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)

# --- Load Assets ---
def load_image(name, size=(60, 60)):
    return pygame.transform.scale(pygame.image.load(os.path.join("assets", name)), size)

characters = ["char1.png", "char2.png", "char3.png", "char4.png"]
stadiums = {"grass": "background_grass.jpg"}

background_img = pygame.transform.scale(pygame.image.load(os.path.join("assets", stadiums["grass"])), (WIDTH, HEIGHT))
main_menu_img = pygame.transform.scale(pygame.image.load(os.path.join("assets", "main_menu_bg.jpg")), (WIDTH, HEIGHT))
red_win_img = pygame.transform.scale(pygame.image.load(os.path.join("assets", "red_wins.jpg")), (WIDTH, HEIGHT))
blue_win_img = pygame.transform.scale(pygame.image.load(os.path.join("assets", "blue_wins.jpg")), (WIDTH, HEIGHT))

pygame.mixer.music.load(os.path.join("assets", "music.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

hit_sound = pygame.mixer.Sound(os.path.join("assets", "kick.mp3"))
hit_sound.set_volume(0.6)
goal_sound = pygame.mixer.Sound(os.path.join("assets", "goal_cheer.mp3"))
goal_sound.set_volume(0.7)

# --- Game State ---
game_state = "menu"
winner = None
player1_char = None
player2_char = None
selected = {"player1": False, "player2": False}
score = {"player1": 0, "player2": 0}
goal_text_timer = 0

# --- Button Drawing ---
def draw_button(text, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    pygame.draw.rect(screen, active_color if x + w > mouse[0] > x and y + h > mouse[1] > y else inactive_color, (x, y, w, h))
    if click[0] == 1 and x + w > mouse[0] > x and y + h > mouse[1] > y and action:
        action()
    text_surf = font.render(text, True, (0, 0, 0))
    screen.blit(text_surf, (x + (w - text_surf.get_width()) // 2, y + (h - text_surf.get_height()) // 2))

# --- Reset Function ---
def reset_game():
    global score, game_state, winner, goal_text_timer
    score = {"player1": 0, "player2": 0}
    ball.reset()
    player1.rect.center = player1_start_pos
    player2.rect.center = player2_start_pos
    winner = None
    goal_text_timer = 0
    game_state = "play"

def go_to_menu():
    global game_state, selected, player1_char, player2_char, score, goal_text_timer
    game_state = "menu"
    selected = {"player1": False, "player2": False}
    player1_char = None
    player2_char = None
    score = {"player1": 0, "player2": 0}
    goal_text_timer = 0

# --- Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.controls = controls
        self.prev_pos = self.rect.center

    def update(self):
        self.prev_pos = self.rect.center
        keys = pygame.key.get_pressed()
        if keys[self.controls['up']]: self.rect.y -= PLAYER_SPEED
        if keys[self.controls['down']]: self.rect.y += PLAYER_SPEED
        if keys[self.controls['left']]: self.rect.x -= PLAYER_SPEED
        if keys[self.controls['right']]: self.rect.x += PLAYER_SPEED
        self.rect.clamp_ip(screen.get_rect())

    def velocity(self):
        dx = self.rect.centerx - self.prev_pos[0]
        dy = self.rect.centery - self.prev_pos[1]
        return pygame.Vector2(dx, dy)

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("soccer_ball.png", size=(40, 40))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.vel = pygame.Vector2(0, 0)

    def update(self):
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        self.vel *= BALL_FRICTION
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vel.y = -self.vel.y * BOUNCE_FACTOR
        if self.rect.left <= 0 and HEIGHT * 0.25 <= self.rect.centery <= HEIGHT * 0.75:
            return "player2"
        if self.rect.right >= WIDTH and HEIGHT * 0.25 <= self.rect.centery <= HEIGHT * 0.75:
            return "player1"
        return None

    def apply_force(self, force):
        self.vel += force

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.vel = pygame.Vector2(0, 0)

# --- Setup ---
player1_start_pos = (80, HEIGHT // 2)
player2_start_pos = (WIDTH - 80, HEIGHT // 2)
ball = Ball()

# --- Main Loop ---
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if game_state == "menu":
        screen.blit(main_menu_img, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
       
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_state = "select_characters"

    elif game_state == "select_characters":
        screen.fill((50, 50, 50))
        title = font.render("Player 1: Left Click | Player 2: Right Click", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        spacing = 200
        for i, char_file in enumerate(characters):
            img = load_image(char_file, size=(80, 80))
            x = 150 + i * spacing
            y = HEIGHT // 2
            screen.blit(img, (x, y))
            rect = pygame.Rect(x, y, 80, 80)
            click = pygame.mouse.get_pressed()
            if rect.collidepoint(pygame.mouse.get_pos()):
                if click[0] and not selected["player1"]:
                    player1_char = load_image(char_file, size=(80, 80))
                    selected["player1"] = True
                elif click[2] and not selected["player2"]:
                    flipped_img = pygame.transform.flip(load_image(char_file, size=(80, 80)), True, False)
                    player2_char = flipped_img
                    selected["player2"] = True
        if selected["player1"] and selected["player2"]:
            player1 = Player(*player1_start_pos, {
                'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d
            }, player1_char)
            player2 = Player(*player2_start_pos, {
                'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT
            }, player2_char)
            players = pygame.sprite.Group(player1, player2)
            ball_group = pygame.sprite.Group(ball)
            game_state = "play"

    elif game_state == "play":
        screen.blit(background_img, (0, 0))
        pygame.draw.rect(screen, (0, 0, 255), (0, HEIGHT * 0.25, 10, HEIGHT * 0.5))
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 10, HEIGHT * 0.25, 10, HEIGHT * 0.5))
        players.update()
        scorer = ball.update()
        if scorer:
            score[scorer] += 1
            goal_sound.play()
            goal_text_timer = 120
            ball.reset()
            player1.rect.center = player1_start_pos
            player2.rect.center = player2_start_pos
        for player in [player1, player2]:
            if pygame.sprite.collide_rect(ball, player):
                direction = pygame.Vector2(ball.rect.center) - pygame.Vector2(player.rect.center)
                if direction.length() == 0:
                    direction = pygame.Vector2(1, 0)
                direction = direction.normalize() * BALL_SPEED
                ball.apply_force(direction + player.velocity())
                hit_sound.play()
        players.draw(screen)
        ball_group.draw(screen)
        score_text = font.render(f"Blue: {score['player1']}   Red: {score['player2']}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 - 150, 20))
        if goal_text_timer > 0:
            goal_text = font.render("Goal!", True, (255, 255, 0))
            screen.blit(goal_text, (WIDTH // 2 - goal_text.get_width() // 2, HEIGHT // 2 - 100))
            goal_text_timer -= 1
        if score['player1'] >= SCORE_LIMIT:
            winner = "Blue"
            game_state = "game_over"
        elif score['player2'] >= SCORE_LIMIT:
            winner = "Red"
            game_state = "game_over"

    elif game_state == "game_over":
        screen.blit(blue_win_img if winner == "Blue" else red_win_img, (0, 0))
        draw_button("Restart", WIDTH // 2 - 330, HEIGHT // 2, 700, 100, (100, 200, 100), (150, 255, 150), reset_game)
        draw_button("Quit", WIDTH // 2 - 330, HEIGHT // 2 + 130, 700, 100, (200, 100, 100), (255, 150, 150), go_to_menu)

    pygame.display.flip()

pygame.quit()
sys.exit()