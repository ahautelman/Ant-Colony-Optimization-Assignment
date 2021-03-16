import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import matplotlib.pyplot as plt
import time
import math
from src.Maze import Maze
from src.PathSpecification import PathSpecification
from src.Ant import Ant
from src.Coordinate import Coordinate


def find_shortest(routes):
    if not routes:
        raise BrokenPipeError("no routes found!")
    shortest = routes.__getitem__(0)
    for route in routes:
        if not shortest.shorter_than(route):
            shortest = route
    return shortest


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

    # Loop that starts the shortest path process
    # @param spec Spefication of the route we wish to optimize
    # @return ACO optimized route
    def find_shortest_route(self, path_specification):
        for g in range(self.generations):
            # if self.generations_since_best > self.stopping_cri:
            #     break
            self.gen_of_ants(path_specification)
        return self.best_route

    # Creates given amount of ants, finds their routes and updates the pheromone matrix

    def get_route(self, path_specification):
        return Ant(self.maze, path_specification).find_route()

    def gen_of_ants(self, path_specification):
        routes = []
        for n in range(self.ants_per_gen):
            ant = Ant(self.maze, path_specification)
            routes.append(ant.find_route())
        self.maze.evaporate(self.evaporation)
        self.maze.add_pheromone_routes(routes, self.q, path_specification.start)
        shortest_route = find_shortest(routes)

        sum = 0
        for i in routes:
            sum += i.size()

        self.avg_per_gens.append(sum / len(routes))
        self.best_per_gens.append(shortest_route.size())
        if shortest_route.size() < self.best_route_size:
            self.best_route = shortest_route
            self.generations_since_best = 0
            self.best_route_size = shortest_route.size()
        else:
            self.generations_since_best += 1
        print("best of the generation:", shortest_route.size(), "current best:", self.best_route_size)
        return routes


# Driver function for Assignment 1
if __name__ == "__main__":
    # parameters
    # easy - 38
    # medium best - 125
    # hard best - 799
    gen = 20
    no_gen = 400
    q = 500
    evap = 0.175
    stopping_criteria = 10

    # construct the optimization objects
    maze = Maze.create_maze("./../data/medium maze.txt")
    maze.set_initialization_pheromone(1)
    coord = Coordinate(4, 0)
    spec = PathSpecification.read_coordinates("./../data/medium coordinates.txt")
    aco = AntColonyOptimization(maze, gen, no_gen, q, evap, stopping_criteria)

    # save starting time
    start_time = int(round(time.time() * 1000))

    # run optimization
    shortest_route = aco.find_shortest_route(spec)

    # print time taken
    print("Time taken: " + str((int(round(time.time() * 1000)) - start_time) / 1000.0))

    plt.plot([i for i in range(no_gen)], aco.avg_per_gens, color='blue')
    plt.plot([i for i in range(no_gen)], aco.best_per_gens, color='red')
    plt.title("Parameters: " + "Q: " + str(q) + ", ants per gen: " + str(gen) + ", evaporation: " + str(evap))
    plt.ylabel('length of path')
    plt.xlabel('generations')
    plt.legend(["average length", "shortest length"])
    plt.show()

    # save solution
    shortest_route.write_to_file("./../data/medium solution.txt")

    # print route size
    print("Route size: " + str(shortest_route.size()))
