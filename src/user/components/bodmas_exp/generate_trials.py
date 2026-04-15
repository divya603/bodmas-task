"""
Generate pre-computed trial data for the BODMAS SMILE experiment.
Output: trials.json (same directory as this script)

Run from the bodmas_exp directory:
    python generate_trials.py
"""

import sys
import json
import random
import os

# Add this directory to path so Python finds the learner modules
sys.path.insert(0, os.path.dirname(__file__))

from learner import create_learner, LEARNER_PROFILES
from learner_integration import LearnerGraphWalker
from tokenizer import tokenize

random.seed(42)

DIAG_LEARNER_DESCRIPTIONS = {
    'addition_first':
        "Does addition and subtraction before multiplication and division",
    'multiplication_first':
        "Treats multiplication as the highest-priority operation; expands brackets with ×",
    'left_to_right_only':
        "Ignores operator precedence — evaluates everything strictly left to right",
    'right_to_left':
        "Ignores operator precedence — evaluates everything strictly right to left",
    'novice':
        "Has no consistent rule — picks operations in no predictable order",
    'bracket_ignorer':
        "Drops brackets entirely, then evaluates left to right",
    'distributor':
        "Knows BODMAS but prefers to expand (distribute) brackets instead of evaluating inside them",
    'bodmas_wrong_direction':
        "Knows multiplication comes before addition, but applies operations right to left",
    'expert':
        "Correctly follows BODMAS: brackets first, then ×÷, then +−, left to right",
    'bodmas_correct':
        "Follows BODMAS (×÷ before +−), evaluates left to right",
}

DIAG_LEARNER_LABELS = {
    'addition_first':         'Addition Before ×',
    'multiplication_first':   '× Highest Priority',
    'left_to_right_only':     'Strictly Left→Right',
    'right_to_left':          'Strictly Right→Left',
    'novice':                 'No Consistent Strategy',
    'bracket_ignorer':        'Ignores Brackets',
    'distributor':            'Prefers Distributing',
    'bodmas_wrong_direction':  'BODMAS Right→Left',
    'expert':                 'Expert (BODMAS)',
    'bodmas_correct':         'BODMAS Correct',
}

BODMAS_PREC = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}


def display_expr(s: str) -> str:
    return s.replace('/', '÷')


def get_learner_trace(expression: str, learner_name: str):
    learner = create_learner(learner_name)
    walker = LearnerGraphWalker(expression, learner)
    return walker.walk_deterministic()


def get_final_answer(steps):
    if steps and 'result' in steps[-1]:
        result = steps[-1]['result']
        if result == int(result):
            return str(int(result))
        return f"{result:.4f}".rstrip('0').rstrip('.')
    return "N/A"


def bracket_depth_at(tokens, index):
    depth = 0
    for i in range(min(index, len(tokens))):
        if tokens[i] in ('(', '[', '{'):
            depth += 1
        elif tokens[i] in (')', ']', '}'):
            depth -= 1
    return max(depth, 0)


def has_distributable_brackets(expression: str) -> bool:
    """
    Return True if the expression has a bracket group that contains +/- inside
    AND is adjacent to an operator — i.e. distribution is actually meaningful.
    """
    from graph_builder2 import find_distributable_brackets, get_bracket_content
    try:
        tokens = tokenize(expression)
        for dist in find_distributable_brackets(tokens):
            inner = get_bracket_content(tokens, dist['bracket_start'], dist['bracket_end'])
            if any(t in ['+', '-'] for t in inner):
                return True
        return False
    except Exception:
        return False


def is_step_wrong(tokens, mystery_action, expert_walker) -> bool:
    try:
        valid, _ = expert_walker.get_valid_actions_for_state(list(tokens))
        if not valid or not mystery_action:
            return True
        expert_action = valid[0]
        if (mystery_action.action_type == expert_action.action_type
                and mystery_action.operator == expert_action.operator
                and mystery_action.operator_index == expert_action.operator_index):
            return False
        if (mystery_action.action_type == 'evaluate'
                and expert_action.action_type == 'evaluate'
                and mystery_action.operator == expert_action.operator
                and mystery_action.operator in ('+', '*')
                and bracket_depth_at(tokens, mystery_action.operator_index)
                    == bracket_depth_at(tokens, expert_action.operator_index)):
            return False
        return True
    except Exception:
        return True


