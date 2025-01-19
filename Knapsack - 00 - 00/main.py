import pandas as pd
import reading_mknapcb as reading_mknapcb
from Heuristic import Knapsack_Heuristic

excel_file_path = 'input_output/input.xlsx'
df = pd.read_excel(excel_file_path)

for index, row in df.iloc[:].iterrows():

    # 0-run_id, 1-category, 2-problem_num, 3-cpu_time_limit, 4-PenaltiyRate, 5-MaxLpIter, 6-LowerBand
    row_values = list(row.iloc)
    run_id, category, problem_num, cpu_time_limit, PenaltiyRate, MaxLpIter, LowerBand = row_values[0], row_values[1], row_values[2], row_values[3], row_values[4], row_values[5], row_values[6]

    # nK = number of knapstacks
    # nI = number of items
    nI, nK , benefit, weight, capacity = reading_mknapcb.reading(category, problem_num)
    
    # creating an Heuristic object
    heu = Knapsack_Heuristic(run_id, PenaltiyRate, MaxLpIter, LowerBand, cpu_time_limit, nI, nK , benefit, weight, capacity)

    # getting result
    len_ItemsPool, phase2_solution, elapsed_time = heu.optimize()

    # writing in excel 
    heu.write_excel(run_id, category, problem_num, nI, nK, cpu_time_limit, PenaltiyRate, MaxLpIter, LowerBand, len_ItemsPool, phase2_solution, elapsed_time)
        
# End of program ------------------------