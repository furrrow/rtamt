import rtamt
import sys
import glob
import numpy as np
import csv

surface_dict = {
    "dry_sand"      : 74,
    "wet_sand"      : 72,
    "shallow_water" : 92,
    "deep_water"    : 8,
    "grass"         : 90,
}
status_dict = {
    "ground"        : 0,
    "close_edge"    : 2,
    "fairy"         : 6,
    "deep_water"    : 8,
}

def read_csv(filename, time_tuple=False):
    f = open(filename, 'r')
    reader = csv.reader(f)
    headers = next(reader, None)

    column = {}
    for h in headers:
        column[h] = []

    for row in reader:
        for h, v in zip(headers, row):
            if time_tuple:
                column[h].append((float(row[0]), float(v)))
            else:
                column[h].append(float(v))
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
    spec = rtamt.StlDiscreteTimeSpecification()
    spec.name = 'speed_limit'

    spec.declare_var('kart1_speed', 'float')
    spec.spec = 'kart1_speed <= 10;'

    try:
        spec.parse()
    except rtamt.RTAMTException as err:
        print(f'RTAMT Exception: {err}')
        sys.exit()
    if "time" not in list(data.keys()):
        data['time'] = data['step']
    robustness_list = spec.evaluate(data)
    return robustness_list

def water_exposure_rule(data):
    """
    inf robustness means it pass by not being triggered
    neg robustness -> bad.

    output robustness:
    - evaluation gets delayed until the end of 'eventually' time delay
    - must log robustness score at each timestep, final robustness score is not a summary.
    - the value is the difference between Gnt and the defined Gnt Threshold
    """
    spec = rtamt.StlDiscreteTimeSpecification()
    spec.name = 'collision_detection'

    spec.declare_var('deep_water', 'bool')
    spec.declare_var('dry_sand', 'bool')
    # '((surface==8) implies (eventually[0:3](always[0:2](surface==74))));'
    spec.spec = '((deep_water)implies(eventually[0:3](always[0:2](dry_sand))));'

    try:
        spec.parse()
        # spec.pastify()
    except rtamt.RTAMTException as err:
        print(f'RTAMT Exception: {err}')
        sys.exit(1)
    if "time" not in list(data.keys()):
        data['time'] = data['step']
    data['deep_water'] = np.array(data['surface']) == surface_dict['deep_water']
    data['dry_sand'] = np.array(data['surface']) == surface_dict['dry_sand']
    robustness_list = spec.evaluate(data)
    return robustness_list

def collision_rule(data):
    """
    inf robustness means it pass by not being triggered
    neg robustness -> bad.

    output robustness:
    - evaluation gets delayed until the end of 'eventually' time delay
    - must log robustness score at each timestep, final robustness score is not a summary.
    - the value is the difference between Gnt and the defined Gnt Threshold
    """
    spec = rtamt.StlDiscreteTimeSpecification()
    spec.name = 'collision_detection'

    spec.declare_var('collision_detection', 'float')
    spec.set_var_io_type('collision_detection', 'input')
    spec.spec = 'collision_detection <= 0;'

    try:
        spec.parse()
        # spec.pastify()
    except rtamt.RTAMTException as err:
        print(f'RTAMT Exception: {err}')
        sys.exit(1)
    if "time" not in list(data.keys()):
        data['time'] = data['step']
    robustness_list = spec.evaluate(data)
    return robustness_list

if __name__ == '__main__':
    csv_folder_path = "/home/jim/Projects/rtamt/mariokart_traces/2025-11-03_22-25-04"
    files = glob.glob(csv_folder_path + "/*.csv")
    files.sort()
    for filename in files:
        data = read_csv(filename)
        speed_result = speed_limit_rule(data)
        water_result = water_exposure_rule(data)
        collision_result = collision_rule(data)
        print("speed limit rule:", speed_result[0:10])
        print("water exposure rule:", water_result[0:10])
        print("collision rule:", collision_result[0:10])

        break