def build_trace_lines(mystery_steps, expert_walker, show_all=True, show_first_n=None):
    rows = []
    for i, step in enumerate(mystery_steps[:-1]):
        tokens = step.get('tokens', [])
        chosen = step.get('chosen_action')
        next_state = mystery_steps[i + 1]['state']
        wrong = is_step_wrong(tokens, chosen, expert_walker)
        rows.append((step['state'], next_state, wrong))

    if not rows:
        return [display_expr(mystery_steps[0]['state'])] if mystery_steps else []

    visible = rows[:show_first_n] if show_first_n is not None else rows

    lines = [display_expr(visible[0][0])]
    for curr_state, next_state, wrong in visible:
        lines.append("↓")
        lines.append("████████████████████" if wrong else display_expr(next_state))

    if show_first_n is not None and show_first_n < len(rows):
        lines.append("...")
        lines.append(display_expr(mystery_steps[-1]['state']))
    elif show_all and rows and rows[-1][2]:
        lines.append("↓")
        lines.append(display_expr(mystery_steps[-1]['state']))

    return lines


def build_trace_lines_first_wrong(steps, expert_walker):
    """Blank only the FIRST wrong step; show everything else."""
    first_wrong_found = False
    rows = []
    for i, step in enumerate(steps[:-1]):
        tokens = step.get('tokens', [])
        chosen = step.get('chosen_action')
        next_state = steps[i + 1]['state']
        if not first_wrong_found and is_step_wrong(tokens, chosen, expert_walker):
            wrong = True
            first_wrong_found = True
        else:
            wrong = False
        rows.append((step['state'], next_state, wrong))

    if not rows:
        return [display_expr(steps[0]['state'])] if steps else []

    lines = [display_expr(rows[0][0])]
    for curr_state, next_state, wrong in rows:
        lines.append("↓")
        lines.append("████████████████████" if wrong else display_expr(next_state))
    return lines


def build_trace_lines_all_visible(steps):
    """Show every step with nothing blacked out."""
    if not steps:
        return []
    lines = [display_expr(steps[0]['state'])]
    for i in range(len(steps) - 1):
        lines.append("↓")
        lines.append(display_expr(steps[i + 1]['state']))
    return lines


def short_action(action):
    """Strip verb prefix from action description for display."""
    d = action.description.replace('/', '÷')
    for prefix in ('Compute ', 'Distribute ', 'Drop brackets: '):
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d


def describe_step_pair(mystery_action, expert_action):
    """Describe what mystery did vs what expert would do at the same state."""
    m = short_action(mystery_action)
    e = short_action(expert_action) if expert_action else '?'
    if mystery_action.action_type == 'drop_brackets':
        return f"Dropped `{m}` instead of evaluating inside"
    elif mystery_action.action_type == 'distribute':
        return f"Distributed `{m}` instead of evaluating `{e}`"
    else:
        return f"Computed `{m}` before `{e}`"


def find_hidden_step_foil_action(mystery_steps, expert_walker):
    """
    Find the first hidden (wrong) step in mystery's trace.
    At that same state, look for a DIFFERENT wrong action.
    Returns (mystery_action, expert_action, foil_action).
    foil_action is None if no distinct alternative wrong action exists at that state.
    """
    for step in mystery_steps[:-1]:
        tokens = step['tokens']
        chosen = step.get('chosen_action')
        if not is_step_wrong(tokens, chosen, expert_walker):
            continue

        valid, _ = expert_walker.get_valid_actions_for_state(list(tokens))
        expert_action = valid[0] if valid else None

        all_actions = step.get('all_actions', [])
        mystery_idx = chosen.operator_index
        expert_idx = expert_action.operator_index if expert_action else None

        # Wrong actions: not the mystery's and not the expert's
        alternatives = [
            a for a in all_actions
            if a.operator_index != mystery_idx
            and a.operator_index != expert_idx
        ]

        foil_action = random.choice(alternatives) if alternatives else None
        return chosen, expert_action, foil_action

    return None, None, None


