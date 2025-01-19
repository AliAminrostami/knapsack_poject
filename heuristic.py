# Importing Dependencies
import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition
import numpy as np
import pandas as pd
import time
from datetime import datetime

class Knapsack_Heuristic:

    def __init__(self, LP_penaltiy_rate, LP_max_percentage, LP_min_value, nI, nK , Profits, Weights, Capacity , cpu_time_limit):
        
        self.PenaltiyRate = LP_penaltiy_rate
        self.MaxLpperc = LP_max_percentage
        self.MinValue = LP_min_value
        self.nI = nI   # number of items
        self.nK = nK   # number of knapstacks
        self.benefit = Profits
        self.weight = Weights
        self.capacity = Capacity
        self.cpu_time_limit = cpu_time_limit
        
    def optimize(self):  

        # Model Definition
        model = pyo.ConcreteModel()    

        # Set Definition
        model.N = pyo.RangeSet(1, self.nI) # RangeSet Items
        model.M = pyo.RangeSet(1, self.nK) # RangeSate Knapsack

        # Parameter Declarations
        def c_init(model, j):
            return self.benefit[j-1] 
        model.c = pyo.Param(model.N, initialize = c_init, mutable = True) # Benefit 

        def a_init(model, i, j):
            return self.weight[i-1][j-1]
        model.a = pyo.Param(model.M, model.N, initialize = a_init) # Weight 

        def b_init(model, i):
            return self.capacity[i-1]
        model.b = pyo.Param(model.M, initialize = b_init) # Capacity

        # Variable Declarations
        model.x = pyo.Var(model.N, bounds = (0,1), domain = pyo.NonNegativeReals) # Lp

        # Objective Function Definition
        def obj_rule(model):
            return sum(model.c[i] * model.x[i] for i in model.N)
        model.obj = pyo.Objective(rule = obj_rule, sense = pyo.maximize)

        # Constraint Declarations 
        def con_rule(model, m):
            return sum(model.a[m,i] * model.x[i] for i in model.N) <= model.b[m]
        model.con = pyo.Constraint(model.M, rule = con_rule)

        # creat the solver
        solver = pyo.SolverFactory('cplex')
        # solver.solve(model)
 
        # Selected items function
        def selection():
            """ doc string """ 
            s1 = []
            for i in model.N:
                if pyo.value(model.x[i]) > self.MinValue:
                    s1.append(i)
            return set(s1)
    
        selectedItems = set() # At the current iteration.
        ItemsPool = set() # At the union of all iterations.
        
        start_time = time.time() # the start time of algorithm
        
        elapsed_time = 0

        
        # Solve the penalized LP relaxation
        #iteration = 1
        
        while((len(ItemsPool)/self.nI) < self.MaxLpperc and elapsed_time<self.cpu_time_limit):
            
            
            results = solver.solve(model) 
            selectedItems = selection() 
            ItemsPool = ItemsPool.union(selectedItems)
            for item in selectedItems: 
                model.c[item] *= self.PenaltiyRate
                
        end_time = time.time()    
        elapsed_time = end_time - start_time  # calculating the total time
            
        obj_value = int(pyo.value(model.obj))
        condition = results.solver.termination_condition
            #iteration += 1
        
        ItemsPoolList = np.zeros(self.nI)
        for item in ItemsPool: 
            ItemsPoolList[item-1] = 1
 
        
        return ItemsPoolList, len(ItemsPool) , elapsed_time , obj_value , condition
    
    def write_excel(self, LP_penaltiy_rate, LP_max_percentage, LP_min_value, len_ItemsPool , run_id , category \
                    , problem_num , run_number , elapsed_time , obj_value , condition,sheet_name):
        
        file_path = 'input_output/output.xlsx'

        df = pd.read_excel(file_path)
        new_data = {'run_id': run_id,
                    'category': category, 
                    'problem_num': problem_num, 
                    'run_number': run_number,                    
                    'nK': self.nK,
                    'nI': self.nI,
                    'cpu_time_limit': self.cpu_time_limit, 
                    'LP_penaltiy_rate': LP_penaltiy_rate,
                    'LP_max_percentage': LP_max_percentage,
                    'LP_min_value': LP_min_value,
                    'LP_len_pool_items': len_ItemsPool,
                    'elapsed_time': elapsed_time,
                    'obj_value': obj_value,
                    'condition':condition,
                    }

         # Convert new_data to a DataFrame
        new_data_df = pd.DataFrame([new_data])

        try:
            # Read existing sheets in the Excel file
            with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                try:
                    existing_data = pd.read_excel(file_path, sheet_name=sheet_name)
                    # Concatenate existing data with the new data
                    updated_data = pd.concat([existing_data, new_data_df], ignore_index=True)
                except ValueError:
                    # If the sheet doesn't exist, create a new one
                    updated_data = new_data_df
                
                # Write the updated data back to the sheet
                updated_data.to_excel(writer, index=False, sheet_name=sheet_name)
        except FileNotFoundError:
            # If the file doesn't exist, create a new one with the given sheet
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                new_data_df.to_excel(writer, index=False, sheet_name=sheet_name)