import rtamt
import sys

def monitor(data):
    """
    inf robustness means it pass by not being triggered
    neg robustness -> bad.
    standard robustness: does not care about anything that comes after implies
    - distance between input requirement and the threshold
    - not very useful
    output robustness:
    - evaluation gets delayed until the end of 'eventually' time delay
    - must log robustness score at each timestep, final robustness score is not a summary.
    - the value is the difference between Gnt and the defined Gnt Threshold
    """
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
    spec.add_sub_spec('response = eventually[0:T](speed <= speed_threshold);')
    spec.spec = 'out = ((surface == surf_threshold) implies response);'
    try:
        spec.parse()
        spec.pastify()
    except rtamt.RTAMTException as err:
        print('RTAMT Exception: {}'.format(err))
        sys.exit()

    for i in range(len(data['time'])):
        out_rob = spec.update(i, [
            ('surface', data['surface'][i][1]),
            ('speed', data['speed'][i][1])
        ])
        print(data['surface'][i][1], data['speed'][i][1])
        response_rob = spec.get_value('response')
        print(f'time: {i}, response robustness: {response_rob}, out robustness: {out_rob}')



if __name__ == '__main__':
    # Example test data
    data1 = {
        'time': [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0), (4.0, 4.0), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)],
        'surface': [(0, 0.0), (1, 0.0), (2, 1.0), (3, 1.0), (4, 1.0), (5, 0.0), (6, 0.0), (7, 0.0), (8, 0.0), (9, 0.0)],
        'speed': [(0, 100), (1, 100), (2, 100), (3, 100), (4, 50.0), (5, 50.0), (6, 50.0), (7, 50.0), (8, 0.0), (9, 0.0)],
    }

    monitor(data1)