def describe_divergences(steps, expert_walker):
    """
    Compare each chosen action against what the expert would do at the same state.
    Returns a plain-English string describing only the divergences that *actually
    occurred* in this trace — including specific examples from the expression.
    """
    found = {}

    def _short(action):
        d = action.description.replace('/', '÷')
        for prefix in ('Compute ', 'Distribute ', 'Drop brackets: '):
            if d.startswith(prefix):
                d = d[len(prefix):]
        return d

    for step in steps[:-1]:
        tokens = step['tokens']
        l = step.get('chosen_action')
        if not l:
            continue
        try:
            valid, _ = expert_walker.get_valid_actions_for_state(list(tokens))
            if not valid:
                continue
            e = valid[0]
        except Exception:
            continue
        if l.action_type == e.action_type and l.operator_index == e.operator_index:
            continue
        l_str = _short(l)
        e_str = _short(e)
        l_idx = l.operator_index if l.operator_index is not None else 0
        e_idx = e.operator_index if e.operator_index is not None else 0
        l_depth = bracket_depth_at(tokens, l_idx)
        e_depth = bracket_depth_at(tokens, e_idx)

        if l.action_type == 'drop_brackets' and 'drop_brackets' not in found:
            found['drop_brackets'] = (
                f"dropped brackets instead of evaluating inside them "
                f"(dropped `{l_str}`)"
            )
        elif l.action_type == 'distribute' and e.action_type != 'distribute' \
                and 'distribute' not in found:
            found['distribute'] = (
                f"expanded brackets by distributing instead of evaluating inside "
                f"(distributed `{l_str}` instead of `{e_str}`)"
            )
        elif l_depth < e_depth and 'skip_brackets' not in found:
            found['skip_brackets'] = (
                f"skipped bracket contents and evaluated outside first "
                f"(chose `{l_str}` instead of `{e_str}`)"
            )
        elif l_depth == e_depth \
                and l.action_type == 'evaluate' and e.action_type == 'evaluate':
            l_prec = BODMAS_PREC.get(l.operator, 0)
            e_prec = BODMAS_PREC.get(e.operator, 0)
            if l_prec < e_prec:
                if l.operator in ('+', '-') and e.operator in ('*', '/') \
                        and 'add_before_mult' not in found:
                    found['add_before_mult'] = (
                        f"did addition/subtraction before multiplication/division "
                        f"(computed `{l_str}` before `{e_str}`)"
                    )
                elif 'wrong_prec' not in found:
                    found['wrong_prec'] = (
                        f"applied operators in the wrong priority order "
                        f"(chose `{l_str}` instead of `{e_str}`)"
                    )
            elif l_prec == e_prec and l_idx != e_idx:
                if l.operator == e.operator and l.operator in ('+', '*'):
                    pass  # associative — order doesn't affect result
                elif l_idx > e_idx and 'right_to_left' not in found:
                    found['right_to_left'] = (
                        f"evaluated right to left instead of left to right "
                        f"(computed `{l_str}` before `{e_str}`)"
                    )
                elif l_idx < e_idx and 'unexpected_order' not in found:
                    found['unexpected_order'] = (
                        f"chose an earlier operation unexpectedly "
                        f"(chose `{l_str}` instead of `{e_str}`)"
                    )

    if not found:
        return "follows the same steps as BODMAS on this expression"
    parts = list(found.values())
    sentence = parts[0].capitalize()
    for p in parts[1:]:
        sentence += f"; also {p}"
    return sentence


NON_EXPERT = [k for k in LEARNER_PROFILES if k not in ('expert', 'bodmas_correct')]

STUDENT_NAMES = ['Ned', 'Emma', 'Emily', 'Jake', 'Julian', 'Bob', 'Mike', 'Jessica']

# 5 fully visible traces, then 5 with wrong steps blacked out
N_FULL_TRACE   = 5
N_BLANKED      = 5


