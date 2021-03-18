import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import random
from src.TSPData import TSPData

# TSP problem solver using genetic algorithms.
class GeneticAlgorithm:

    # Constructs a new 'genetic algorithm' object.
    # @param generations the amount of generations.
    # @param popSize the population size.
    def __init__(self, generations, pop_size, min_distance_crossover, mutation_chance = 0.1, c=1000, alpha=1.1):
        self.generations = generations
        self.pop_size = pop_size
        self.mutation_chance = mutation_chance
        self.min_distance_crossover = min_distance_crossover
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

    def cross_over(self, parent1, parent2):
        return

    def fitness(self, chromosome, tsp_data):
        loss = 0
        for i in range(len(chromosome) - 1):
            loss += len(tsp_data.product_to_product[i][i + 1])
        return self.c / (loss ** self.alpha)

    def calc_probabilites(self, fitness):
        probabilities = []
        total_fit = 0
        for i in range(len(fitness)):
            total_fit = total_fit + fitness[i]
        for i in range(len(fitness)):
            probabilities.append(fitness[i]/total_fit)
        return probabilities

    def pick_parents(self, chromosomes, fitness):
        parents = []
        probabilities = self.calc_probabilites(fitness)
        for i in range(self.pop_size/2):
            rand = random.uniform(0, 1)
            curr_sum = probabilities[0]
            for y in range(1, len(probabilities)):
                if rand < curr_sum:
                    parents.append(chromosomes[y])
                    break
                else:
                    curr_sum += probabilities[y]
        return parents

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

        return [child_1, child_2]

    # This method should solve the TSP.
    # @param pd the TSP data.
    # @return the optimized product sequence.
    def solve_tsp(self, tsp_data):
        chromosomes = []
        fitness = []
        # Create initial population of n chromosomes +
        for i in range(self.pop_size):
            list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            chromosomes.append(self.shuffle(list))
        # Evaluate fitness of each chromosome +
        for i in range(len(chromosomes)):
            fitness.append(self.fitness(chromosomes[i], tsp_data))

        for g in range(self.generations):
            # Choose p/2 parents +
            picked_parents = self.pick_parents(chromosomes, fitness)

            mated_parents = []
            new_chromosomes = []
            while len(mated_parents) < len(picked_parents):
                # Randomly select 2 parents, apply crossover +
                parent1 = random.choice(picked_parents)
                parent2 = random.choice(picked_parents)
                while parent1 == parent2:
                    parent2 = random.choice(picked_parents)
                if parent1 not in mated_parents:
                    mated_parents.append(parent1)
                if parent2 not in mated_parents:
                    mated_parents.append(parent2)
                children = self.cross_over(parent1, parent2)
                # Apply mutations +
                mutant_children = self.mutate(children)
                new_chromosomes.extend(mutant_children)
                # Repeat 4-5 until all parents are selected +

            # Replace old population with new chromosomes +
            chromosomes = new_chromosomes
            # Evaluate fitness of each chromosome +
            new_fitness = []
            for i in range(len(chromosomes)):
                new_fitness.append(self.fitness(chromosomes[i], tsp_data))
            fitness = new_fitness
            print(fitness)
            # Terminate if number of generations reached limit, otherwise go to step 3 +

        return list

# Assignment 2.b
if __name__ == "__main__":
    #parameters
    population_size = 20
    generations = 20
    min_distance_crossover = 3
    persistFile = "./../tmp/productMatrixDist"
        
    #setup optimization
    tsp_data = TSPData.read_from_file(persistFile)
    ga = GeneticAlgorithm(generations, population_size, min_distance_crossover)

    #run optimzation and write to file
    solution = ga.solve_tsp(tsp_data)
    tsp_data.write_action_file(solution, "./../data/TSP solution.txt")