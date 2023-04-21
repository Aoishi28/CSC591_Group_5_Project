from utils import *
from xpln import *
from xpln2 import *
from data import DATA
from statistical_tests import *
from os import listdir
from os.path import isfile, join
from texttable import Texttable

def initialize_tables():
    results_table = {'all': {'data' : [], 'evals' : 0},
             'sway1': {'data' : [], 'evals' : 0},
             'sway2': {'data' : [], 'evals' : 0},
             'xpln1': {'data' : [], 'evals' : 0},
             'xpln2': {'data' : [], 'evals' : 0},
             'top': {'data' : [], 'evals' : 0}}

    stats_tests_table = [[['all', 'all'],None],
                    [['all', 'sway1'],None],
                    [['sway1', 'sway2'],None],
                    [['sway1', 'xpln1'],None],
                    [['sway2', 'xpln2'],None],
                    [['sway1', 'top'],None]]
    
    return results_table, stats_tests_table

def update_results_table(results_table, data, data2, betters, rule, best, best2, best_xpln2, evals):
    results_table['top']['data'].append(DATA(data,betters))
    results_table['xpln1']['data'].append(DATA(data,selects(rule,data.rows)))
    results_table['xpln2']['data'].append(DATA(data2,best_xpln2))
    results_table['all']['data'].append(data)
    results_table['sway1']['data'].append(best)
    results_table['sway2']['data'].append(best2)
    results_table['all']['evals'] += 0
    results_table['sway1']['evals'] += evals
    results_table['sway2']['evals'] += evals
    results_table['xpln1']['evals'] += evals
    results_table['xpln2']['evals'] += evals
    results_table['top']['evals'] += len(data.rows)
    return results_table

def update_stats_tests_table(stats_tests_table, data, iteration):
    for i in range(len(stats_tests_table)):
        [base, diff], result = stats_tests_table[i]
        if result == None:
            stats_tests_table[i][1] = ['=' for _ in range(len(data.cols.y))]
        for k in range(len(data.cols.y)):
            if stats_tests_table[i][1][k] == '=':
                y0, z0 = results_table[base]['data'][iteration].cols.y[k],results_table[diff]['data'][iteration].cols.y[k]
                is_equal = bootstrap(y0.vals(), z0.vals()) and cliffsDelta(y0.vals(), z0.vals())
                if not is_equal:
                    stats_tests_table[i][1][k] = '≠'
    return stats_tests_table

def write_tables(results_table, stats_tests_table, file_path):
    with open(file_path.replace('/data', '/out').replace('.csv', '.out'), 'w', encoding="utf-8") as outfile:
        headers = [y.txt for y in data.cols.y]

        table1_first_row = [" "] + headers + ["n_evals avg"]
        table1_rows = [table1_first_row]

        for k,v in results_table.items():
            stats = [k] + [stats_average(v['data'])[y] for y in headers]
            stats += [v['evals']/the['n_iter']]
            table1_rows.append(stats)

        table1 = Texttable()
        table1.add_rows(table1_rows)

        print(table1.draw())
        outfile.writelines(table1.draw())

        table2_first_row = [" "] + headers
        table2_rows_formatted = [table2_first_row]

        for [base, diff], result in stats_tests_table:
            table2_rows_formatted.append([f"{base} to {diff}"] + result)

        table2 = Texttable()
        table2.add_rows(table2_rows_formatted)

        print(table2.draw())
        outfile.writelines("\n\n")
        outfile.writelines(table2.draw())
        
    with open(file_path.replace('/data', '/out').replace('.csv', '.latex'), 'w', encoding="utf-8") as outfile:
        outfile.writelines(create_latex_table(table1_rows))
        outfile.writelines(create_latex_table(table2_rows_formatted))

if __name__ == '__main__':
    data_path = './etc/data/'
    out_path = './etc/out/'
    files = [f for f in listdir(data_path) if isfile(join(data_path, f))]

    y,n,saved = 0,0,deepcopy(the)
    for k,v in cli(settings(help)).items():
        the[k] = v
        saved[k] = v
    if the['help'] == True:
        print(help)
    else:
        for file in files:
            iteration = 0
            file_path = join(data_path, file)
            
            results_table, stats_tests_table = initialize_tables()
            while iteration < the['n_iter']:
                data = DATA(file_path)
                data2 = preprocess_data(file_path, DATA)

                best,rest,evals = data.sway()
                xp = XPLN(best, rest)
                rule,_= xp.xpln(data,best,rest)

                best2,rest2,evals2 = data2.sway2()
                xp2 = XPLN2(best2, rest2)
                best_xpln2, rest_xpln2 = xp2.random_forest(data2)

                if rule != -1:
                    betters, _ = data.betters(len(best.rows))
                    results_table = update_results_table(results_table, data, data2, betters, rule, best, best2, best_xpln2, evals)
                    stats_tests_table = update_stats_tests_table(stats_tests_table, data, iteration)
                    iteration += 1
            
            write_tables(results_table, stats_tests_table, file_path)
            