def generate_random_equation():
    """
    Generate a random arithmetic expression guaranteed to:
    - Have at least one * and one +/- (so a precedence conflict exists)
    - Parse cleanly (no division, to avoid messy decimals)
    - Produce a different trace for at least one non-expert learner
    ~50% chance of including a bracketed sub-expression.
    Falls back to '2+3*4' if nothing valid is found after 60 attempts.
    """
    for _ in range(60):
        n    = random.randint(3, 5)
        nums = [str(random.randint(1, 9)) for _ in range(n)]
        ops  = [random.choice(['+', '-', '*']) for _ in range(n - 1)]
        if '*' not in ops:
            ops[random.randrange(len(ops))] = '*'
        if not any(o in ('+', '-') for o in ops):
            ops[random.randrange(len(ops))] = random.choice(['+', '-'])

        use_brackets = (n >= 3) and (random.random() < 0.5)

        if use_brackets:
            blen   = random.randint(2, min(3, n - 1))
            bstart = random.randint(0, n - blen)
            bend   = bstart + blen

            # Ensure +/- inside brackets (interesting for bracket_ignorer/distributor)
            inner_ops = ops[bstart:bend - 1]
            if not any(o in ('+', '-') for o in inner_ops) and inner_ops:
                ops[bstart + random.randrange(len(inner_ops))] = random.choice(['+', '-'])

            # Ensure * adjacent to bracket (real precedence conflict)
            adj_has_mult = (
                (bstart > 0 and ops[bstart - 1] == '*') or
                (bend < n   and ops[bend - 1]   == '*')
            )
            if not adj_has_mult:
                if bstart > 0:
                    ops[bstart - 1] = '*'
                else:
                    ops[bend - 1] = '*'

            parts = []
            for i in range(n):
                if i == bstart:
                    parts.append('(')
                parts.append(nums[i])
                if i == bend - 1:
                    parts.append(')')
                if i < len(ops):
                    parts.append(ops[i])
            expr = ''.join(parts)
        else:
            parts = []
            for i, num in enumerate(nums):
                parts.append(num)
                if i < len(ops):
                    parts.append(ops[i])
            expr = ''.join(parts)

        try:
            tokenize(expr)
        except Exception:
            continue

        # Require at least one non-expert learner to diverge from expert
        try:
            expert_states = [s['state'] for s in get_learner_trace(expr, 'expert')]
            check_learners = ['addition_first', 'left_to_right_only', 'right_to_left']
            if any(c in expr for c in '([{'):
                check_learners.append('bracket_ignorer')
            for name in check_learners:
                try:
                    if [s['state'] for s in get_learner_trace(expr, name)] != expert_states:
                        return expr
                except Exception:
                    continue
        except Exception:
            continue

    return '2+3*4'  # safe fallback


def pick_mystery(all_results, expression, expert_walker):
    """
    Pick a mystery learner whose mistake is actually visible/describable.
    Excludes learners whose only divergence is in associative operator order
    (those get described as BODMAS-identical and aren't useful as mystery learners).
    """
    has_any_brackets, has_dist = expression_filters(expression)
    expert_states = [s['state'] for s in all_results['expert']['steps']]

    candidates = [
        k for k in NON_EXPERT
        if all_results[k]['answer'] != 'Error'
        and [s['state'] for s in all_results[k]['steps']] != expert_states
        and describe_divergences(all_results[k]['steps'], expert_walker) != BODMAS_IDENTICAL
    ]
    candidates = apply_visibility_filters(candidates, has_any_brackets, has_dist)
    return random.choice(candidates) if candidates else None


def expression_filters(expression):
    """Return (has_any_brackets, has_dist) for filtering learner candidates."""
    has_any_brackets = any(c in expression for c in '([{')
    has_dist = has_distributable_brackets(expression)
    return has_any_brackets, has_dist


def apply_visibility_filters(pool, has_any_brackets, has_dist):
    """
    Remove learners whose defining behaviour is invisible in this expression.
    - bracket_ignorer: only meaningful when brackets exist
    - distributor: only meaningful when distributable brackets (+/- inside) exist
    - multiplication_first: misleading when brackets exist but aren't distributable
    """
    if not has_any_brackets:
        pool = [k for k in pool if k != 'bracket_ignorer']
    if not has_dist:
        pool = [k for k in pool if k != 'distributor']
    if has_any_brackets and not has_dist:
        pool = [k for k in pool if k != 'multiplication_first']
    return pool


BODMAS_IDENTICAL = "follows the same steps as BODMAS on this expression"


