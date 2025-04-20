import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Game configuration
WIDTH, HEIGHT = 400, 600
FPS = 60

# Colors
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# Sprite class
class Sprite(pygame.sprite.Sprite):
    def __init__(self, type, w, h, sx, sy, x, y, gy, col, friction_x=0.05):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((w, h))
        self.image.fill(col)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.width = w
        self.height = h
        self.speed_x = sx
        self.speed_y = sy
        self.gravity_y = gy
        self.gravity_x = 0
        self.color = col
        self.friction_x = friction_x
        self.friction_y = 0
        self.age = 0
        self.active = True
        self.last_bounce = 0
    
    def update(self):
        # Update position based on speed and gravity
        self.speed_x = (self.speed_x + self.gravity_x) * (1 - self.friction_x)
        self.speed_y += self.gravity_y
        self.rect.x = (self.rect.x + self.speed_x) % WIDTH
        self.rect.y += self.speed_y
        self.age += 1

        if self.type == "papi":
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
                self.speed_y = 0  # Stop vertical movement when hitting the bottom

        if self.type == "jump":
            if self.rect.top > HEIGHT:
                self.kill()

# Game class
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Papi Jump")
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.level = 1
        self.best_score = 0
        self.sprites = pygame.sprite.Group()
        self.jumps = pygame.sprite.Group()
        self.papi = None
        self.is_game_over = False
        self.init_game()

    def init_game(self):
        self.score = 0
        self.level = 1
        self.sprites.empty()
        self.jumps.empty()
        self.is_game_over = False
        # Add initial "Papi" sprite
        self.papi = Sprite("papi", 30, 30, 0, 0, WIDTH // 2, HEIGHT - 100, 0.2, RED)
        self.sprites.add(self.papi)
        # Add initial jump platform at the center
        self.spawn_jump(HEIGHT - 50, centered=True)
        # Add more jump platforms
        for y in range(HEIGHT - 150, 0, -100):
            self.spawn_jump(y)
        # Initial jump
        self.papi.speed_y = -10
    
    def spawn_jump(self, height, centered=False):
        width = random.randint(40, 60)
        if centered:
            x = (WIDTH - width) // 2
        else:
            x = random.randint(0, WIDTH - width)
        jump = Sprite("jump", width, 10, 0, 1, x, height, 0, GREEN)
        self.jumps.add(jump)
        self.sprites.add(jump)
    
    def update_game(self):
        if not self.is_game_over:
            self.sprites.update()
            
            # Check for collisions
            hits = pygame.sprite.spritecollide(self.papi, self.jumps, False)
            if hits:
                for hit in hits:
                    if self.papi.speed_y > 0 and self.papi.rect.bottom <= hit.rect.bottom:
                        self.papi.rect.bottom = hit.rect.top
                        self.papi.speed_y = -10
                        self.score += 1
            else:
                # Check if Papi is falling and not on any platform
                if self.papi.speed_y > 0 and self.papi.rect.bottom >= HEIGHT:
                    self.is_game_over = True

            # Spawn new jumps
            if len(self.jumps) < 6:
                self.spawn_jump(0)

            # Move camera (scroll game world)
            if self.papi.rect.top <= HEIGHT / 3:
                scroll_speed = 3
                self.papi.rect.y += scroll_speed
                for jump in self.jumps:
                    jump.rect.y += scroll_speed

            # Remove off-screen jumps
            for jump in self.jumps:
                if jump.rect.top > HEIGHT:
                    jump.kill()
    
    def draw_game(self):
        self.screen.fill(WHITE)
        self.sprites.draw(self.screen)
        self.draw_score()
        if self.is_game_over:
            self.draw_game_over()
    
    def draw_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score} Level: {self.level}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

    def draw_game_over(self):
        font = pygame.font.Font(None, 48)
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press SPACE to restart", True, BLACK)
        self.screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        self.screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

    def restart_game(self):
        self.init_game()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.is_game_over:
                        self.restart_game()

            keys = pygame.key.get_pressed()
            if not self.is_game_over:
                if keys[pygame.K_LEFT]:
                    self.papi.speed_x = -5
                elif keys[pygame.K_RIGHT]:
                    self.papi.speed_x = 5
                else:
                    self.papi.speed_x = 0

            self.update_game()
            self.draw_game()
            pygame.display.flip()
        pygame.quit()

# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()
