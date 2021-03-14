import copy
import os
import random
import sys

from src.Crossroad import Crossroad
from src.Direction import Direction
from src.Route import Route

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


# Method picks in which direction to move.
# @param probabilities list of probabilities for each position. The sum of probabilities should sum up to 1
# @param rand a randomly generated number in range [0, 1]
def roulette_wheel(probabilities, rand):
    # east corresponds to 0
    # N -> 1
    # W -> 2
    # S -> 3
    curr_prob_sum = probabilities[0]
    if rand < curr_prob_sum:
        return Direction.east
    curr_prob_sum += probabilities[1]
    if rand < curr_prob_sum:
        return Direction.north
    curr_prob_sum += probabilities[2]
    if rand < curr_prob_sum:
        return Direction.west
    return Direction.south


# Class that represents the ants functionality.
class Ant:  # TODO: clean up this spaghetti code

    # Constructor for ant taking a Maze and PathSpecification.
    # @param maze Maze the ant will be running in.
    # @param spec The path specification consisting of a start coordinate and an end coordinate.
    def __init__(self, maze, path_specification):
        self.maze = maze
        self.start = path_specification.get_start()
        self.end = path_specification.get_end()
        self.current_position = self.start
        self.rand = random
        self.tabu_list = []     # list of visited nodes.
        self.crossroads = []    # list of object of class Crossroad, stores the last encountered crossroad and the number of steps taken since.

    # Method that performs a single run through the maze by the ant.
    # @return The route the ant found through the maze.
    def find_route(self):
        route = Route(self.start)
        while self.current_position != self.end:
            self.tabu_list.append(self.current_position)                        # add current position to visited nodes
            surrounding_pheromone = self.maze.get_surrounding_pheromone(self.current_position)
            if self.is_crossroad(surrounding_pheromone):
                self.crossroads.append(Crossroad(self.current_position, 0))     # save node in crossroads stack
            self.pick_direction(route, surrounding_pheromone)                   # update current position and route
            self.update_crossroad()                                             # update the number of steps taken from last crossroad point.
        return route

    def find_final_route(self):
        route = Route(self.start)
        while self.current_position != self.end:
            self.tabu_list.append(self.current_position)                        # add current position to visited nodes
            surrounding_pheromone = self.maze.get_surrounding_pheromone(self.current_position)
            if self.is_crossroad(surrounding_pheromone):
                self.crossroads.append(Crossroad(self.current_position, 0))     # save node in crossroads stack
            self.pick_direction(route, surrounding_pheromone, False)                   # update current position and route
            self.update_crossroad()

    # Method checks whether a node is a crossroad (there a more than 1 possible directions to pick from).
    # @param surrounding_pheromone SurroundingPheromone containing the pheromone information around a certain point in the maze.
    def is_crossroad(self, surrounding_pheromone):
        directions = self.get_possible_directions(surrounding_pheromone)
        return len(directions) > 1

    # Method updates the current position and the route of the ant.
    # @param route Route describing the currently chosen route.
    # @param surrounding_pheromone SurroundingPheromone containing the pheromone information around a certain point in the maze.
    def pick_direction(self, route, surrounding_pheromone, r=True):
        pheromone_sum = surrounding_pheromone.get_total_surrounding_pheromone()  # sum of all the possible choices.
        directions = self.get_possible_directions(surrounding_pheromone)  # list containing possible directions.
        surrounding_pheromone = self.maze.get_surrounding_pheromone(self.current_position)
        if not directions:  # ant encountered a dead end.
            #print("deadend", self.current_position, surrounding_pheromone)
            if not self.crossroads:  # stack of crossroads is empty
                raise ValueError("Encountered dead end in maze!")
            crossroad = self.crossroads.pop()  # get last encountered crossroad
            self.current_position = crossroad.get_position()  # update position to that node
            for i in range(crossroad.get_steps()):
                route.pop()  # remove all picked directions up to the crossroad.
            # self.pick_direction(route, self.maze.get_surrounding_pheromone(self.current_position))
            return
        probabilities = [0, 0, 0, 0]  # list of probabilities for picking each direction.
        # east corresponds to index 0
        # N -> 1
        # W -> 2
        # S -> 3
        for direction in directions:
            probabilities[Direction.dir_to_int(direction)] = surrounding_pheromone.get(direction) / directions.__len__()
        direction = None
        if r:
            rand = random.uniform(0, 1)
            direction = roulette_wheel(probabilities, rand)
            # print (probabilities)
        else:
            direction = probabilities.index(max(probabilities))
        # print(direction, self.current_position, surrounding_pheromone)
        # print(directions, self.current_position, surrounding_pheromone)
        self.current_position = self.current_position.add_direction(direction)  # update position
        route.add(direction)  # update route

    # Method updates the number of steps taken from the last crossroad node.
    def update_crossroad(self):
        if not self.crossroads:
            return
        crossroad = self.crossroads.pop()
        self.crossroads.append(crossroad.increase_step())

    # Method returns a list of possible directions from a certain node.
    def get_possible_directions(self, surrounding_pheromone):
        directions = []
        # check if there is an unvisited node in certain direction
        if self.is_possible_direction(surrounding_pheromone, Direction.north):
            directions.append(Direction.north)
        if self.is_possible_direction(surrounding_pheromone, Direction.south):
            directions.append(Direction.south)
        if self.is_possible_direction(surrounding_pheromone, Direction.east):
            directions.append(Direction.east)
        if self.is_possible_direction(surrounding_pheromone, Direction.west):
            directions.append(Direction.west)
        return directions

    def is_possible_direction(self, surrounding_pheromone, direction):
        coord = copy.copy(self.current_position)
        coord = coord.add_direction(direction)
        return surrounding_pheromone.get(direction) != 0 and coord not in self.tabu_list
