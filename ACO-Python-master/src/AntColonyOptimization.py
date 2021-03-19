import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import time
import math
import multiprocessing
from contextlib import contextmanager
from src.Maze import Maze
from src.PathSpecification import PathSpecification
from src.Ant import Ant


# Method that returns the shortest route from a list of routes.
# @param route list of Route object.
def find_shortest(routes):
    if not routes:
        raise BrokenPipeError("no routes found!")
    shortest = routes.__getitem__(0)
    for route in routes:
        if not shortest.shorter_than(route):
            shortest = route
    return shortest


@contextmanager
def poolcontext(*args, **kwargs):
    """
    Method allows running functions in parallel.
    """
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()


# Class representing the first assignment. Finds shortest path between two points in a maze according to a specific
# path specification.
class AntColonyOptimization:

    # Constructs a new optimization object using ants.
    # @param maze the maze .
    # @param antsPerGen the amount of ants per generation.
    # @param generations the amount of generations.
    # @param Q normalization factor for the amount of dropped pheromone
    # @param evaporation the evaporation factor.
    def __init__(self, maze, ants_per_gen, generations, q, evaporation, stopping_cri):
        self.maze = maze
        self.ants_per_gen = ants_per_gen
        self.generations = generations
        self.q = q
        self.evaporation = evaporation
        self.best_route = None
        self.best_route_size = math.inf
        self.generations_since_best = 0
        self.stopping_cri = stopping_cri
        self.avg_per_gens = []
        self.best_per_gens = []

    def reset(self):
        self.maze.reset()
        self.best_route = None
        self.best_route_size = math.inf
        self.generations_since_best = 0
        self.avg_per_gens = []
        self.best_per_gens = []

    # Loop that starts the shortest path process
    # @param spec Spefication of the route we wish to optimize
    # @return ACO optimized route
    def find_shortest_route(self, path_specification):
        for g in range(self.generations):
            if self.generations_since_best > self.stopping_cri:     # stopping criterion.
                break
            self.gen_of_ants(path_specification)
        return self.best_route

    def get_route(self, path_specification):
        return Ant(self.maze, path_specification).find_route()

    def gen_of_ants(self, path_specification):
        with poolcontext(multiprocessing.cpu_count()) as pool:
            routes = pool.map(self.get_route, [path_specification for _ in range(self.ants_per_gen)])       # get list of routes for ants_per_gen ants.
        shortest_route = find_shortest(routes)
        if shortest_route.size() < self.best_route_size:    # found route is the new global best
            self.best_route = shortest_route        # update global best
            self.best_route_size = shortest_route.size()
            self.generations_since_best = 0
            for i in range(10):
                routes.append(shortest_route)       # add 10 times the normal amount of pheromone
        else:
            self.generations_since_best += 1
        for i in range(4):
            routes.append(shortest_route)           # add 5 times the normal amount of pheromone
                                                    # for the best route in generation.
        self.maze.evaporate(self.evaporation)       # evaporate pheromone
        self.maze.add_pheromone_routes(routes, self.q, path_specification.start)        # add pheromone for current generation.
        sum = 0
        for i in routes:
            sum += i.size()
        self.avg_per_gens.append(sum / len(routes))
        self.best_per_gens.append(shortest_route.size())
        print("best of the generation:", shortest_route.size(), "current best:", self.best_route_size)
        return routes


# Driver function for Assignment 1
if __name__ == "__main__":
    # parameters
    # easy best - 38
    # medium best - 125
    # hard maze - 797

    gen = 20
    no_gen = 500
    q = 500
    evap = 0.6
    stopping_criteria = 20

    # construct the optimization objects
    maze = Maze.create_maze("./../data/hard maze.txt")
    spec = PathSpecification.read_coordinates("./../data/hard coordinates.txt")
    aco = AntColonyOptimization(maze, gen, no_gen, q, evap, stopping_criteria)

    # save starting time
    start_time = int(round(time.time() * 1000))

    # run optimization
    shortest_route = aco.find_shortest_route(spec)

    # print time taken
    print("Time taken: " + str((int(round(time.time() * 1000)) - start_time) / 1000.0))

    # save solution
    shortest_route.write_to_file("./../data/hard solution.txt")

    # print route size
    print("Route size: " + str(shortest_route.size()))
