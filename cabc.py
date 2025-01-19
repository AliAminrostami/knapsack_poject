
import copy
import random
import time
import numpy as np
import pandas as pd
from datetime import datetime
from bee import Bee

def calculating_seed_number(category, problem_num, run_number):
    pn = str(problem_num)
    if(len(pn)==1):
        pn = "0" + pn

    run_number = str(run_number)
    if(len(run_number)==1):
        run_number = "0" + run_number

    result = int(list(category)[-1] + pn + run_number)
    return result

class Classic_Artificial_Bee_Colony:

    def __init__(self, run_id, category, problem_num, run_number, cpu_time_limit, nK, nI, Capacity, Profits, Weights, \
        employed_bees_num, onlooker_bees_num, max_try_improve, onlooker_selection_type, onlooker_k_tournoment, crossover_type, \
        pc_onePoint, pc_uniForm, pm, result_file_name, ItemsPoolList):
        
        seed_num = calculating_seed_number(category, problem_num, run_number)

        random.seed(seed_num)
        np.random.seed(seed_num)
        
        self.seed_num = seed_num
        self.run_id = run_id
        self.category = category
        self.problem_num = problem_num
        self.run_number = run_number
        self.cpu_time_limit = cpu_time_limit
        self.nK = nK
        self.nI = nI
        self.capacity = Capacity
        self.profits = np.array(Profits)
        self.weights = np.array(Weights)
        self.employed_bees_num = employed_bees_num
        self.onlooker_bees_num = onlooker_bees_num
        self.max_try_improve = max_try_improve
        self.selection_type = onlooker_selection_type
        self.k_tournoment = onlooker_k_tournoment
        self.crossover_type = crossover_type
        self.pc_onePoint = pc_onePoint
        self.pc_uniForm = pc_uniForm
        self.pm = pm
        self.result_file_name = result_file_name
        self.bees = []
        self.ItemsPool = ItemsPoolList

    def optimize(self):
        self.initialize_population()

        best_fitnesses_of_iteration = []
        best_fitnesses_so_far = []
        best_fitness_so_far = 0
        best_bee_so_far = Bee
        last_best_fitness_of_itration = 0
        time_number_list = []
    
        total_iteration_num = 0
        best_fitness_iteration_num = total_iteration_num # getting the last iteration that fitness ever updated

        currentTime = datetime.now().strftime("%H:%M:%S")
        print(f"run_id -> {self.run_id}: {currentTime}")
    
        start_t = time.time() # the start time of algorithm
        end_t = time.time()
        end_t_best_so_far = time.time()
        elapsed_time = 0

        while(elapsed_time<self.cpu_time_limit):

            result = open(self.result_file_name, 'a')    
            total_iteration_num+=1
            
            self.employed_bees_phase()
            self.onlooker_bees_phase()
            
            best_bee_of_iteration, best_fitness_of_iteration = self.find_best_bee()

            if(best_fitness_of_iteration > best_fitness_so_far):
                best_fitness_so_far = best_fitness_of_iteration
                best_bee_so_far = best_bee_of_iteration
                print(f"best fitness so far: {best_fitness_so_far}")
                best_fitness_iteration_num = total_iteration_num
                end_t_best_so_far = time.time()
              
            if (last_best_fitness_of_itration != best_fitness_of_iteration):
                end_t = time.time()
                elapsed_best_updated = end_t - start_t
                time_number_list.append(elapsed_best_updated)
                best_fitnesses_of_iteration.append(best_fitness_of_iteration)
                best_fitnesses_so_far.append(best_fitness_so_far)                
                last_best_fitness_of_itration = best_fitness_of_iteration  
                
            self.scout_bees_phase()            

            current_time = time.time()
            elapsed_time = current_time-start_t # calculating the total time for checking limitation
                            
            result.close()    

        best_fitness_time = end_t_best_so_far - start_t
                        
        len_bee = np.sum(best_bee_so_far.data == 1)

        return len_bee, best_bee_so_far, best_fitness_so_far, best_fitnesses_of_iteration, best_fitnesses_so_far, best_fitness_iteration_num, \
            total_iteration_num, best_fitness_time, time_number_list

    def initialize_population(self):
        # making each random solution -> employed bees
        # each random solution is made by randomly choose answers, and make them 1, until it stays feasible

        for _ in range(self.employed_bees_num):
            bee = self.make_a_bee()
            self.bees.append(bee)

    def employed_bees_phase(self):
          
        # we try for improvement one time for each bee, if change happens we add one to improvement-try property of that bee
        for bee in self.bees:
            change_flag = self.try_for_improvement(bee)
            
            if(change_flag == False): 
                bee.try_improve += 1

    def onlooker_bees_phase(self):
        # by rolette wheel precedure we do "onlooker_bees_num" times cross_over and mutation,
        # on solution that employed bees have made
        
        for _ in range(self.onlooker_bees_num):
            
            if (self.selection_type == "Roulette Wheel"):
                # selecting the bee by roulette wheel
                bee = self.roulette_wheel()

            elif(self.selection_type == "Tournoment"):
                # selecting a bee by tournoment procedure
                bee = self.tournoment()
            
            # we try for improvement one time for each bee, if change happens we add one to improvement-try property of that bee
            change_flag = self.try_for_improvement(bee)
            if(change_flag == False): 
                bee.try_improve += 1
                                                             
    def scout_bees_phase(self):
        # in here we select only delete the first bee that we see that has a try_improve larger than max_improvement try,
        # and delete it and replace it with new bee

        first_max_flag = False
        index = 0

        while index < len(self.bees) and first_max_flag == False:
            bee = self.bees[index]
            if bee.try_improve >= self.max_try_improve:
                self.bees.pop(index)
                self.bees.append(self.make_a_bee())
                first_max_flag == True
            index += 1

    def make_a_bee(self):
        # making each random solution -> employed bees
        # each random solution is made by randomly choose answers, and make them 1, until it stays feasible

        new_bee = Bee(self.nI)
        new_bee.data = copy.copy(self.ItemsPool)
        feasibility_flag = self.check_feasiblity(new_bee)

        while(not feasibility_flag):
            x = random.randint(0, self.nI-1)
            if(new_bee.data[x]==1):
                new_bee.data[x] = 0
                feasibility_flag = self.check_feasiblity(new_bee)

        self.calculate_fitness(new_bee)

        return new_bee

    def check_feasiblity(self, bee):
        # checking feasiblity of the answers that has been made (capacity)
        # Now perform the element-wise multiplication

        used_capacities = np.sum(bee.data * self.weights, axis=1)
        return np.all(used_capacities <= self.capacity)

    def try_for_improvement(self, bee):
        # we do the cross over and mutation here
        # we also return that if the process made any changes or not
        
        change_flag = False
        new_bee = copy.deepcopy(bee)
        
        # doing the cross over on selected bee and a neighbor (that will be handled in _cross_over)
        if(self.crossover_type == "one_point"):
            self.crossover_one_point(new_bee)
        elif(self.crossover_type == "uniform"):
            self.crossover_uniform(new_bee)
        
        # doing the mutation on selected bee
        self.mutation(new_bee) 
        
        # checking the feasiblity and improvement
        if(self.check_feasiblity(new_bee)):
           self.calculate_fitness(new_bee)
           if(new_bee.fitness > bee.fitness):
                change_flag = True     
                bee.data = copy.copy(new_bee.data) 
                bee.fitness = new_bee.fitness
                bee.try_improve = 0

        return change_flag    

    def crossover_one_point(self, bee):
        # we get a bee as entry, firstly we check if the probablity would let us do the crossover on this bee or not
        # secondly if the probablity let us, we check the determine precedure
        # thirdly we choose a random position
        # at the end we change the entered bee.data somehow that the first part (before choosen position) be from itself, 
            # and the second part (after choosen position) be from neighbor bee
        
        # in here we do not neccesserly change the entered bee
        
        x = random.random()

        if(x<=self.pc_onePoint):
            # choosing a random position for change
            random_pos = random.randint(1, self.nI-1)
            
            # choosing a neighbor, and it does not matter if it is the bee itself
            neighbor_bee = random.choice(self.bees)

            # in here we change parts of our "bee.data" base on choosed position,
            # the first part comes from bee.data, and the second part comes from neighbor.data 
            bee.data[random_pos:] = neighbor_bee.data[random_pos:].copy()

    def crossover_uniform(self, bee):
        # in here firstly we determine the precedure
        # secondly for each item in bee.data (entery) we check the cross_over probablity
        # we change the items that can pass the probablity, with the Adjacent item of neighbor bee
        
        # in here we mostly change the entered bee, but only a few items (it depends on "pc_uniForm")

        
        # choosing a neighbor, and it does not matter if it is the bee itself
        neighbor_bee = random.choice(self.bees)

        for item in range(self.nI):
            x = random.random()
            
            if(x<=self.pc_uniForm):            
                bee.data[item] = copy.copy(neighbor_bee.data[item]) 

    def mutation(self, bee):
        # for each answer that employed bees have made, we select a random position and we change it with 0 or 1 (randomly)
        # only if the changed answer be better than the previous one and it be valid, it will change
        # we also return that if the muatation has done a change or not
        
        random_numbers = np.random.random(self.nI)
        mask = random_numbers <= self.pm
        bee.data[mask] = np.where(bee.data[mask] == 0, 1, 0)

        mask = self.ItemsPool == 0
        bee.data[mask] = 0

    def calculate_fitness(self, bee):
        # fitness is amount of capacity that the bee can take (the capacity that the answer is occupying)
        bee.fitness = np.sum(self.profits * bee.data)

    def roulette_wheel(self):

        sum_of_fitnesses = sum([bee.fitness for bee in self.bees])

        rand_num = random.uniform(0, sum_of_fitnesses)
        cumulative_fitness = 0
        
        for bee in self.bees:
            cumulative_fitness += bee.fitness
            if cumulative_fitness >= rand_num:
                return bee
        
    def tournoment(self):
        # choosing our bee with tournoment procedure with "k_tournoment" variable
        
        bees_array = np.array(self.bees)  # Convert list of bees to numpy array

        # Randomly select k_tournament bees
        selected_indices = np.random.choice(len(bees_array), self.k_tournoment, replace=False)
        tournament_list = bees_array[selected_indices]

        # Find bee with maximum fitness
        max_bee_index = np.argmax([bee.fitness for bee in tournament_list])
        max_bee = tournament_list[max_bee_index]

        return max_bee
    
    def find_best_bee(self):
        fitness_values = np.zeros(len(self.bees))

        for i, bee in enumerate(self.bees):
            fitness_values[i] = bee.fitness

        best_index = np.argmax(fitness_values)
        best_bee = self.bees[best_index]
        best_fitness = fitness_values[best_index]

        return best_bee, best_fitness

    def write_results(self, LP_penaltiy_rate, LP_max_percentage, LP_min_value, len_ItemsPool,\
        len_bee, best_final_bee, best_final_fitness, best_fitnesses_of_iterations, best_fitness_iteration_num, total_iteration_num, \
        best_fitness_time):

        result = open(self.result_file_name, 'a')
        result.write("FINAL RESULT \n \n")
            
        fitness_avg = sum(best_fitnesses_of_iterations)/len(best_fitnesses_of_iterations)
        result.write(f"the best final Bee => \ndata: {best_final_bee.data}\nthe best final fitness: {best_final_fitness} \n")
        result.write(f"the average fitness of all: {fitness_avg}\n\n")

        result.write(f"best_fitness_iteration_num = {best_fitness_iteration_num}\n")        
        result.write(f"total_iteration_num = {total_iteration_num}\n")
        result.write(f"best_fitness_time = {best_fitness_time}\n\n")        

        result.write(f"len_ItemsPool = {len_ItemsPool}\n")
        result.write(f"len_final_bee = {len_bee}\n\n")

        result.write("------------------------ \n")
        result.write("Total PARAMETERS: \n")
        result.write(f"run_id = {self.run_id}\n")
        result.write(f"category = {self.category}\n")
        result.write(f"problem_num = {self.problem_num}\n")
        result.write(f"run_number = {self.run_number}\n")
        result.write(f"nK = {self.nK}\n")
        result.write(f"nI = {self.nI}\n")
        result.write(f"cpu_time_limit = {self.cpu_time_limit}\n")
        result.write(f"seed_num = {self.seed_num}\n\n")

        result.write("LP PARAMETERS: \n")
        result.write(f"LP_penaltiy_rate = {LP_penaltiy_rate}\n")
        result.write(f"LP_max_percentage = {LP_max_percentage}\n")
        result.write(f"LP_min_value = {LP_min_value}\n\n")

        result.write("ABC PARAMETERS: \n")  
        result.write(f"bees_num = {self.employed_bees_num}\n")
        result.write(f"max_try_improve = {self.max_try_improve}\n")
        result.write(f"onlooker_selection_type = {self.selection_type}\n")
        result.write(f"onlooker_k_tournoment = {self.k_tournoment}\n")
        result.write(f"crossover_type = {self.crossover_type}\n")
        result.write(f"pc_onePoint = {self.pc_onePoint}\n")
        result.write(f"pc_uniForm = {self.pc_uniForm}\n")        
        result.write(f"pm = {self.pm}\n")

        result.close()

    def write_excel(self, LP_penaltiy_rate, LP_max_percentage, LP_min_value, len_ItemsPool, \
        len_bee, best_final_fitness, best_fitness_iteration_num, total_iteration_num, best_fitness_time):
        file_path = 'input_output/output.xlsx'

        df = pd.read_excel(file_path)
        new_data = {'run_id': self.run_id,
                    'category': self.category, 
                    'problem_num': self.problem_num, 
                    'run_number': self.run_number,
                    'seed_num': self.seed_num,
                    'nK': self.nK,
                    'nI': self.nI,
                    'cpu_time_limit': self.cpu_time_limit, 
                    'LP_penaltiy_rate': LP_penaltiy_rate,
                    'LP_max_percentage': LP_max_percentage,
                    'LP_min_value': LP_min_value,
                    'ABC_bees_num': self.employed_bees_num, 
                    'ABC_max_try_improve': self.max_try_improve, 
                    'ABC_onlooker_selection': self.selection_type,
                    'ABC_onlooker_KT': self.k_tournoment,
                    'ABC_cross_over_type': self.crossover_type,
                    'ABC_pc_onePoint': self.pc_onePoint, 
                    'ABC_pc_uniForm': self.pc_uniForm, 
                    'ABC_pm': self.pm, 
                    'LP_len_pool_items': len_ItemsPool,
                    'ABC_len_best_fitness': len_bee,
                    'best_final_fitness': best_final_fitness,
                    'best_fitness_time': best_fitness_time,                    
                    'best_fitness_iteration_num': best_fitness_iteration_num,
                    'total_iteration_num': total_iteration_num,
                    }

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(file_path, index=False)