def pick_foil(mystery, all_results, expert_walker, expression, fmt=None):
    """
    Pick a foil learner. Returns None if no valid foil exists (so the caller
    can reject the expression and try a new one).
    A valid foil must:
      - NOT follow the same steps as BODMAS on this expression
      - have a displayed description different from the mystery's displayed description
        (for full_trace, descriptions are stripped of examples before comparing)
    """
    def displayed_desc(k):
        full = describe_divergences(all_results[k]['steps'], expert_walker)
        if fmt == 'full_trace':
            idx = full.find(' (')
            primary = full.split('; also ')[0]
            return primary[:primary.find(' (')] if primary.find(' (') != -1 else primary
        return full

    has_any_brackets, has_dist = expression_filters(expression)

    mystery_states = [s['state'] for s in all_results[mystery]['steps']]
    mystery_desc = displayed_desc(mystery)

    candidates = [k for k in NON_EXPERT if k != mystery and all_results[k]['answer'] != 'Error']
    candidates = apply_visibility_filters(candidates, has_any_brackets, has_dist)

    # Must diverge from BODMAS
    candidates = [
        k for k in candidates
        if describe_divergences(all_results[k]['steps'], expert_walker) != BODMAS_IDENTICAL
    ]

    # Prefer different trace from mystery
    diff_trace = [k for k in candidates if [s['state'] for s in all_results[k]['steps']] != mystery_states]
    pool = diff_trace if diff_trace else candidates

    if not pool:
        return None

    # Must display a different description from mystery
    diff_desc = [k for k in pool if displayed_desc(k) != mystery_desc]
    if not diff_desc:
        return None
    return random.choice(diff_desc)


def generate_trial(idx, expression, mystery_learner, fmt, all_results=None, foil=None, student_name=None):
    if all_results is None:
        all_results = {}
        for name in LEARNER_PROFILES:
            try:
                steps = get_learner_trace(expression, name)
                all_results[name] = {'steps': steps, 'answer': get_final_answer(steps)}
            except Exception:
                all_results[name] = {'steps': [], 'answer': 'Error'}

    mystery_steps = all_results[mystery_learner]['steps']
    final_answer = all_results[mystery_learner]['answer']

    expert_learner = create_learner('expert')
    expert_walker = LearnerGraphWalker(expression, expert_learner)

    if fmt == 'full_trace':
        trace_lines = build_trace_lines_all_visible(mystery_steps)

        if foil is None:
            foil = pick_foil(mystery_learner, all_results, expert_walker, expression, fmt=fmt)

        def strip_examples(description):
            clauses = description.split('; also ')
            stripped = []
            for clause in clauses:
                idx = clause.find(' (')
                stripped.append(clause[:idx] if idx != -1 else clause)
            return '; also '.join(stripped)

        options_keys = [mystery_learner, foil]
        random.shuffle(options_keys)
        options = [
            {
                'key': k,
                'label': DIAG_LEARNER_LABELS.get(k, k),
                'description': strip_examples(
                    describe_divergences(all_results[k]['steps'], expert_walker)
                ),
            }
            for k in options_keys
        ]

    elif fmt == 'blanked_wrong':
        trace_lines = build_trace_lines_first_wrong(mystery_steps, expert_walker)

        # Describe what happened at the specific hidden step,
        # not what the foil learner did on its own trace
        mystery_action, expert_action, foil_action = find_hidden_step_foil_action(
            mystery_steps, expert_walker
        )

        mystery_desc = describe_step_pair(mystery_action, expert_action) if mystery_action else '?'
        foil_desc    = describe_step_pair(foil_action,    expert_action) if foil_action    else '?'

        options = [
            {'key': mystery_learner, 'label': DIAG_LEARNER_LABELS.get(mystery_learner, mystery_learner), 'description': mystery_desc},
            {'key': 'foil',          'label': 'Other',                                                    'description': foil_desc},
        ]
        random.shuffle(options)

    else:
        trace_lines = []
        options = []

    return {
        'id':          idx + 1,
        'expression':  display_expr(expression),
        'format':      fmt,
        'studentName': student_name or random.choice(STUDENT_NAMES),
        'traceLines':  trace_lines,
        'finalAnswer': final_answer,
        'options':     options,
        'correctKey':  mystery_learner,
    }


