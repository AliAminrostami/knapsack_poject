import pandas as pd
import reading_mknapcb as reading_mknapcb
import diagram
from cabc import Classic_Artificial_Bee_Colony
from heuristic_copy import Knapsack_Heuristic

excel_file_path = 'input_output/input.xlsx'
df = pd.read_excel(excel_file_path)

df['category'] = df['category'].astype('Int64')
 

for index, row in df.iloc[:].iterrows():

    #0-run_id, 1-category, 2-problem_num, 3-run_number, 4-cpu_time_limit, 5-LP_penaltiy_rate, 6-LP_max_iteration, 7-LP_min_value
    #8-ABC_bees_num, 9-ABC_max_try_improve, 10-ABC_onlooker_selection, 11-ABC_onlooker_KT, 12-ABC_cross_over_type, 13-ABC_pc_onePoint
    #14-ABC_pc_uniForm, 15-ABC_pm

    row_values = list(row.iloc)

    run_id, category, problem_num, run_number, cpu_time_limit, LP_penaltiy_rate, LP_max_iteration, LP_min_value = \
        row_values[0], row_values[1], row_values[2],row_values[3], row_values[4], row_values[5], row_values[6], row_values[7]
    
    
    # nK = number of knapstacks
    # nI = number of items
    nK, nI, Capacity, Profits, Weights = reading_mknapcb.reading(category, problem_num)

    heu = Knapsack_Heuristic(LP_penaltiy_rate, LP_max_iteration, LP_min_value, nI, nK, Profits, Weights, Capacity , cpu_time_limit)

    # getting result
    ItemsPoolList, len_ItemsPool , elapsed_time , obj_value , condition = heu.optimize()
    print(ItemsPoolList)
    print(len_ItemsPool)
    print(elapsed_time)
    print(obj_value)
    print(condition)
    
    # write in excel_1
    heu.write_excel ( LP_penaltiy_rate, LP_max_iteration, LP_min_value, len_ItemsPool , run_id , category \
                    , problem_num , run_number , elapsed_time , obj_value , condition)
        
    #result_file_name = f'input_output/{run_id}.txt'
    #result = open(result_file_name, 'a')
    #result.write(f"Hybrid LP Relaxation Artificial Bee Colony Algorithm on Multidimentional Knapsack Problem \n \n")        
    #result.close()



# End of program ------------------------ 

