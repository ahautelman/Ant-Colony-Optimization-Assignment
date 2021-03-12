import os
import sys
import traceback

from src.Direction import Direction
from src.SurroundingPheromone import SurroundingPheromone

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


# Class that holds all the maze data. This means the pheromones, the open and blocked tiles in the system as
# well as the starting and end coordinates.
class Maze:

    # Constructor of a maze
    # @param walls int array of tiles accessible (1) and non-accessible (0)
    # @param width width of Maze (horizontal)
    # @param length length of Maze (vertical)
    # pheromone data structure will be initialized when the initialize_pheromone method is called
    def __init__(self, walls, width, length, start, end):       # TODO: i dont think we need to give the start and end coordinates since they are found in PathSpecification
        self.walls = walls
        self.length = length
        self.width = width
        self.start = start
        self.end = end
        self.pheromones = None
        self.initialize_pheromones()

    # Initialize pheromones to a start value.
    def initialize_pheromones(self):
        pheromone_matrix = self.walls

        for x in range(self.width):
            for y in range(self.length):
                if self.walls[x, y] == 1:
                    north_pheromone = 1 if y - 1 >= 0 and self.walls[x, y - 1] == 1 else 0
                    east_pheromone = 1 if x + 1 <= self.width and self.walls[x + 1, y] == 1 else 0
                    south_pheromone = 1 if y + 1 <= self.length and self.walls[x, y + 1] == 1 else 0
                    west_pheromone = 1 if x - 1 >= 0 and self.walls[x - 1, y] == 1 else 0
                    pheromone_matrix[x, y] = SurroundingPheromone(north_pheromone, east_pheromone, south_pheromone,
                                                                  west_pheromone)
                else:
                    pheromone_matrix[x, y] = SurroundingPheromone(0, 0, 0, 0)

        self.pheromones = pheromone_matrix
        return pheromone_matrix

    # Reset the maze for a new shortest path problem.
    def reset(self):
        self.initialize_pheromones()

    # Update the pheromones along a certain route according to a certain Q
    # @param r The route of the ants
    # @param Q Normalization factor for amount of dropped pheromone
    def add_pheromone_route(self, route, q):
        pheromone = q / len(route)
        coordinate = self.start

        # not checking the last node since it is going to be the end node
        for i in range(len(route) - 2):
            direction = route[i]
            self.pheromones[coordinate.x, coordinate.y].add(dir, pheromone)
            coordinate = coordinate.add_direction(direction)

    # Update pheromones for a list of routes
    # @param routes A list of routes
    # @param Q Normalization factor for amount of dropped pheromone
    def add_pheromone_routes(self, routes, q):
        for r in routes:
            self.add_pheromone_route(r, q)

    # Evaporate pheromone
    # @param rho evaporation factor
    def evaporate(self, rho):
        pheromones = self.pheromones

        east = 0
        north = 1
        west = 2
        south = 3

        for x in range(self.width):
            for y in range(self.length):
                if self.walls[x, y] == 1:
                    north_e = pheromones[x, y].get(Direction(north)) * (1 - rho)
                    east_e = pheromones[x, y].get(Direction(east)) * (1 - rho)
                    south_e = pheromones[x, y].get(Direction(south)) * (1 - rho)
                    west_e = pheromones[x, y].get(Direction(west)) * (1 - rho)
                    pheromones[x, y] = SurroundingPheromone(north_e, east_e, south_e, west_e)

    # Width getter
    # @return width of the maze
    def get_width(self):
        return self.width

    # Length getter
    # @return length of the maze
    def get_length(self):
        return self.length

    # Returns the amount of pheromones on the neighbouring positions (N/S/E/W).
    # @param position The position to check the neighbours of.
    # @return the pheromones of the neighbouring positions.
    def get_surrounding_pheromone(self, position):
        return self.pheromones[position.x, position.y]

    # Pheromone getter for a specific position. If the position is not in bounds returns 0
    # @param pos Position coordinate
    # @return pheromone at point
    def get_pheromone(self, pos):
        return self.pheromones[pos.x, pos.y]

    # Check whether a coordinate lies in the current maze.
    # @param position The position to be checked
    # @return Whether the position is in the current maze
    def in_bounds(self, position):
        return position.x_between(0, self.width) and position.y_between(0, self.length)

    # Representation of Maze as defined by the input file format.
    # @return String representation
    def __str__(self):
        string = ""
        string += str(self.width)
        string += " "
        string += str(self.length)
        string += " \n"
        for y in range(self.length):
            for x in range(self.width):
                string += str(self.walls[x][y])
                string += " "
            string += "\n"
        return string

    # Method that builds a mze from a file
    # @param filePath Path to the file
    # @return A maze object with pheromones initialized to 0's inaccessible and 1's accessible.
    @staticmethod
    def create_maze(file_path):
        try:
            f = open(file_path, "r")
            lines = f.read().splitlines()
            dimensions = lines[0].split(" ")
            width = int(dimensions[0])
            length = int(dimensions[1])

            # make the maze_layout
            maze_layout = []
            for x in range(width):
                maze_layout.append([])

            for y in range(length):
                line = lines[y + 1].split(" ")
                for x in range(width):
                    if line[x] != "":
                        state = int(line[x])
                        maze_layout[x].append(state)
            print("Ready reading maze file " + file_path)
            return Maze(maze_layout, width, length)
        except FileNotFoundError:
            print("Error reading maze file " + file_path)
            traceback.print_exc()
            sys.exit()
