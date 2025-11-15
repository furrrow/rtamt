import sys
import csv
import rtamt
import os

def monitor():
    # Load traces
    # data = read_csv('playback_trace00.csv')
    data = read_csv('/home/jim/Projects/rtamt/mariokart_traces/2025-11-03_22-25-04/playback_trace00.csv')

    spec = rtamt.StlDiscreteTimeSpecification(semantics=rtamt.Semantics.OUTPUT_ROBUSTNESS)
    spec.name = 'Example 1'
    spec.declare_const('threshold', 'float', '92')
    spec.declare_const('T', 'float', '5')
    spec.declare_var('surface', 'float')
    spec.declare_var('kart1_speed', 'float')
    spec.declare_var('response', 'float')
    spec.declare_var('out', 'float')
    spec.set_var_io_type('surface', 'input')
    spec.set_var_io_type('kart1_speed', 'output')
    spec.add_sub_spec('response = eventually[0:10](kart1_speed <= 5);')
    spec.spec = 'out = ((surface == threshold) implies response);'
    

    
    try:
        spec.parse()
        spec.pastify()
    except rtamt.RTAMTException as err:
        print('RTAMT Exception: {}'.format(err))
        sys.exit()

    for i in range(len(data['kart1_speed'])):
        out_rob = spec.update(i, [('surface', data['surface'][i][1]), ('kart1_speed', data['kart1_speed'][i][1])])
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
