import rtamt
import sys
import glob
import numpy as np
import csv
import os
import re
from tqdm import tqdm
import matplotlib.pyplot as plt

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

def speed_limit_rule(data, speed_limit=900):
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
    spec.spec = f"kart1_speed <= {speed_limit};"

    try:
        spec.parse()
    except rtamt.RTAMTException as err:
        print(f'RTAMT Exception: {err}')
        sys.exit()
    if "time" not in list(data.keys()):
        data['time'] = data['step']
    robustness_list = spec.evaluate(data)
    return robustness_list

def water_exposure_rule(data, slow_speed=50):
    """
    inf robustness means it pass by not being triggered
    neg robustness -> bad.

    output robustness:
    - evaluation gets delayed until the end of 'eventually' time delay
    - must log robustness score at each timestep, final robustness score is not a summary.
    - the value is the difference between Gnt and the defined Gnt Threshold
    """
    spec = rtamt.StlDiscreteTimeSpecification(semantics=rtamt.Semantics.OUTPUT_ROBUSTNESS)
    spec.name = 'water_exposure_rule'
    spec.declare_const('threshold', 'float', '92')
    spec.declare_const('speed_threshold', 'float', '700')
    spec.declare_const('T', 'float', '50')
    spec.declare_var('surface', 'float')
    spec.declare_var('kart1_speed', 'float')
    spec.declare_var('response', 'float')
    spec.declare_var('out', 'float')
    spec.set_var_io_type('surface', 'input')
    spec.set_var_io_type('kart1_speed', 'output')
    spec.add_sub_spec('response = eventually[0:T](kart1_speed <= speed_threshold);')
    spec.spec = 'out = ((surface == threshold) implies response);'

    try:
        spec.parse()
        spec.pastify()
    except rtamt.RTAMTException as err:
        print(f'RTAMT Exception: {err}')
        sys.exit(1)
    # if "time" not in list(data.keys()):
    #     data['time'] = data['step']
    robustness_list = []
    # cart_x = np.array(data['kart1_X'])
    # cart_y = np.array(data['kart1_Y'])
    # plt.plot(cart_x, cart_y)
    # plt.show()

    for i in range(len(data['kart1_X'])):
        out_rob = spec.update(i, [
            ('surface', data['surface'][i]),
            ('kart1_speed', data['kart1_speed'][i]),
        ])
        robustness_list.append([i, out_rob])
        response_rob = spec.get_value('response')
        # robustness_list.append([i, rob==0])
        # print(f"time {i} resp_rob {response_rob:.3f} out_rob {out_rob:.3f} ")
        # if i > 10:
        #     break
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
    verbose = False
    speed_limit = 700

    speed_limit_matrix = []
    water_rule_matrix = []
    collision_rule_matrix = []
    speed_limit_dict = {"avg_neg_robustness": [], "min_neg_robustness": []}
    water_rule_dict = {"avg_neg_robustness": [], "min_neg_robustness": []}
    collision_rule_dict = {"avg_neg_robustness": [], "min_neg_robustness": []}
    for filename in tqdm(files, disable=verbose):
        trace_name = os.path.split(filename)[-1]
        trace_idx = re.search("\d+", os.path.split(filename)[-1]).group()
        trace_idx = int(trace_idx)
        data = read_csv(filename)
        speed_result = np.array(speed_limit_rule(data, speed_limit=speed_limit))
        water_result = np.array(water_exposure_rule(data))
        collision_result = np.array(collision_rule(data))

        # check if any timesteps have been skipped
        if speed_result[:, 0][-1] != len(speed_result[:, 0])-1:
            print(f"warning: {filename} speed_result total timestep mismatch!")
        if water_result[:, 0][-1] != len(water_result[:, 0])-1:
            print(f"warning: {filename} water_result total timestep mismatch!")
        if collision_result[:, 0][-1] != len(collision_result[:, 0])-1:
            print(f"warning: {filename} collision_result total timestep mismatch!")

        if verbose:
            print(f"file {filename}")
            print("speed limit rule:", speed_result[0:10, 1])
            print("water exposure rule:", water_result[0:10, 1])
            print("collision rule:", collision_result[0:10, 1])
            print()
        speed_limit_matrix.append(speed_result[:, 1])
        non_neg_val = (speed_result[:, 1][speed_result[:, 1] < 0])
        speed_limit_dict['avg_neg_robustness'].append(
            np.average(non_neg_val) if len(non_neg_val) > 0 else np.nan)
        speed_limit_dict['min_neg_robustness'].append(
            np.min(non_neg_val) if len(non_neg_val) > 0 else np.nan)

        water_rule_matrix.append(water_result[:, 1])
        non_neg_val = (water_result[:, 1][water_result[:, 1] < 0])
        water_rule_dict['avg_neg_robustness'].append(
            np.average(non_neg_val) if len(non_neg_val) > 0 else np.nan)
        water_rule_dict['min_neg_robustness'].append(
            np.min(non_neg_val) if len(non_neg_val) > 0 else np.nan)

        collision_rule_matrix.append(collision_result[:, 1])
        non_neg_val = (collision_result[:, 1][collision_result[:, 1] < 0])
        collision_rule_dict['avg_neg_robustness'].append(
            np.average(non_neg_val) if len(non_neg_val) > 0 else np.nan)
        collision_rule_dict['min_neg_robustness'].append(
            np.min(non_neg_val) if len(non_neg_val) > 0 else np.nan)
        # for debug purposes
        # if len(speed_limit_dict['avg_neg_robustness']) > 0:
        #     break

    print("speed_limit_rule:")
    print(f"average negative robustness {np.nanmean(speed_limit_dict['avg_neg_robustness']):.1f}, "
          f"minimal negative robustness {np.nanmin(speed_limit_dict['min_neg_robustness']):.1f}")
    print("water_rule:")
    print(f"average negative robustness {np.nanmean(water_rule_dict['avg_neg_robustness']):.1f}, "
          f"minimal negative robustness {np.nanmin(water_rule_dict['min_neg_robustness']):.1f}")
    print("collision_rule:")
    print(f"average negative robustness {np.nanmean(collision_rule_dict['avg_neg_robustness']):.1f}, "
          f"minimal negative robustness {np.nanmin(collision_rule_dict['min_neg_robustness']):.1f}")