def generate_block(fmt, n, seen_expressions, start_idx):
    """Generate n trials of a given format, avoiding already-used expressions."""
    trials = []
    idx = start_idx
    while len(trials) < n:
        expr = generate_random_equation()
        if expr in seen_expressions:
            continue
        seen_expressions.add(expr)

        all_results = {}
        for name in LEARNER_PROFILES:
            try:
                steps = get_learner_trace(expr, name)
                all_results[name] = {'steps': steps, 'answer': get_final_answer(steps)}
            except Exception:
                all_results[name] = {'steps': [], 'answer': 'Error'}

        expert_walker = LearnerGraphWalker(expr, create_learner('expert'))
        mystery = pick_mystery(all_results, expr, expert_walker)
        if mystery is None:
            continue

        if fmt == 'blanked_wrong':
            # For blanked trials, check that a distinct alternative wrong action
            # exists at the hidden step — otherwise the foil would be meaningless
            mystery_steps = all_results[mystery]['steps']
            m_action, e_action, foil_action = find_hidden_step_foil_action(
                mystery_steps, expert_walker
            )
            if foil_action is None:
                continue
            foil = None  # generate_trial will call find_hidden_step_foil_action again
            print(f"  Trial {idx + 1}: {expr} ({mystery}, {fmt})")
        else:
            foil = pick_foil(mystery, all_results, expert_walker, expr, fmt=fmt)
            if foil is None:
                continue
            print(f"  Trial {idx + 1}: {expr} ({mystery} vs {foil}, {fmt})")

        trial = generate_trial(idx, expr, mystery, fmt, all_results=all_results, foil=foil)
        trials.append(trial)
        idx += 1
    return trials


# ---------------------------------------------------------------------------
# Hardcoded advice-opinion trials
# advice_type: 'strategic' | 'step_specific' | 'irrelevant'
# 2 strategic + 2 step_specific + 1 irrelevant = 5 trials
# ---------------------------------------------------------------------------
ADVICE_TRIAL_SPECS = [
    {
        'expression':      '3+2*5',
        'mystery_learner': 'addition_first',
        'student_name':    'Ned',
        'advice_type':     'strategic',
        'advice':          'Multiplication and division should always be done before addition and subtraction.',
    },
    {
        'expression':      '2+3*4',
        'mystery_learner': 'addition_first',
        'student_name':    'Emma',
        'advice_type':     'step_specific',
        'advice':          'Three times four equals twelve.',
    },
    {
        'expression':      '12-3+4',
        'mystery_learner': 'right_to_left',
        'student_name':    'Sam',
        'advice_type':     'strategic',
        'advice':          'When two operatores with the same priority appear next to each other, always work from left to right.',
    },
    {
        'expression':      '5+3*2',
        'mystery_learner': 'addition_first',
        'student_name':    'Alex',
        'advice_type':     'step_specific',
        'advice':          'Three times two equals six — so the expression becomes 5+6, not 8×2.',
    },
    {
        'expression':      '4+2*3',
        'mystery_learner': 'addition_first',
        'student_name':    'Jordan',
        'advice_type':     'irrelevant',
        'advice':          'Make sure to write each step neatly and double-check your arithmetic.',
    },
]


def generate_advice_trial(idx, spec):
    expression    = spec['expression']
    mystery       = spec['mystery_learner']
    student_name  = spec['student_name']
    advice        = spec['advice']
    advice_type   = spec['advice_type']

    steps = get_learner_trace(expression, mystery)
    trace_lines = build_trace_lines_all_visible(steps)
    final_answer = get_final_answer(steps)

    options = [
        {'key': 'yes', 'label': 'Yes', 'description': ''},
        {'key': 'no',  'label': 'No',  'description': ''},
    ]
    random.shuffle(options)

    return {
        'id':           idx + 1,
        'format':       'advice_opinion',
        'expression':   display_expr(expression),
        'traceLines':   trace_lines,
        'finalAnswer':  final_answer,
        'studentName':  student_name,
        'advice':       advice,
        'adviceType':   advice_type,
        'options':      options,
        'correctKey':   None,
    }


