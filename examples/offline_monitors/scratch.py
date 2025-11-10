import rtamt
import sys
import glob
import numpy as np
import csv

def read_csv(filename):
    f = open(filename, 'r')
    reader = csv.reader(f)
    headers = next(reader, None)

    column = {}
    for h in headers:
        column[h] = []

    for row in reader:
        for h, v in zip(headers, row):
            column[h].append((float(row[0]), float(v)))

    return column

def speed_limit_rule(data):
    """
    inf robustness means it pass by not being triggered
    neg robustness -> bad.

    output robustness:
    - evaluation gets delayed until the end of 'eventually' time delay
    - must log robustness score at each timestep, final robustness score is not a summary.
    - the value is the difference between Gnt and the defined Gnt Threshold
    """
    spec = rtamt.StlDenseTimeSpecification(semantics=rtamt.Semantics.OUTPUT_ROBUSTNESS)
    spec.name = 'speed_limit'

    spec.declare_var('kart1_speed', 'float')

    spec.set_var_io_type('kart1_speed', 'input')

    spec.spec = 'out = (kart1_speed <= 10);'

    try:
        spec.parse()
        # spec.pastify()
    except rtamt.RTAMTException as err:
        print(f'RTAMT Exception: {err}')
        sys.exit(1)

    robustness_list = []
    rob = spec.evaluate(['kart1_speed', data['kart1_speed']])
    for i, data_point in enumerate(data['kart1_speed']):
        robustness_list.append(
            spec.update(i, [
                ('kart1_speed', data['kart1_speed'][i][1])
            ])
        )
    return robustness_list


if __name__ == '__main__':
    csv_folder_path = "/home/jim/Projects/rtamt/mariokart_traces/2025-11-03_22-25-04"
    files = glob.glob(csv_folder_path + "/*.csv")
    files.sort()
    for filename in files:
        data = read_csv(filename)
        robustness_result = speed_limit_rule(data)
        print(robustness_result[0:10])
        break
