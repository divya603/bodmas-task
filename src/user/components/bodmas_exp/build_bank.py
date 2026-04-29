"""
Build trial_bank.json — 20 hardcoded, pre-verified expressions.

Pool A ( 5, correctKey='yes'):  correct description shown — 1 misconception.
                                 All 5 shown to every participant.
Pool B ( 5, correctKey='no'):   foil (wrong) description shown — 1 misconception.
                                 Every participant sees all 5.
Pool C ( 5, correctKey='yes'):  2 misconceptions; inference points to the 1ST error.
                                 Every participant sees all 5.
Pool D ( 5, correctKey='yes'):  2 misconceptions; inference points to the 2ND error.
                                 Every participant sees all 5.

Per-participant trial count: 5 (A) + 5 (B) + 5 (C) + 5 (D) = 20 trials.

Analysis flags on every trial
──────────────────────────────
has_misconception        bool   — trace contains at least one error
has_1_misconception      bool   — exactly one misconception (false for C/D)
misconception_types      list   — ordered codes of errors visible in the trace
inference_target         str    — which misconception code the shown description names
right_inference          bool   — inference_target is in misconception_types
inference_points_to_first bool|null — C→True, D→False, A/B→null

Misconception codes
───────────────────
add_before_mult   — did +/- before ×/÷
bracket_drop      — dropped brackets entirely
bracket_distribute — distributed brackets the wrong way
bracket_skip      — evaluated outside brackets before resolving inside
same_prio_rtl     — two same-priority ops; went right-to-left
left_to_right     — ignored all precedence, strict left-to-right

Run: python build_bank.py
"""

import os, json, random

random.seed(42)

