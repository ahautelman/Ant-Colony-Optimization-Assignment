import os, sys
import copy

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import random
from src.TSPData import TSPData


# TSP problem solver using genetic algorithms.
class GeneticAlgorithm:

    # Constructs a new 'genetic algorithm' object.
    # @param generations the amount of generations.
    # @param popSize the population size.
    # @param min_distance_crossover min distance in between cuts for crossover.
    # @param mutation_chance probability of a chromosome mutation
    # @param c constant for loss function
    # @param a route length penalty in loss function
    def __init__(self, generations, pop_size, min_distance_crossover, mutation_chance=0.1, c=1000, alpha=1.2,
                 reproducing_prob=0.8):
        self.generations = generations
        self.pop_size = pop_size
        self.mutation_chance = mutation_chance
        self.min_distance_crossover = min_distance_crossover
        self.c = c
        self.alpha = alpha
        self.reproducing_prob = reproducing_prob

    def fitness(self, chromosome, tsp_data):
        """
        calculates the fitness of one chromosome
        :param chromosome: chromosome for which the fitness is calculated
        :param tsp_data: route data
        :return: fitness of :param chromosome
        """
        fitness = tsp_data.start_distances[chromosome[0]]

        for i in range(len(chromosome) - 1):
            fitness += tsp_data.product_to_product[chromosome[i]][chromosome[i + 1]].size()
        fitness += tsp_data.end_distances[chromosome[len(chromosome) - 1]]
        return self.c / (fitness ** self.alpha)

    def select_parents(self, chromosomes, fitness, population_factor):
        """
        selects parents to produce children based on the roulette wheel
        :param chromosomes: chromosomes of the generation
        :param fitness: fitness of the chromosomes
        :param population_factor: factor which corresponds to how many parents are selected
        :return: a set of selected parents
        """
        parents = []
        # chromosomes = chromosomes

        for i in range(int(self.pop_size / population_factor)):
            selected = self.select_one(chromosomes, fitness)
            index = chromosomes.index(selected)
            chromosomes.remove(selected)
            fitness.pop(index)
            parents.append(selected)

        return parents

    def select_one(self, population, fitness):
        """
        roulette wheel which selects one chromosome from the
        population based on probabilities.

        :param population: set of chromosomes
        :param fitness: fitness of the chromosomes
        :return: the selected chromosome, if it fails to select a chromosome
        it returns a random one
        """
        fitness_sum = sum(fitness)
        roulette = random.uniform(0, fitness_sum)
        current = 0

        for i in range(len(population)):
            current += fitness[i]
            if current >= roulette:
                return population[i]

    def mutate(self, children):
        """
        mutates children with probability self.mutation_chance

        :param children: a set of chromosomes
        :return: mutated children
        """
        mutants = []

        for i in range(len(children)):
            child = children[i]
            rand = random.uniform(0, 1)
            if rand < self.mutation_chance:
                idx = range(len(children))
                i1, i2 = random.sample(idx, 2)
                child[i1], child[i2] = child[i2], child[i1]
                mutants.append(child)
            else:
                mutants.append(child)

        return mutants

    def crossover(self, parent1, parent2):
        """
        The order crossover (OX)

        :param parent1: a chromosome
        :param parent2: a chromosome
        :return: two children that are made with the help of crossover OX
        """
        rand = random.uniform(0, 1)

        # do crossover with probability self.reproducing_prob
        if rand > self.reproducing_prob:
            return [parent1, parent2]

        product_size = 17
        child_1 = []
        child_2 = []
        sequence_1 = []
        sequence_2 = []
        keep_1 = []
        keep_2 = []

        # select two points for the array of the products
        cross_point_1 = random.randint(0, product_size - self.min_distance_crossover)
        if product_size - cross_point_1 == self.min_distance_crossover:
            cross_point_2 = product_size
        else:
            cross_point_2 = random.randint(cross_point_1 + self.min_distance_crossover, product_size)

        # values that remain unchanged in between crossover points
        for i in range(cross_point_1 + 1, cross_point_2 + 1):
            keep_1.append(parent1[i])
            keep_2.append(parent2[i])

        sequence_1 = [x for x in parent2 if x not in keep_1]
        sequence_2 = [x for x in parent1 if x not in keep_2]

        for j in range(0, cross_point_1 + 1):
            child_1.append(sequence_1[j])
            child_2.append(sequence_2[j])

        child_1 = child_1 + keep_1
        child_2 = child_2 + keep_2

        for j in range(cross_point_1 + 1, len(sequence_2)):
            child_1.append(sequence_1[j])
            child_2.append(sequence_2[j])

        return [child_1, child_2]

    def solve_tsp(self, tsp_data):
        """
        algorithm that uses ga to solve travelling salesman problem

        :param tsp_data: route data
        :return: the best chromosome found
        """
        chromosomes = []
        fitness = []

        # Create initial population of n chromosomes
        while len(chromosomes) < self.pop_size:
            chromosome = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            random.shuffle(chromosome)
            if not chromosomes.__contains__(chromosome):
                chromosomes.append(chromosome)

        for g in range(self.generations):
            print("-Generation", g)
            new_chromosomes = []

            # Evaluate fitness of each chromosome
            for i in range(len(chromosomes)):
                fitness.append(self.fitness(chromosomes[i], tsp_data))

            # Choose p/2 parents
            picked_parents = self.select_parents(chromosomes, fitness, 2)

            # create a new population
            while len(new_chromosomes) < self.pop_size:

                # Randomly select 2 parents, apply crossover
                parent1 = self.select_one(picked_parents, fitness)
                parent2 = self.select_one(picked_parents, fitness)
                children = self.crossover(parent1, parent2)

                # Apply mutations
                mutant_children = self.mutate(children)
                new_chromosomes.extend(mutant_children)

            # create a new population
            chromosomes.extend(new_chromosomes)
            chromosomes = self.find_best_chromosomes(chromosomes, tsp_data)
            fitness = []
            
            print("best individual", self.fitness(self.find_best_chromosome(chromosomes, tsp_data), tsp_data))

        return self.find_best_chromosome(chromosomes, tsp_data)

    def find_best_chromosome(self, chromosomes, tsp_data):
        """
        finds a chromosome with the highest fitness
        :return chromosome
        """

        best = chromosomes[0]
        best_fitness = self.fitness(best, tsp_data)

        for chromosome in chromosomes:
            fitness = self.fitness(chromosome, tsp_data)
            if fitness > best_fitness:
                best = chromosome
        return best

    def find_best_chromosomes(self, new_chromosomes, tsp_data):
        """
        find the best chromosomes in the population

        :param new_chromosomes: a list of chromosomes
        :param tsp_data: route data
        :return: an array of size self.pop_size of ebst chromosomes
        """

        fitness = [self.fitness(x, tsp_data) for x in new_chromosomes]

        fitness_and_chromosomes = list(zip(fitness, new_chromosomes))
        fitness_and_chromosomes.sort(key=lambda x: x[0], reverse=True)
        best_chromosomes = []

        for i in range(self.pop_size):
            best_chromosomes.append(fitness_and_chromosomes[i][1])

        return best_chromosomes


# Assignment 2.b
if __name__ == "__main__":
    # parameters
    population_size = 500
    gens = 200
    cross_distance = 5
    persistFile = "./../data/productMatrixDist.txt"

    # setup optimization
    tsp_data = TSPData.read_from_file(persistFile)
    print("read file")
    ga = GeneticAlgorithm(gens, population_size, cross_distance)

    # run optimzation and write to file
    solution = ga.solve_tsp(tsp_data)
    tsp_data.write_action_file(solution, "./../data/TSP solution.txt")
