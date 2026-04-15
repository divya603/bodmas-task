import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from learner import create_learner
from learner_integration import LearnerGraphWalker

def trace(expr, learner_name):
    learner = create_learner(learner_name)
    walker = LearnerGraphWalker(expr, learner)
    steps = walker.walk_deterministic()
    return [s['state'] for s in steps]

candidates = [
    ('(2+3)*(4+1)+5',    'addition_first'),
    ('(6-2)*3+(8-4)*2',  'addition_first'),
    ('(1+3)*5-(2+1)*4',  'addition_first'),
    ('2*(3+4)+1*(5+2)',   'addition_first'),
    ('(4+2)*(3-1)+6',    'addition_first'),
    ('3*(2+5)-(1+4)*2',  'addition_first'),
    ('(5-1)*4+(3+2)*2',  'addition_first'),
    ('(7-3)*2+(4+1)*3',  'addition_first'),
    ('4*3+2*5-1',        'left_to_right_only'),
    ('3*4+2*3-1',        'left_to_right_only'),
    ('5*2+4*3+1',        'left_to_right_only'),
    ('2*6-3+4*2',        'left_to_right_only'),
    ('6*2+3-1*4',        'left_to_right_only'),
    ('(2+3)*4-1',        'right_to_left'),
    ('(4-1)*3+2',        'right_to_left'),
    ('(3+5)*2+4-1',      'right_to_left'),
    ('(6-2)*5+3-4',      'right_to_left'),
    ('(5-2)*(3+4)-2',    'bracket_ignorer'),
    ('(4+2)*3+2*(5-1)',  'bracket_ignorer'),
    ('(6+2)*(3-1)+4',    'bracket_ignorer'),
]

for i, (expr, ln) in enumerate(candidates, 1):
    try:
        e = trace(expr, 'expert')
        l = trace(expr, ln)
        fw = next((j for j, (a, b) in enumerate(zip(e, l)) if a != b), None)
        same = e[-1] == l[-1]
        flag = "  *** SAME ANSWER ***" if same else ""
        print(f"{i:2}. {expr:<26} {ln:<22} diverges@state={fw}  expert={e[-1]:<8} learner={l[-1]:<8}{flag}")
        print(f"    expert trace:  {' -> '.join(e)}")
        print(f"    learner trace: {' -> '.join(l)}")
        print()
    except Exception as ex:
        print(f"{i:2}. {expr:<26} {ln:<22} ERROR: {ex}")
        print()
