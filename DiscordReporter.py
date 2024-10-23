from neat import reporting
from neat.math_util import mean, stdev
import time
import requests
import json
import Private


class DiscordReporter(reporting.BaseReporter):
    def __init__(self, username="SageTrainer"):
        self.username = username
        self.generation = None
        self.generation_start_time = None
        self.generation_times = []
        self.num_extinctions = 0

    def _report_to_discord(self, message):
        requests.post(
            Private.DISCORD_WEBHOOK,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"username": self.username, "content": message}),
        )

    def start_generation(self, generation):
        self.generation = generation
        self.generation_start_time = time.time()

    def end_generation(self, config, population, species_set):
        elapsed = time.time() - self.generation_start_time
        self.generation_times.append(elapsed)
        self.generation_times = self.generation_times[-10:]
        average = sum(self.generation_times) / len(self.generation_times)
        self._report_to_discord("Total extinctions: {0:d}".format(self.num_extinctions))
        if len(self.generation_times) > 1:
            self._report_to_discord(
                "Generation time: {0:.3f} sec ({1:.3f} average)".format(
                    elapsed, average
                )
            )
        else:
            self._report_to_discord("Generation time: {0:.3f} sec".format(elapsed))

    def post_evaluate(self, config, population, species, best_genome):
        fitnesses = [c.fitness for c in population.values()]
        fit_mean = mean(fitnesses)
        fit_std = stdev(fitnesses)
        self._report_to_discord(
            f"**Generation {self.generation} complete**\n"
            + "\nPopulation's average fitness: {0:.5f} stdev: {1:.5f}".format(
                fit_mean, fit_std
            )
            + "\nBest fitness: {0:.5f}".format(best_genome.fitness)
        )

    def complete_extinction(self):
        self.num_extinctions += 1
        self._report_to_discord("All species extinct.")

    def found_solution(self, config, generation, best):
        self._report_to_discord(
            "Best individual in generation {0} meets fitness threshold - complexity: {1!r}".format(
                self.generation, best.size()
            )
        )

    def species_stagnant(self, sid, species):
        self._report_to_discord(
            "Species {0} with {1} members is stagnated: removing it".format(
                sid, len(species.members)
            )
        )
