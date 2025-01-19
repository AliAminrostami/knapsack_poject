# Importing Dependencies
import time
import pandas as pd
from datetime import datetime
import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition

class Knapsack_Heuristic:

    def __init__(self, run_id, PenaltiyRate, MaxLpIter, LowerBand, cpu_time_limit, nI, nK , benefit, weight, capacity):

        self.run_id = run_id
        self.PenaltiyRate = PenaltiyRate
        self.MaxLpIter = MaxLpIter
        self.LowerBand = LowerBand
        self.cpu_time_limit = cpu_time_limit
        self.nI = nI   # number of items
        self.nK = nK   # number of knapstacks
        self.benefit = benefit
        self.weight = weight
        self.capacity = capacity

    def optimize(self):  

        # Model Definition
        model = pyo.ConcreteModel()    

        # Set Definition
        model.N = pyo.RangeSet(1,self.nI) # RangeSet Items
        model.M = pyo.RangeSet(1,self.nK) # RangeSate Knapsack

        # Parameter Declarations
        def c_init(model,j):
            return self.benefit[j-1] 
        model.c = pyo.Param(model.N, initialize= c_init, mutable = True) # Benefit 

        def a_init(model,i,j):
            return self.weight[i-1][j-1]
        model.a = pyo.Param(model.M, model.N, initialize= a_init) # Weight 

        def b_init(model,i):
            return self.capacity[i-1]
        model.b = pyo.Param(model.M, initialize= b_init) # Capacity

        # Variable Declarations
        model.x = pyo.Var(model.N, bounds= (0,1), domain= pyo.NonNegativeReals) # Lp

        # Objective Function Definition
        def obj_rule(model):
            return sum(model.c[i] * model.x[i]  for i in  model.N)
        model.obj = pyo.Objective(rule= obj_rule, sense= pyo.maximize)

        # Constraint Declarations 
        def con_rule(model,m):
            return sum(model.a[m,i] * model.x[i] for i in model.N) <= model.b[m]
        model.con = pyo.Constraint(model.M, rule= con_rule)

        # creat the solver
        solver = pyo.SolverFactory('cplex')
        # solver.solve(model)

        # Selected items function
        def selection():
            """ doc string """
            s1 = []
            for i in model.N:
                if pyo.value(model.x[i]) > self.LowerBand :
                    s1.append(i)
            return set(s1)

        start_t = time.time() # the start time of algorithm
        currentTime = datetime.now().strftime("%H:%M:%S")
        print(f"run_id -> {self.run_id}: {currentTime}")
        elapsed_time = 0
    
        selectedItems = set() # At the current iteration.
        ItemsPool = set() # At the union of all iterations.

        # Phase1
        # Solve the penalized LP relaxation
        if  self.MaxLpIter == 0:
            model.x.domain = pyo.Binary
            solver.options['timelimit'] = self.cpu_time_limit
            solver.solve(model)
            
        else:
            iteration = 1
            while(iteration <= self.MaxLpIter):

                solver.solve(model) 
                selectedItems = selection() 
                ItemsPool = ItemsPool.union(selectedItems)
                for item in selectedItems: 
                    model.c[item] *= self.PenaltiyRate

                iteration += 1

            # Phase2
            for item in ItemsPool: 
                model.c[item] = self.benefit[item-1]

            ### Variable redefine
            model.x.domain = pyo.Binary
            model.x.fix(0)
            for item in ItemsPool: 
                model.x[item] = model.x[item].unfix()

            ### solver options 
            solver.options['timelimit'] = self.cpu_time_limit

            ### Wait to load the solution into the model after the solver status is checked
            results = solver.solve(model, load_solutions=False)
            solution_stat_flag = 0

            if (results.solver.status == SolverStatus.ok):
                if (results.solver.termination_condition == TerminationCondition.optimal):
                    solution_stat_flag = 1
                    print("Optimal solution found!!!") 
                # solver.options['timelimit'] = None
                else:
                    print("Optimal solution not found!!!") 
                    solution_stat_flag = 2
                model.solutions.load_from(results) # Manually load 
            else:
                solution_stat_flag = 3
                print("Feasible solution not found!!!!")
                # model.solutions.load_from(results) # Manually load the solution into the model 

        if(solution_stat_flag == 1 or solution_stat_flag == 2):
            len_ItemsPool = len(ItemsPool)
            phase2_solution = pyo.value(model.obj)
            print(f"best fitness so far: {phase2_solution}\n")
            current_time = time.time()
            elapsed_time = current_time-start_t # calculating the total time

        # return solution_stat_flag, len_ItemsPool, phase2_solution, elapsed_time
        return len_ItemsPool, phase2_solution, elapsed_time

    def write_excel(self, run_id, category, problem_num, nI, nK, cpu_time_limit, PenaltiyRate, MaxLpIter, LowerBand,\
        Len_ItemsPool, phase2_solution, elapsed_time ):
        file_path = 'input_output/output.xlsx'

        df = pd.read_excel(file_path)
        new_data = {'run_id': run_id,
                    'category': category, 
                    'problem_num': problem_num,
                    'nI': nI,
                    'nK': nK,
                    'cpu_time_limit': cpu_time_limit, 
                    'PenaltiyRate': PenaltiyRate, 
                    'MaxLpIter': MaxLpIter, 
                    'MaxLpIter': MaxLpIter, 
                    'LowerBand': LowerBand, 
                    'Len_ItemsPool': Len_ItemsPool, 
                    'phase2_solution': phase2_solution, 
                    'elapsed_time': elapsed_time,
                    }

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(file_path, index=False)