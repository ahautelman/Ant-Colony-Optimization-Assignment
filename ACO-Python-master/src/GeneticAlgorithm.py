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
    def __init__(self, generations, pop_size, min_distance_crossover, mutation_chance=0.1, c=1000, alpha=1.1,
                 fucking_prob=0.8):
        self.generations = generations
        self.pop_size = pop_size
        self.mutation_chance = mutation_chance
        self.min_distance_crossover = min_distance_crossover
        self.c = c
        self.alpha = alpha
        self.fucking_prob = fucking_prob

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

    def fitness(self, chromosome, tsp_data):
        number = tsp_data.start_distances[chromosome[0]]
        # 2, 4, 6, 1
        for i in range(len(chromosome) - 1):
            number += tsp_data.product_to_product[chromosome[i]][chromosome[i + 1]].size()
        number += tsp_data.end_distances[chromosome[len(chromosome) - 1]]
        return self.c / (number ** self.alpha)

    def calc_probabilites(self, fitness):
        probabilities = []
        total_fit = 0
        for i in range(len(fitness)):
            total_fit = total_fit + fitness[i]
        for i in range(len(fitness)):
            probabilities.append(fitness[i] / total_fit)
        print(sum(probabilities))
        return probabilities

    def pick_parents(self, chromosomes, fitness):
        parents = []
        for i in range(int(self.pop_size / 2)):
            current_sum = 0
            selected = self.select_one(chromosomes, fitness)
            index = chromosomes.index(selected)
            # print(chromosomes)
            chromosomes.remove(selected)
            # print("selected", selected)
            fitness.pop(index)

            parents.append(selected)
        # print("parents", len(parents))
        # print(parents)
        return parents

    # def pick_parents(self, chromosomes, fitness):
    #     parents = []
    #     for i in range(int(self.pop_size / 2)):
    #         current_sum = 0
    #         parents.append(self.select_one(chromosomes, fitness))
    #     print("parents", len(parents))
    #     return parents
    #
    def select_one(self, population, fitness):
        max = sum(fitness)
        pick = random.uniform(0, max)
        current = 0
        for i in range(len(population)):
            current += fitness[i]
            if current >= pick:
                return population[i]

    def mutate(self, children):
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

    def cross_over(self, parent1, parent2):
        print("Parent 1", parent1)
        print("Parent 2", parent2)
        rand = random.uniform(0, 1)

        if rand > self.fucking_prob:
            return [parent1, parent2]

        # size 18 0 - 17
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
        print("Child 1", child_1)
        print("Child 2", child_2)

        return [child_1, child_2]

    # This method should solve the TSP.
    # @param pd the TSP data.
    # @return the optimized product sequence.
    def solve_tsp(self, tsp_data):
        chromosomes = []
        fitness = []
        # Create initial population of n chromosomes +
        # print("creating initial population")
        while len(chromosomes) < self.pop_size:
            list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            shuffled = self.shuffle(list)
            if not chromosomes.__contains__(shuffled):
                chromosomes.append(shuffled)

        # print(chromosomes)

        # Evaluate fitness of each chromosome +
        for i in range(len(chromosomes)):
            fitness.append(self.fitness(chromosomes[i], tsp_data))

        for g in range(self.generations):
            print("-Generation", g)
            # Choose p/2 parents +
            picked_parents = self.pick_parents(chromosomes, fitness)

            mated_parents = []
            new_chromosomes = []
            # print(len(picked_parents))
            # while len(mated_parents) < len(picked_parents):
            while len(new_chromosomes) < 5 * self.pop_size:
                # print("-- number of fuckings", len(mated_parents))
                print("--- number of children", len(new_chromosomes))
                # Randomly select 2 parents, apply crossover +
                parent1 = picked_parents[random.randint(0, len(picked_parents) - 1)]
                parent2 = picked_parents[random.randint(0, len(picked_parents) - 1)]
                # while parent1 == parent2:
                #     parent2 = picked_parents[random.randint(0, len(picked_parents) - 1)]
                # if not mated_parents.__contains__(parent1):
                #     mated_parents.append(parent1)
                #     print("added something", len(mated_parents))
                # if not mated_parents.__contains__(parent2):
                #     mated_parents.append(parent2)
                #     print("added something", len(mated_parents))
                children = self.cross_over(parent1, parent2)
                # Apply mutations +
                mutant_children = self.mutate(children)
                new_chromosomes.extend(mutant_children)
                # Repeat 4-5 until all parents are selected +

            # Replace old population with new chromosomes +
            chromosomes = self.find_best_chromosomes(new_chromosomes, tsp_data)
            # Evaluate fitness of each chromosome +
            new_fitness = []
            # print("CHROMOSOMES", chromosomes)
            for i in range(len(chromosomes)):
                new_fitness.append(self.fitness(chromosomes[i], tsp_data))
            fitness = new_fitness
            # print(fitness)
            # Terminate if number of generations reached limit, otherwise go to step 3 +
        return self.find_best_chromosome(chromosomes, tsp_data)

    def find_best_chromosome(self, chromosomes, tsp_data):
        best = chromosomes[0]
        best_fitness = self.fitness(best, tsp_data)

        for chromosome in chromosomes:
            fittness = self.fitness(chromosome, tsp_data)
            if (fittness < best_fitness):
                best = chromosome
        return best

    def find_best_chromosomes(self, new_chromosomes, tsp_data):
        fitnesses = [self.fitness(x, tsp_data) for x in new_chromosomes]

        fitnesses_and_chromosomes = list(zip(fitnesses, new_chromosomes))
        fitnesses_and_chromosomes.sort(key=lambda x: x[0], reverse=True)
        print("length of new chromies:", len(new_chromosomes))
        best_chromosomes = []
        for i in range(self.pop_size):
            best_chromosomes.append(fitnesses_and_chromosomes[i][1])
        return best_chromosomes


# Assignment 2.b
if __name__ == "__main__":
    # parameters
    population_size = 500
    generations = 100
    min_distance_crossover = 3
    persistFile = "./../data/productMatrixDist.txt"

    # setup optimization
    tsp_data = TSPData.read_from_file(persistFile)
    print("read file")
    ga = GeneticAlgorithm(generations, population_size, min_distance_crossover)

    # run optimzation and write to file
    solution = ga.solve_tsp(tsp_data)
    tsp_data.write_action_file(solution, "./../data/TSP solution.txt")