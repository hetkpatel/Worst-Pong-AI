import neat
from DiscordReporter import DiscordReporter
from game import PongGame, Player, MoveChoice
import pickle
from enum import Enum
import pygame


def test_ai(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    game = PongGame()
    while True:
        # Move Human Player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            game.update_paddles(Player.LEFT, MoveChoice.UP)
        if keys[pygame.K_DOWN]:
            game.update_paddles(Player.LEFT, MoveChoice.DOWN)

        # Move AI Player
        o2 = net.activate(
            (game.paddle2.y, game.ball.y, abs(game.paddle2.x - game.ball.x))
        )
        game.update_paddles(Player.RIGHT, MoveChoice(o2.index(max(o2))))

        game.loop()


def train_ai(genome1, genome2, config):
    net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
    net2 = neat.nn.FeedForwardNetwork.create(genome2, config)
    game = PongGame()
    while True:
        # Move AI 1
        option1 = net1.activate(
            (game.paddle1.y, game.ball.y, abs(game.paddle1.x - game.ball.x))
        )
        game.update_paddles(Player.LEFT, MoveChoice(option1.index(max(option1))))

        # Move AI 2
        option2 = net2.activate(
            (game.paddle2.y, game.ball.y, abs(game.paddle2.x - game.ball.x))
        )
        game.update_paddles(Player.RIGHT, MoveChoice(option2.index(max(option2))))

        if game.loop(True):
            genome1.fitness += game.left_hit
            genome2.fitness += game.right_hit
            break


def eval_genomes(genomes, config):
    for i, (_, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break

        genome1.fitness = 0
        for _, genome2 in genomes[i + 1 :]:
            genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
            train_ai(genome1, genome2, config)


def run(config_file, mode):
    # Load configuration.
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )

    match mode:
        case Mode.TRAIN:
            # Create the population, which is the top-level object for a NEAT run.
            p = neat.Population(config)  # New population
            # UNCOMMENT: Start from checkpoint generation
            # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
            # Add a stdout reporter to show progress in the terminal.
            p.add_reporter(neat.StdOutReporter(True))
            p.add_reporter(DiscordReporter(username="Worst-Pong-AI"))
            p.add_reporter(neat.StatisticsReporter())
            p.add_reporter(neat.Checkpointer(1, filename_prefix="gen-cp-"))

            # Train for up to 10 generations
            winner = p.run(eval_genomes, 10)

            with open("worst.pickle", "wb") as f:
                pickle.dump(winner, f)

        case Mode.TEST:
            with open("worst.pickle", "rb") as f:
                winner = pickle.load(f)
            test_ai(winner, config)


class Mode(Enum):
    TRAIN = 1
    TEST = 2


if __name__ == "__main__":
    # Change to Mode.TEST to test worst.pickle
    run("config", Mode.TRAIN)