# All traces verified by hand.
# Trace format: alternating [expression, '↓', expression, ...] — the ↓ is the
# step separator rendered by BodmasTrialView.vue.
BANK_DATA = [

    # ═══════════════════════════════════════════════════════════════════════════
    # Pool A — 15 trials — correct description shown, answer = Yes
    # Each participant draws 10 at random from this pool.
    # ═══════════════════════════════════════════════════════════════════════════

    # ── addition_first learner ──────────────────────────────────────────────
    {
        'expr':              '(2+3)*5+1',
        'learner':           'addition_first',
        'pool':              'A',
        'trace':             ['(2+3)×5+1', '↓', '5×5+1', '↓', '5×6', '↓', '30'],
        'learnerAns':        '30',
        'expertAns':         '26',
        'correct_desc':      'doing addition before multiplication',
        'foil_desc':         None,
        'student':           'Ned',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'add_before_mult',
    },
    {
        'expr':              '(6-2)*3+4*2',
        'learner':           'addition_first',
        'pool':              'A',
        'trace':             ['(6-2)×3+4×2', '↓', '4×3+4×2', '↓', '4×7×2', '↓', '28×2', '↓', '56'],
        'learnerAns':        '56',
        'expertAns':         '20',
        'correct_desc':      'doing addition before multiplication',
        'foil_desc':         None,
        'student':           'Emily',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'add_before_mult',
    },
    # ── left_to_right_only learner ──────────────────────────────────────────
    {
        'expr':              '4*2*3+5*2',
        'learner':           'left_to_right_only',
        'pool':              'A',
        'trace':             ['4×2×3+5×2', '↓', '8×3+5×2', '↓', '24+5×2', '↓', '29×2', '↓', '58'],
        'learnerAns':        '58',
        'expertAns':         '34',
        'correct_desc':      'doing all operations strictly left to right, ignoring operator priority',
        'foil_desc':         None,
        'student':           'Mike',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'add_before_mult',
    },
    # ── right_to_left learner ───────────────────────────────────────────────
    {
        'expr':              '8-3+2*5',
        'learner':           'right_to_left',
        'pool':              'A',
        'trace':             ['8-3+2×5', '↓', '8-3+10', '↓', '8-13', '↓', '-5'],
        'learnerAns':        '-5',
        'expertAns':         '15',
        'correct_desc':      'evaluating the expression right to left, without considering operator priority',
        'foil_desc':         None,
        'student':           'Morgan',
        'misconception_types': ['same_prio_rtl'],
        'inference_target':  'same_prio_rtl',
    },
    # ── bracket_ignorer learner ─────────────────────────────────────────────
    {
        'expr':              '5*(3+4)-2',
        'learner':           'bracket_ignorer',
        'pool':              'A',
        'trace':             ['5×(3+4)-2', '↓', '5×3+4-2', '↓', '15+4-2', '↓', '19-2', '↓', '17'],
        'learnerAns':        '17',
        'expertAns':         '33',
        'correct_desc':      'ignoring the brackets and computing as if they weren\'t there',
        'foil_desc':         None,
        'student':           'Riley',
        'misconception_types': ['bracket_drop'],
        'inference_target':  'bracket_drop',
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Pool B — 5 trials — foil (wrong) description shown, answer = No
    # Every participant sees all 5.
    # ═══════════════════════════════════════════════════════════════════════════
    {
        'expr':              '(4+3)*2+5*1',
        'learner':           'addition_first',
        'pool':              'B',
        'trace':             ['(4+3)×2+5×1', '↓', '7×2+5×1', '↓', '7×7×1', '↓', '49×1', '↓', '49'],
        'learnerAns':        '49',
        'expertAns':         '19',
        'correct_desc':      'doing addition/subtraction before multiplication/division',
        'foil_desc':         'evaluating strictly left to right, ignoring operator priority',
        'student':           'Quinn',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'same_prio_rtl',   # foil names RTL
    },
    {
        'expr':              '6*(2+1)-3*4',
        'learner':           'addition_first',
        'pool':              'B',
        'trace':             ['6×(2+1)-3×4', '↓', '6×3-3×4', '↓', '6×0×4', '↓', '0×4', '↓', '0'],
        'learnerAns':        '0',
        'expertAns':         '6',
        'correct_desc':      'doing addition/subtraction before multiplication/division',
        'foil_desc':         'dropping the brackets and evaluating as if they weren\'t there',
        'student':           'Pat',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'bracket_drop',   # foil names bracket-drop
    },
    {
        'expr':              '6*3+4-2*3',
        'learner':           'left_to_right_only',
        'pool':              'B',
        'trace':             ['6×3+4-2×3', '↓', '18+4-2×3', '↓', '22-2×3', '↓', '20×3', '↓', '60'],
        'learnerAns':        '60',
        'expertAns':         '16',
        'correct_desc':      'doing addition/subtraction before multiplication/division',
        'foil_desc':         'evaluating strictly right to left, ignoring operator priority',
        'student':           'Drew',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'same_prio_rtl',   # foil names RTL
    },
    {
        'expr':              '9-4+2*3',
        'learner':           'right_to_left',
        'pool':              'B',
        'trace':             ['9-4+2×3', '↓', '9-4+6', '↓', '9-10', '↓', '-1'],
        'learnerAns':        '-1',
        'expertAns':         '11',
        'correct_desc':      'evaluating right to left',
        'foil_desc':         'doing addition before multiplication',
        'student':           'Lee',
        'misconception_types': ['same_prio_rtl'],
        'inference_target':  'add_before_mult',   # foil names add-before-mult
    },
    {
        'expr':              '4*(2+3)-1',
        'learner':           'bracket_ignorer',
        'pool':              'B',
        'trace':             ['4×(2+3)-1', '↓', '4×2+3-1', '↓', '8+3-1', '↓', '11-1', '↓', '10'],
        'learnerAns':        '10',
        'expertAns':         '19',
        'correct_desc':      'dropping the brackets as if they weren\'t there',
        'foil_desc':         'expanding the brackets instead of evaluating inside them first',
        'student':           'Chris',
        'misconception_types': ['bracket_drop'],
        'inference_target':  'bracket_distribute',   # foil names bracket-distribute
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Pool C — 5 trials — 2 misconceptions; inference points to the 1ST error.
    # right_inference = True (the description is accurate — it names the 1st error).
    # Every participant sees all 5.
    # ═══════════════════════════════════════════════════════════════════════════

    # C1 — add_before_mult (1st) → bracket_drop (2nd)
    # Learner first sums 2+3=5 outside then drops (3+7) brackets.
    # Expert: 2 + 3×6×10 = 182
    {
        'expr':              '2+3*6*(3+7)',
        'learner':           'compound_add_bracket_drop',
        'pool':              'C',
        'trace':             [
            '2+3×6×(3+7)', '↓',
            '5×6×(3+7)',   '↓',   # ERROR 1: 2+3=5 (add_before_mult)
            '5×6×3+7',     '↓',   # ERROR 2: dropped (3+7) (bracket_drop)
            '30×3+7',      '↓',
            '90+7',        '↓',
            '97',
        ],
        'learnerAns':        '97',
        'expertAns':         '182',
        'desc_shown':        'doing addition before multiplication',
        'student':           'Noah',
        'misconception_types': ['add_before_mult', 'bracket_drop'],
        'inference_target':  'add_before_mult',
    },

    # C2 — add_before_mult (1st) → bracket_drop (2nd)
    # Expert: 3 + 2×4×3 = 27
    {
        'expr':              '3+2*4*(5-2)',
        'learner':           'compound_add_bracket_drop',
        'pool':              'C',
        'trace':             [
            '3+2×4×(5-2)', '↓',
            '5×4×(5-2)',   '↓',   # ERROR 1: 3+2=5 (add_before_mult)
            '5×4×5-2',     '↓',   # ERROR 2: dropped (5-2) (bracket_drop)
            '20×5-2',      '↓',
            '100-2',       '↓',
            '98',
        ],
        'learnerAns':        '98',
        'expertAns':         '27',
        'desc_shown':        'doing addition before multiplication',
        'student':           'Olivia',
        'misconception_types': ['add_before_mult', 'bracket_drop'],
        'inference_target':  'add_before_mult',
    },

    # C3 — bracket_drop (1st) → add_before_mult (2nd)
    # Student drops brackets around (2×3), then adds 4+2 before multiplying.
    # Expert: 4+(2×3)-5+1 = 4+6-5+1 = 6
    {
        'expr':              '4+(2*3)-5+1',
        'learner':           'compound_bracket_add',
        'pool':              'C',
        'trace':             [
            '4+(2×3)-5+1', '↓',
            '4+2×3-5+1',   '↓',   # ERROR 1: dropped brackets (bracket_drop)
            '6×3-5+1',     '↓',   # ERROR 2: 4+2=6 (add_before_mult)
            '18-5+1',      '↓',
            '13+1',        '↓',
            '14',
        ],
        'learnerAns':        '14',
        'expertAns':         '6',
        'desc_shown':        'ignoring the brackets and computing as if they weren\'t there',
        'student':           'Lily',
        'misconception_types': ['add_before_mult', 'bracket_drop'],
        'inference_target':  'add_before_mult',
    },

    # C4 — add_before_mult (1st) → same_prio_rtl (2nd)
    # Expert: 3+10-4+2 = 11
    {
        'expr':              '3+5*2-4+2',
        'learner':           'compound_add_rtl',
        'pool':              'C',
        'trace':             [
            '3+5×2-4+2', '↓',
            '8×2-4+2',   '↓',   # ERROR 1: 3+5=8 (add_before_mult)
            '16-4+2',    '↓',
            '16-6',      '↓',   # ERROR 2: 4+2=6 before 16-4 (same_prio_rtl)
            '10',
        ],
        'learnerAns':        '10',
        'expertAns':         '11',
        'desc_shown':        'doing addition before multiplication',
        'student':           'Mia',
        'misconception_types': ['add_before_mult', 'same_prio_rtl'],
        'inference_target':  'add_before_mult',
    },

    # C5 — same_prio_rtl (1st) → add_before_mult (2nd)
    # Expert: 6-2+12 = 16
    {
        'expr':              '6-2+3*4',
        'learner':           'compound_rtl_add',
        'pool':              'C',
        'trace':             [
            '6-2+3×4', '↓',
            '6-5×4',   '↓',   # ERROR 1: 2+3=5 right-to-left (same_prio_rtl)
            '1×4',     '↓',   # ERROR 2: 6-5=1 before 5×4 (add_before_mult)
            '4',
        ],
        'learnerAns':        '4',
        'expertAns':         '16',
        'desc_shown':        'evaluating right to left when there are multiple operators of the same priority',
        'student':           'Owen',
        'misconception_types': ['same_prio_rtl', 'add_before_mult'],
        'inference_target':  'same_prio_rtl',
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Pool D — 5 trials — 2 misconceptions; inference points to the 2ND error.
    # right_inference = True (the description is accurate — it names the 2nd error).
    # Every participant sees all 5.
    # ═══════════════════════════════════════════════════════════════════════════

    # D1 — add_before_mult (1st) → bracket_drop (2nd)
    # Expert: 1 + 4×5×8 = 161
    {
        'expr':              '1+4*5*(2+6)',
        'learner':           'compound_add_bracket_drop',
        'pool':              'D',
        'trace':             [
            '1+4×5×(2+6)', '↓',
            '5×5×(2+6)',   '↓',   # ERROR 1: 1+4=5 (add_before_mult)
            '5×5×2+6',     '↓',   # ERROR 2: dropped (2+6) (bracket_drop)
            '25×2+6',      '↓',
            '50+6',        '↓',
            '56',
        ],
        'learnerAns':        '56',
        'expertAns':         '161',
        'desc_shown':        'dropping the brackets and computing as if they weren\'t there',
        'student':           'Zoe',
        'misconception_types': ['add_before_mult', 'bracket_drop'],
        'inference_target':  'bracket_drop',
    },

    # D2 — add_before_mult (1st) → bracket_drop (2nd)
    # Expert: 4 + 1×3×2 = 10
    {
        'expr':              '4+1*3*(6-4)',
        'learner':           'compound_add_bracket_drop',
        'pool':              'D',
        'trace':             [
            '4+1×3×(6-4)', '↓',
            '5×3×(6-4)',   '↓',   # ERROR 1: 4+1=5 (add_before_mult)
            '5×3×6-4',     '↓',   # ERROR 2: dropped (6-4) (bracket_drop)
            '15×6-4',      '↓',
            '90-4',        '↓',
            '86',
        ],
        'learnerAns':        '86',
        'expertAns':         '10',
        'desc_shown':        'dropping the brackets and computing as if they weren\'t there',
        'student':           'Liam',
        'misconception_types': ['add_before_mult', 'bracket_drop'],
        'inference_target':  'bracket_drop',
    },

    # D3 — add_before_mult (1st) → same_prio_rtl (2nd)
    # Expert: 6+5-3+2 = 10
    {
        'expr':              '6+1*5-3+2',
        'learner':           'compound_add_rtl',
        'pool':              'D',
        'trace':             [
            '6+1×5-3+2', '↓',
            '7×5-3+2',   '↓',   # ERROR 1: 6+1=7 (add_before_mult)
            '35-3+2',    '↓',
            '35-5',      '↓',   # ERROR 2: 3+2=5 before 35-3 (same_prio_rtl)
            '30',
        ],
        'learnerAns':        '30',
        'expertAns':         '10',
        'desc_shown':        'evaluating right to left when there are multiple operators of the same priority',
        'student':           'Ella',
        'misconception_types': ['add_before_mult', 'same_prio_rtl'],
        'inference_target':  'same_prio_rtl',
    },

    # D4 — add_before_mult (1st) → same_prio_rtl (2nd)
    # Expert: 2+12-6+3 = 11
    {
        'expr':              '2+4*3-6+3',
        'learner':           'compound_add_rtl',
        'pool':              'D',
        'trace':             [
            '2+4×3-6+3', '↓',
            '6×3-6+3',   '↓',   # ERROR 1: 2+4=6 (add_before_mult)
            '18-6+3',    '↓',
            '18-9',      '↓',   # ERROR 2: 6+3=9 before 18-6 (same_prio_rtl)
            '9',
        ],
        'learnerAns':        '9',
        'expertAns':         '11',
        'desc_shown':        'evaluating right to left when there are multiple operators of the same priority',
        'student':           'Finn',
        'misconception_types': ['add_before_mult', 'same_prio_rtl'],
        'inference_target':  'same_prio_rtl',
    },

    # D5 — same_prio_rtl (1st) → add_before_mult (2nd)
    # Expert: 7-2+15 = 20
    {
        'expr':              '7-2+3*5',
        'learner':           'compound_rtl_add',
        'pool':              'D',
        'trace':             [
            '7-2+3×5', '↓',
            '7-5×5',   '↓',   # ERROR 1: 2+3=5 right-to-left (same_prio_rtl)
            '2×5',     '↓',   # ERROR 2: 7-5=2 before 5×5 (add_before_mult)
            '10',
        ],
        'learnerAns':        '10',
        'expertAns':         '20',
        'desc_shown':        'doing addition/subtraction before multiplication/division',
        'student':           'Nora',
        'misconception_types': ['same_prio_rtl', 'add_before_mult'],
        'inference_target':  'add_before_mult',
    },
]


# =============================================================================
# ADVICE BANK — 20 trials, format = 'advice_slider'
#
# Same pool structure as Type 1:
#   Pool A ( 5): advice correctly targets the single misconception
#   Pool B ( 5): advice targets the WRONG misconception (foil)
#   Pool C ( 5): 2 misconceptions; advice targets the 1ST error
#   Pool D ( 5): 2 misconceptions; advice targets the 2ND error
#
# All 20 are shown to every participant (no sampling).
# =============================================================================

ADVICE_BANK_DATA = [

    # ── Pool A — correct advice (5 trials) ────────────────────────────────────
    {
        'expr':              '5+2*3',
        'learner':           'addition_first',
        'pool':              'A',
        'trace':             ['5+2×3', '↓', '7×3', '↓', '21'],
        'learnerAns':        '21',
        'expertAns':         '11',
        'advice':            'Multiplication must be done before addition — always calculate × or ÷ before + or −.',
        'advice_type':       'correct',
        'student':           'Ava',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'add_before_mult',
    },
    {
        'expr':              '7-4+2*5',
        'learner':           'left_to_right_only',
        'pool':              'A',
        'trace':             ['7-4+2×5', '↓', '3+2×5', '↓', '5×5', '↓', '25'],
        'learnerAns':        '25',
        'expertAns':         '13',
        'advice':            'Even when working left to right, × must jump the queue — calculate all multiplications before any additions.',
        'advice_type':       'correct',
        'student':           'Ben',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'add_before_mult',
    },
    {
        'expr':              '9-5+3*2',
        'learner':           'right_to_left',
        'pool':              'A',
        'trace':             ['9-5+3×2', '↓', '9-5+6', '↓', '9-11', '↓', '-2'],
        'learnerAns':        '-2',
        'expertAns':         '10',
        'advice':            'When + and − appear one after another, always tackle the leftmost one first — work left to right.',
        'advice_type':       'correct',
        'student':           'Cora',
        'misconception_types': ['same_prio_rtl'],
        'inference_target':  'same_prio_rtl',
    },
    {
        'expr':              '3*(5+2)-4',
        'learner':           'bracket_ignorer',
        'pool':              'A',
        'trace':             ['3×(5+2)-4', '↓', '3×5+2-4', '↓', '15+2-4', '↓', '17-4', '↓', '13'],
        'learnerAns':        '13',
        'expertAns':         '17',
        'advice':            'Brackets mean "do this first" — always work out everything inside the brackets before touching anything outside.',
        'advice_type':       'correct',
        'student':           'Dan',
        'misconception_types': ['bracket_drop'],
        'inference_target':  'bracket_drop',
    },
    {
        'expr':              '4+1*6+2',
        'learner':           'addition_first',
        'pool':              'A',
        'trace':             ['4+1×6+2', '↓', '5×6+2', '↓', '5×8', '↓', '40'],
        'learnerAns':        '40',
        'expertAns':         '12',
        'advice':            'Scan the whole expression for × signs and deal with all of them before doing any + or −.',
        'advice_type':       'correct',
        'student':           'Eva',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'add_before_mult',
    },

    # ── Pool B — wrong advice, doesn't match the actual misconception (5) ──────
    {
        'expr':              '3+4*2',
        'learner':           'addition_first',
        'pool':              'B',
        'trace':             ['3+4×2', '↓', '7×2', '↓', '14'],
        'learnerAns':        '14',
        'expertAns':         '11',
        'advice':            'Work from right to left — start with the last operation in the expression.',
        'advice_type':       'wrong',
        'student':           'Finn',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'same_prio_rtl',    # foil: advice is about RTL
    },
    {
        'expr':              '5+2*4+3',
        'learner':           'addition_first',
        'pool':              'B',
        'trace':             ['5+2×4+3', '↓', '7×4+3', '↓', '7×7', '↓', '49'],
        'learnerAns':        '49',
        'expertAns':         '16',
        'advice':            'Make sure to always work out what is inside the brackets before anything else.',
        'advice_type':       'wrong',
        'student':           'Grace',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'bracket_drop',     # foil: no brackets in expression
    },
    {
        'expr':              '8-3+1*4',
        'learner':           'right_to_left',
        'pool':              'B',
        'trace':             ['8-3+1×4', '↓', '8-3+4', '↓', '8-7', '↓', '1'],
        'learnerAns':        '1',
        'expertAns':         '9',
        'advice':            'Multiplication always comes before addition and subtraction — calculate all × first.',
        'advice_type':       'wrong',
        'student':           'Henry',
        'misconception_types': ['same_prio_rtl'],
        'inference_target':  'add_before_mult',  # foil: actual issue is RTL not × order
    },
    {
        'expr':              '4*(3+1)-2',
        'learner':           'bracket_ignorer',
        'pool':              'B',
        'trace':             ['4×(3+1)-2', '↓', '4×3+1-2', '↓', '12+1-2', '↓', '13-2', '↓', '11'],
        'learnerAns':        '11',
        'expertAns':         '14',
        'advice':            'When operators have the same level, always work left to right.',
        'advice_type':       'wrong',
        'student':           'Iris',
        'misconception_types': ['bracket_drop'],
        'inference_target':  'same_prio_rtl',    # foil: actual issue is bracket dropping
    },
    {
        'expr':              '6-1*3+2',
        'learner':           'left_to_right_only',
        'pool':              'B',
        'trace':             ['6-1×3+2', '↓', '5×3+2', '↓', '15+2', '↓', '17'],
        'learnerAns':        '17',
        'expertAns':         '5',
        'advice':            'Always double-check each calculation step by writing it out neatly.',
        'advice_type':       'wrong',
        'student':           'Jake',
        'misconception_types': ['add_before_mult'],
        'inference_target':  'bracket_skip',     # foil: irrelevant advice
    },

    # ── Pool C — 2 misconceptions; advice targets the 1ST error ───────────────
    # Reuses the same compound traces as Type-1 Pool C.
    {
        'expr':              '2+3*6*(3+7)',
        'learner':           'compound_add_bracket_drop',
        'pool':              'C',
        'trace':             [
            '2+3×6×(3+7)', '↓',
            '5×6×(3+7)',   '↓',   # ERROR 1: add_before_mult
            '5×6×3+7',     '↓',   # ERROR 2: bracket_drop
            '30×3+7',      '↓',
            '90+7',        '↓',
            '97',
        ],
        'learnerAns':        '97',
        'expertAns':         '182',
        'advice':            'In any expression, multiplication comes before addition — always calculate × first, before doing any + or −.',
        'advice_type':       'points_to_first',
        'student':           'Kim',
        'misconception_types': ['add_before_mult', 'bracket_drop'],
        'inference_target':  'add_before_mult',
    },
    {
        'expr':              '3+2*4*(5-2)',
        'learner':           'compound_add_bracket_drop',
        'pool':              'C',
        'trace':             [
            '3+2×4×(5-2)', '↓',
            '5×4×(5-2)',   '↓',   # ERROR 1: add_before_mult
            '5×4×5-2',     '↓',   # ERROR 2: bracket_drop
            '20×5-2',      '↓',
            '100-2',       '↓',
            '98',
        ],
        'learnerAns':        '98',
        'expertAns':         '27',
        'advice':            'Scan the whole expression for × signs before doing any addition. Multiply first, then add.',
        'advice_type':       'points_to_first',
        'student':           'Leo',
        'misconception_types': ['add_before_mult', 'bracket_drop'],
        'inference_target':  'add_before_mult',
    },
    {
        'expr':              '4+2*3-5+1',
        'learner':           'compound_add_rtl',
        'pool':              'C',
        'trace':             [
            '4+2×3-5+1', '↓',
            '6×3-5+1',   '↓',   # ERROR 1: add_before_mult
            '18-5+1',    '↓',
            '18-6',      '↓',   # ERROR 2: same_prio_rtl
            '12',
        ],
        'learnerAns':        '12',
        'expertAns':         '6',
        'advice':            'When you see × in an expression, that multiplication must be done before any + or − on either side of it.',
        'advice_type':       'points_to_first',
        'student':           'Maya',
        'misconception_types': ['add_before_mult', 'same_prio_rtl'],
        'inference_target':  'add_before_mult',
    },
    {
        'expr':              '3+5*2-4+2',
        'learner':           'compound_add_rtl',
        'pool':              'C',
        'trace':             [
            '3+5×2-4+2', '↓',
            '8×2-4+2',   '↓',   # ERROR 1: add_before_mult
            '16-4+2',    '↓',
            '16-6',      '↓',   # ERROR 2: same_prio_rtl
            '10',
        ],
        'learnerAns':        '10',
        'expertAns':         '11',
        'advice':            'Multiplication binds numbers more tightly than addition — always do × before + or −.',
        'advice_type':       'points_to_first',
        'student':           'Nina',
        'misconception_types': ['add_before_mult', 'same_prio_rtl'],
        'inference_target':  'add_before_mult',
    },
    {
        'expr':              '5+2*4-3+4',
        'learner':           'compound_add_rtl',
        'pool':              'C',
        'trace':             [
            '5+2×4-3+4', '↓',
            '7×4-3+4',   '↓',   # ERROR 1: add_before_mult
            '28-3+4',    '↓',
            '28-7',      '↓',   # ERROR 2: same_prio_rtl
            '21',
        ],
        'learnerAns':        '21',
        'expertAns':         '14',
        'advice':            'Find every × in the expression and handle it before any + or − — multiplication always comes first.',
        'advice_type':       'points_to_first',
        'student':           'Omar',
        'misconception_types': ['add_before_mult', 'same_prio_rtl'],
        'inference_target':  'add_before_mult',
    },

    # ── Pool D — 2 misconceptions; advice targets the 2ND error ───────────────
    # Reuses the same compound traces as Type-1 Pool D.
    {
        'expr':              '1+4*5*(2+6)',
        'learner':           'compound_add_bracket_drop',
        'pool':              'D',
        'trace':             [
            '1+4×5×(2+6)', '↓',
            '5×5×(2+6)',   '↓',   # ERROR 1: add_before_mult
            '5×5×2+6',     '↓',   # ERROR 2: bracket_drop
            '25×2+6',      '↓',
            '50+6',        '↓',
            '56',
        ],
        'learnerAns':        '56',
        'expertAns':         '161',
        'advice':            'Brackets are the first priority — whatever is inside parentheses must be calculated before anything else.',
        'advice_type':       'points_to_second',
        'student':           'Petra',
        'misconception_types': ['add_before_mult', 'bracket_drop'],
        'inference_target':  'bracket_drop',
    },
    {
        'expr':              '4+1*3*(6-4)',
        'learner':           'compound_add_bracket_drop',
        'pool':              'D',
        'trace':             [
            '4+1×3×(6-4)', '↓',
            '5×3×(6-4)',   '↓',   # ERROR 1: add_before_mult
            '5×3×6-4',     '↓',   # ERROR 2: bracket_drop
            '15×6-4',      '↓',
            '90-4',        '↓',
            '86',
        ],
        'learnerAns':        '86',
        'expertAns':         '10',
        'advice':            'The brackets tell you to subtract 4 from 6 before multiplying. Always resolve brackets first.',
        'advice_type':       'points_to_second',
        'student':           'Raj',
        'misconception_types': ['add_before_mult', 'bracket_drop'],
        'inference_target':  'bracket_drop',
    },
    {
        'expr':              '6+1*5-3+2',
        'learner':           'compound_add_rtl',
        'pool':              'D',
        'trace':             [
            '6+1×5-3+2', '↓',
            '7×5-3+2',   '↓',   # ERROR 1: add_before_mult
            '35-3+2',    '↓',
            '35-5',      '↓',   # ERROR 2: same_prio_rtl
            '30',
        ],
        'learnerAns':        '30',
        'expertAns':         '10',
        'advice':            'When + and − appear after doing multiplications, work left to right — do the leftmost operation first.',
        'advice_type':       'points_to_second',
        'student':           'Sofia',
        'misconception_types': ['add_before_mult', 'same_prio_rtl'],
        'inference_target':  'same_prio_rtl',
    },
    {
        'expr':              '2+4*3-6+3',
        'learner':           'compound_add_rtl',
        'pool':              'D',
        'trace':             [
            '2+4×3-6+3', '↓',
            '6×3-6+3',   '↓',   # ERROR 1: add_before_mult
            '18-6+3',    '↓',
            '18-9',      '↓',   # ERROR 2: same_prio_rtl
            '9',
        ],
        'learnerAns':        '9',
        'expertAns':         '11',
        'advice':            'After multiplying, deal with + and − from left to right — the − comes before the + here, so do it first.',
        'advice_type':       'points_to_second',
        'student':           'Tomas',
        'misconception_types': ['add_before_mult', 'same_prio_rtl'],
        'inference_target':  'same_prio_rtl',
    },
    {
        'expr':              '1+3*4-2+5',
        'learner':           'compound_add_rtl',
        'pool':              'D',
        'trace':             [
            '1+3×4-2+5', '↓',
            '4×4-2+5',   '↓',   # ERROR 1: add_before_mult
            '16-2+5',    '↓',
            '16-7',      '↓',   # ERROR 2: same_prio_rtl
            '9',
        ],
        'learnerAns':        '9',
        'expertAns':         '16',
        'advice':            "After all the multiplications are done, handle + and − left to right — don't jump ahead to the + before the −.",
        'advice_type':       'points_to_second',
        'student':           'Uma',
        'misconception_types': ['add_before_mult', 'same_prio_rtl'],
        'inference_target':  'same_prio_rtl',
    },
]


def strip_example(text):
    """
    Remove trailing parenthetical specific examples from descriptions.
    e.g. "Did addition/subtraction before multiplication/division (computed `5+1` before `5×5`)"
         → "Did addition/subtraction before multiplication/division"
    Safe for mid-sentence parens like "Distributed (expanded) the brackets..."
    because those don't end with ')'.
    """
    if not text:
        return text
    idx = text.rfind(' (')
    if idx != -1 and text.endswith(')'):
        return text[:idx]
    return text


def build_advice_bank():
    """Build advice_bank.json from ADVICE_BANK_DATA."""
    bank = []
    for i, d in enumerate(ADVICE_BANK_DATA):
        pool = d['pool']

        n = len(d['misconception_types'])
        has_misconception        = n > 0
        has_1_misconception      = n == 1
        right_inference          = pool != 'B'
        inference_points_to_first = (
            True  if pool == 'C' else
            False if pool == 'D' else
            None
        )

        entry = {
            'id':                      i + 1,
            'format':                  'advice_slider',
            'pool':                    pool,
            'expression':              d['expr'].replace('*', '×'),
            'mysteryLearner':          d['learner'],
            'studentName':             d['student'],
            'traceLines':              d['trace'],
            'finalAnswer':             d['learnerAns'],
            'expertAnswer':            d['expertAns'],
            'advice':                  d['advice'],
            'adviceType':              d['advice_type'],
            'options':                 [],
            'correctKey':              None,
            # ── Analysis flags ──────────────────────────────────────────────
            'has_misconception':         has_misconception,
            'has_1_misconception':       has_1_misconception,
            'misconception_types':       d['misconception_types'],
            'inference_target':          d['inference_target'],
            'right_inference':           right_inference,
            'inference_points_to_first': inference_points_to_first,
        }
        bank.append(entry)

        rtag = '✓ right' if right_inference else '✗ foil '
        print(f"  {i+1:2}. [Adv Pool {pool}] {rtag}  {d['expr']:<25}  {d['misconception_types']}")

    out = os.path.join(os.path.dirname(__file__), 'advice_bank.json')
    with open(out, 'w') as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)

    for p in ['A', 'B', 'C', 'D']:
        cnt = sum(1 for e in bank if e['pool'] == p)
        descs = {
            'A': 'correct advice, all 5 shown',
            'B': 'wrong advice,   all 5 shown',
            'C': 'all 5 shown, advice → 1st error',
            'D': 'all 5 shown, advice → 2nd error',
        }
        print(f"  Advice Pool {p}: {cnt:2}  — {descs[p]}")
    print(f"\nWrote {len(bank)} entries → {out}")
    return bank


def main():
    bank = []
    for i, d in enumerate(BANK_DATA):
        pool = d['pool']

        # Description shown to participant — strip specific computed examples
        if pool in ('C', 'D'):
            desc_shown = strip_example(d['desc_shown'])
        elif pool == 'B':
            desc_shown = strip_example(d['foil_desc'])
        else:
            desc_shown = strip_example(d['correct_desc'])

        # Answer key
        correct_key = 'no' if pool == 'B' else 'yes'

        # Analysis flags
        n = len(d['misconception_types'])
        has_misconception        = n > 0
        has_1_misconception      = n == 1
        right_inference          = pool != 'B'   # B is the only wrong-inference pool
        inference_points_to_first = (
            True  if pool == 'C' else
            False if pool == 'D' else
            None                          # A and B: single-misconception → N/A
        )

        options = [
            {'key': 'yes', 'label': 'Yes', 'description': ''},
            {'key': 'no',  'label': 'No',  'description': ''},
        ]
        random.shuffle(options)

        entry = {
            'id':                      i + 1,
            'format':                  'type1_yn',
            'pool':                    pool,
            'expression':              d['expr'].replace('*', '×'),
            'mysteryLearner':          d['learner'],
            'studentName':             d['student'],
            'traceLines':              d['trace'],
            'finalAnswer':             d['learnerAns'],
            'expertAnswer':            d['expertAns'],
            'correctDescription':      strip_example(d.get('correct_desc', desc_shown)),
            'foilDescription':         strip_example(d.get('foil_desc')),
            'descriptionShown':        desc_shown,
            'options':                 options,
            'correctKey':              correct_key,
            # ── Analysis flags ──────────────────────────────────────────────
            'has_misconception':         has_misconception,
            'has_1_misconception':       has_1_misconception,
            'misconception_types':       d['misconception_types'],
            'inference_target':          d['inference_target'],
            'right_inference':           right_inference,
            'inference_points_to_first': inference_points_to_first,
        }
        bank.append(entry)

        ans_tag   = 'Yes ✓' if correct_key == 'yes' else 'No  ✗'
        rtag      = '✓ right' if right_inference else '✗ foil '
        print(f"  {i+1:2}. [Pool {pool}] {ans_tag}  {rtag}  {d['expr']:<25}  {d['misconception_types']}")

    out = os.path.join(os.path.dirname(__file__), 'trial_bank.json')
    with open(out, 'w') as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)

    for p in ['A', 'B', 'C', 'D']:
        cnt = sum(1 for e in bank if e['pool'] == p)
        descs = {
            'A': 'participant draws 10 at random, answer = Yes',
            'B': 'all 5 shown,          answer = No',
            'C': 'all 5 shown,          answer = Yes  (inference → 1st error)',
            'D': 'all 5 shown,          answer = Yes  (inference → 2nd error)',
        }
        print(f"  Pool {p}: {cnt:2}  — {descs[p]}")
    print(f"\nWrote {len(bank)} entries → {out}")
    print(f"Per-participant: 10 (A) + 5 (B) + 5 (C) + 5 (D) = 25 trials")

    print("\n── Building advice bank (Type 3) ──────────────────────────────────────")
    build_advice_bank()


if __name__ == '__main__':
    main()
