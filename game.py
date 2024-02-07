import pygame
import sys
import random
from enum import Enum
import math


class PongGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Constants
        self.WIDTH, self.HEIGHT = 800, 600
        self.PADDLE_WIDTH, self.PADDLE_HEIGHT = 10, 100
        self.BALL_SIZE = 15
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.FPS = 60  # Change to 0 for faster training

        # Fitness Metrics
        self.left_hit, self.right_hit = 0, 0

        # Create the screen
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pong")

        # Create paddles
        self.paddle1 = pygame.Rect(
            50,
            self.HEIGHT // 2 - self.PADDLE_HEIGHT // 2,
            self.PADDLE_WIDTH,
            self.PADDLE_HEIGHT,
        )
        self.paddle2 = pygame.Rect(
            self.WIDTH - 50 - self.PADDLE_WIDTH,
            self.HEIGHT // 2 - self.PADDLE_HEIGHT // 2,
            self.PADDLE_WIDTH,
            self.PADDLE_HEIGHT,
        )

        # Create the ball
        self.ball = pygame.Rect(
            self.WIDTH // 2 - self.BALL_SIZE // 2,
            self.HEIGHT // 2 - self.BALL_SIZE // 2,
            self.BALL_SIZE,
            self.BALL_SIZE,
        )

        # Scores
        self.score1 = 0
        self.score2 = 0

        # Create font
        self.font = pygame.font.Font(None, 50)

        # Create clock
        self.clock = pygame.time.Clock()

        # Initialize ball speed
        self.set_ball_speed()

    def set_ball_speed(self):
        self.ball_speed_x = random.choice([-1, 1]) * random.randint(1, 10)
        self.ball_speed_y = random.choice([-1, 1]) * random.randint(1, 10)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update_paddles(self, player, moveDir):
        if moveDir == 0:
            return

        # Player 1 controls
        if player == Player.LEFT and moveDir == MoveChoice.UP and self.paddle1.top > 0:
            self.paddle1.y -= 5
        if (
            player == Player.LEFT
            and moveDir == MoveChoice.DOWN
            and self.paddle1.bottom < self.HEIGHT
        ):
            self.paddle1.y += 5

        # Player 2 controls
        if player == Player.RIGHT and moveDir == MoveChoice.UP and self.paddle2.top > 0:
            self.paddle2.y -= 5
        if (
            player == Player.RIGHT
            and moveDir == MoveChoice.DOWN
            and self.paddle2.bottom < self.HEIGHT
        ):
            self.paddle2.y += 5

    def update_ball(self):
        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y

        # Collisions with walls
        if self.ball.top <= 0:
            self.ball.top = 0
            self.ball_speed_y = abs(self.ball_speed_y)
        elif self.ball.bottom >= self.HEIGHT:
            self.ball.bottom = self.HEIGHT
            self.ball_speed_y = -abs(self.ball_speed_y)

        if self.ball.left <= 0:
            self.score2 += 1
            self.set_ball_speed()
            self.ball.x = self.WIDTH // 2 - self.BALL_SIZE // 2
            self.ball.y = self.HEIGHT // 2 - self.BALL_SIZE // 2
        elif self.ball.right >= self.WIDTH:
            self.score1 += 1
            self.set_ball_speed()
            self.ball.x = self.WIDTH // 2 - self.BALL_SIZE // 2
            self.ball.y = self.HEIGHT // 2 - self.BALL_SIZE // 2

        # Collisions with paddles
        if self.ball.colliderect(self.paddle1) or self.ball.colliderect(self.paddle2):
            self.ball_speed_x = -self.ball_speed_x

            def _calculate_bounce_angle(self, paddle):
                relative_intersect_y = (paddle.y + paddle.height / 2) - self.ball.y
                normalized_intersect_y = relative_intersect_y / (paddle.height / 2)
                bounce_angle = normalized_intersect_y * (
                    5 * math.pi / 12
                )  # 75 degrees in radians
                return bounce_angle

            # Adjust the ball's direction based on which paddle it hits
            if self.ball.colliderect(self.paddle1):
                self.left_hit += 1
                self.ball_speed_y = 10 * -math.sin(
                    _calculate_bounce_angle(self=self, paddle=self.paddle1)
                )
            elif self.ball.colliderect(self.paddle2):
                self.right_hit += 1
                self.ball_speed_y = 10 * -math.sin(
                    _calculate_bounce_angle(self=self, paddle=self.paddle2)
                )

    def draw(self, train):
        # Clear the screen
        self.screen.fill(self.BLACK)

        # Draw paddles and ball
        pygame.draw.rect(self.screen, self.WHITE, self.paddle1)
        pygame.draw.rect(self.screen, self.WHITE, self.paddle2)
        pygame.draw.ellipse(self.screen, self.WHITE, self.ball)

        # Draw scores
        score_text = self.font.render(
            f"{self.score1} - {self.score2}", True, self.WHITE
        )
        self.screen.blit(
            score_text, (self.WIDTH // 2 - score_text.get_width() // 2, 20)
        )

        # Draw hit count for each paddle
        if train:
            hit_text1 = self.font.render(
                f"{self.left_hit}", True, pygame.Color(0, 225, 0)
            )
            hit_text2 = self.font.render(
                f"{self.right_hit}", True, pygame.Color(0, 225, 0)
            )
            self.screen.blit(
                hit_text1, (self.WIDTH // 2 - hit_text1.get_width() - 200, 20)
            )
            self.screen.blit(
                hit_text2, (self.WIDTH // 2 - hit_text2.get_width() + 200, 20)
            )

        # Update the display
        pygame.display.flip()

    def loop(self, train=False):
        self.handle_events()
        self.update_ball()
        self.draw(train)
        if self.FPS > 0:
            self.clock.tick(self.FPS)

        return (
            True
            if train
            and (
                self.score1 >= 1
                or self.score2 >= 1
                or self.left_hit > 50
                or self.right_hit > 50
            )
            else False
        )


class Player(Enum):
    LEFT = 1
    RIGHT = 2


class MoveChoice(Enum):
    STAY = 0
    UP = 1
    DOWN = 2


if __name__ == "__main__":
    game = PongGame()
    while True:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            game.update_paddles(Player.LEFT, MoveChoice.UP)
        if keys[pygame.K_s]:
            game.update_paddles(Player.LEFT, MoveChoice.DOWN)

        if keys[pygame.K_UP]:
            game.update_paddles(Player.RIGHT, MoveChoice.UP)
        if keys[pygame.K_DOWN]:
            game.update_paddles(Player.RIGHT, MoveChoice.DOWN)

        game.loop()
