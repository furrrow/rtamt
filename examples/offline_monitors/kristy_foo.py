import sys
import csv
import rtamt
import os

def monitor():
    # Load traces
    data = read_csv('example1b.csv')
    spec = rtamt.StlDiscreteTimeSpecification(semantics=rtamt.Semantics.OUTPUT_ROBUSTNESS)
    spec.name = 'Example 1'
    spec.declare_const('surf_threshold', 'float', '1')
    spec.declare_const('speed_threshold', 'float', '50')
    spec.declare_const('T', 'float', '5')
    spec.declare_var('surface', 'float')
    spec.declare_var('speed', 'float')
    spec.declare_var('response', 'float')
    spec.declare_var('out', 'float')
    # spec.set_var_io_type('surface', 'input')
    # spec.set_var_io_type('speed', 'output')
    spec.add_sub_spec('response = eventually[0:5](speed <= speed_threshold);')
    spec.spec = 'out = ((surface == surf_threshold) implies response);'
    

    
    try:
        spec.parse()
        spec.pastify()
    except rtamt.RTAMTException as err:
        print('RTAMT Exception: {}'.format(err))
        sys.exit()

    for i in range(len(data['speed'])):
        # print((i, [('surface', data['surface'][i][1]), ('speed', data['speed'][i][1])]))
        out_rob = spec.update(i, [('surface', data['surface'][i][1]), ('speed', data['speed'][i][1])])
        response_rob = spec.get_value('response')
        print(f'time: {i}, response robustness: {response_rob}, out robustness: {out_rob}')


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

if __name__ == '__main__':
    # Process arguments
    
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    monitor()
