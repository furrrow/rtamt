import rtamt
import sys

def monitor(data1):
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
    # spec = rtamt.StlDiscreteTimeSpecification(semantics=rtamt.Semantics.STANDARD)
    spec = rtamt.StlDiscreteTimeSpecification(semantics=rtamt.Semantics.OUTPUT_ROBUSTNESS)
    spec.name = 'Example 1'

    spec.declare_var('req', 'float')
    spec.declare_var('gnt', 'float')
    spec.declare_var('out', 'float')

    spec.set_var_io_type('req', 'input')
    spec.set_var_io_type('gnt', 'output')

    # spec.spec = 'out = ((req >= 3) implies (eventually[0:2](gnt >= 3)));'
    # spec.spec = 'out = ((req >= 3) or (gnt >= 3));'
    spec.spec = 'out = ((req >= 3) implies (eventually[0:1](gnt >= 3)));'

    try:
        spec.parse()
        spec.pastify()
    except rtamt.RTAMTException as err:
        print(f'RTAMT Exception: {err}')
        sys.exit(1)

    rob = None
    for i in range(len(data1['gnt'])):
        rob = spec.update(i, [
            ('req', data1['req'][i][1]),
            ('gnt', data1['gnt'][i][1])
        ])
        print(f"time {i} robustness {rob:.3f}")

    print(f'Example (a) - standard robustness: {rob}')


if __name__ == '__main__':
    # Example test data
    data1 = {
        'time': [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0), (4.0, 4.0)],
        'req': [(0, 0.0), (1, 4.0), (2, 0.0), (3, 0.0), (4, 0.0)],
        'gnt': [(0, 0.0), (1, 0.0), (2, 2.0), (3, 0.0), (4, 0.0)]
    }

    monitor(data1)
