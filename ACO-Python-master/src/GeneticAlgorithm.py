import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import random
from src.TSPData import TSPData

# TSP problem solver using genetic algorithms.
class GeneticAlgorithm:

    # Constructs a new 'genetic algorithm' object.
    # @param generations the amount of generations.
    # @param popSize the population size.
    def __init__(self, generations, pop_size, c=1000, alpha=1.1):
        self.generations = generations
        self.pop_size = pop_size
        self.c = c
        self.alpha = alpha

     # Knuth-Yates shuffle, reordering a array randomly
     # @param chromosome array to shuffle.
    def shuffle(self, chromosome):
        n = len(chromosome)
        for i in range(n):
            r = i + int(random.uniform(0, 1) * (n - i))
            swap = chromosome[r]
            chromosome[r] = chromosome[i]
            chromosome[i] = swap
        return chromosome

    # This method should solve the TSP.
    # @param pd the TSP data.
    # @return the optimized product sequence.
    def solve_tsp(self, tsp_data):
        list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17]
        return list

    def loss(self, chromosome, tsp_data):
        loss = 0
        for i in range(len(chromosome) - 1):
            loss += len(tsp_data.product_to_product[i][i+1])
        return self.c / (loss**self.alpha)


# Assignment 2.b
if __name__ == "__main__":
    #parameters
    population_size = 20
    generations = 20
    persistFile = "./../tmp/productMatrixDist"
        
    #setup optimization
    tsp_data = TSPData.read_from_file(persistFile)
    ga = GeneticAlgorithm(generations, population_size)

    #run optimzation and write to file
    solution = ga.solve_tsp(tsp_data)
    tsp_data.write_action_file(solution, "./../data/TSP solution.txt")