# ---------------------------------------------------------------------------
# Hardcoded advice-slider trials (trials 16–20)
# Longer expressions with 2+ multiplications so multiple mistakes occur.
# advice_type: 'first_misconception' | 'last_error_specific' | 'irrelevant'
#            | 'step_specific'       | 'strategic'
# ---------------------------------------------------------------------------
ADVICE_SLIDER_SPECS = [
    {
        # Two *-operations; addition_first makes a mistake before each one.
        # Advice points at the FIRST misconception (the very first wrong move).
        'expression':      '1+2*3+4*5',
        'mystery_learner': 'addition_first',
        'student_name':    'Taylor',
        'advice_type':     'first_misconception',
        'advice':          (
            'The very first thing to look for in any expression is a × or ÷ sign. '
        ),
    },
    {
        # Three operations; advice calls out the LAST multiplication specifically.
        'expression':      '8-3*2+5*4-1',
        'mystery_learner': 'addition_first',
        'student_name':    'Morgan',
        'advice_type':     'last_error_specific',
        'advice':          (
            'make sure that multiplication is done '
            'before you add or subtract anything around it.'
        ),
    },
    {
        # Advice is completely unrelated to the actual mistake.
        'expression':      '2+3*4-1+5*2',
        'mystery_learner': 'addition_first',
        'student_name':    'Casey',
        'advice_type':     'irrelevant',
        'advice':          (
            'Try reading the expression out loud before writing anything down — '
            'it can help you spot simple typos.'
        ),
    },
    {
        # Pinpoints one specific multiplication that the learner got wrong.
        'expression':      '6-1*3+4*5',
        'mystery_learner': 'addition_first',
        'student_name':    'Riley',
        'advice_type':     'step_specific',
        'advice':          (
            '1 × 3 = 3, so the first part of the expression is 6 − 3, not 5 × 3.'
        ),
    },
    {
        # High-level strategic rule covering the whole misconception.
        'expression':      '3+2*4+1*5-2',
        'mystery_learner': 'addition_first',
        'student_name':    'Quinn',
        'advice_type':     'strategic',
        'advice':          (
            'Multiplication and division always come before addition and subtraction. '
            'Scan the entire expression for every × and ÷ sign and deal with all of '
            'them before touching any + or −.'
        ),
    },
]


def generate_advice_slider_trial(idx, spec):
    expression   = spec['expression']
    mystery      = spec['mystery_learner']
    student_name = spec['student_name']
    advice       = spec['advice']
    advice_type  = spec['advice_type']

    steps = get_learner_trace(expression, mystery)
    trace_lines = build_trace_lines_all_visible(steps)
    final_answer = get_final_answer(steps)

    return {
        'id':          idx + 1,
        'format':      'advice_slider',
        'expression':  display_expr(expression),
        'traceLines':  trace_lines,
        'finalAnswer': final_answer,
        'studentName': student_name,
        'advice':      advice,
        'adviceType':  advice_type,
        'options':     [],   # slider replaces option buttons
        'correctKey':  None,
    }


def main():
    out_dir = os.path.dirname(__file__)

    # ── Type-1 trials: load trial_bank.json → write trials.json ──────────────
    bank_path = os.path.join(out_dir, 'trial_bank.json')
    with open(bank_path) as f:
        trials = json.load(f)

    # Re-index 1..N
    for i, t in enumerate(trials):
        t['id'] = i + 1

    out_path = os.path.join(out_dir, 'trials.json')
    with open(out_path, 'w') as f:
        json.dump(trials, f, indent=2)

    pool_counts = {p: sum(1 for t in trials if t['pool'] == p) for p in ['A', 'B', 'C', 'D']}
    print(f"Type-1: {len(trials)} trials  "
          f"(A={pool_counts['A']} B={pool_counts['B']} C={pool_counts['C']} D={pool_counts['D']})")
    print(f"  → {out_path}")

    # ── Type-3 trials: load advice_bank.json → write advice_trials.json ───────
    advice_bank_path = os.path.join(out_dir, 'advice_bank.json')
    with open(advice_bank_path) as f:
        advice_trials = json.load(f)

    for i, t in enumerate(advice_trials):
        t['id'] = i + 1

    advice_out_path = os.path.join(out_dir, 'advice_trials.json')
    with open(advice_out_path, 'w') as f:
        json.dump(advice_trials, f, indent=2)

    adv_counts = {p: sum(1 for t in advice_trials if t['pool'] == p) for p in ['A', 'B', 'C', 'D']}
    print(f"Type-3: {len(advice_trials)} advice trials  "
          f"(A={adv_counts['A']} B={adv_counts['B']} C={adv_counts['C']} D={adv_counts['D']})")
    print(f"  → {advice_out_path}")


if __name__ == '__main__':
    main()
