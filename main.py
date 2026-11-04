"""Static gravity holding torque of a serial planar arm in a vertical plane.

Lengths are metres, masses kilograms, joint angles relative radians.
No motor commands, dynamic sizing or hardware validation are performed.
"""
import argparse
import json
import math
from pathlib import Path


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def calculate(lengths_m, masses_kg, angles_rad, payload_kg=0.0, com_fractions=None, gravity=9.81):
    if not all(isinstance(v, (list, tuple)) for v in (lengths_m, masses_kg, angles_rad)):
        raise ValueError('Link lengths, masses and angles must be arrays')
    count = len(lengths_m)
    if count == 0 or count > 100 or len(masses_kg) != count or len(angles_rad) != count:
        raise ValueError('Provide matching arrays for 1 to 100 links')
    if com_fractions is None:
        com_fractions = [0.5] * count
    if not isinstance(com_fractions, (list, tuple)) or len(com_fractions) != count:
        raise ValueError('Provide one center-of-mass fraction per link')
    if any(not finite_number(v) or v <= 0 for v in lengths_m):
        raise ValueError('Link lengths must be positive finite metres')
    if any(not finite_number(v) or v < 0 for v in masses_kg):
        raise ValueError('Link masses must be nonnegative finite kilograms')
    if any(not finite_number(v) for v in angles_rad):
        raise ValueError('Angles must be finite relative radians')
    if any(not finite_number(v) or not 0 <= v <= 1 for v in com_fractions):
        raise ValueError('COM fractions must lie between zero and one')
    if not finite_number(payload_kg) or payload_kg < 0 or not finite_number(gravity) or gravity <= 0:
        raise ValueError('Payload must be nonnegative and gravity positive, both finite')
    joints = [(0.0, 0.0)]
    centers = []
    angle = 0.0
    for length, relative, fraction in zip(lengths_m, angles_rad, com_fractions):
        angle += relative
        if not math.isfinite(angle):
            raise ValueError('Angles exceed numerical range')
        dx, dy = length * math.cos(angle), length * math.sin(angle)
        x, y = joints[-1]
        centers.append((x + fraction*dx, y + fraction*dy))
        joints.append((x + dx, y + dy))
    tx, ty = joints[-1]
    torque = [gravity * (sum(masses_kg[k] * (centers[k][0]-joints[j][0])
                            for k in range(j, count)) + payload_kg * (tx-joints[j][0]))
              for j in range(count)]
    energy = gravity * (sum(m*c[1] for m,c in zip(masses_kg, centers)) + payload_kg*ty)
    if any(not math.isfinite(v) for p in joints+centers for v in p) or any(not math.isfinite(v) for v in torque+[energy]):
        raise ValueError('Inputs exceed numerical range')
    return {'holding_torque_Nm':torque, 'joint_positions_m':joints,
            'link_centers_m':centers, 'potential_energy_J':energy}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('examples/horizontal.json'))
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text())
        result = calculate(**config)
    except (OSError, ValueError, TypeError, OverflowError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, allow_nan=False))
