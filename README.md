# Robot Torque Calculator: Static Gravity Loads for a Planar Arm

Calculate the holding torque of each joint in a serial arm moving in a vertical plane. You will run three poses, inspect signed torques and check the implementation against the derivative of potential energy. Python's standard library is enough.

Full illustrated lesson and interactive calculator: https://wifarobotics.com/learn/robot-torque-calculator/

## What you will build

The project contains one command-line calculator, three JSON configuration files and ten automated tests. It accepts link lengths, link masses, relative joint angles, link centers of mass and a point payload at the final tip. It returns joint locations, mass centers, potential energy and the torque needed to oppose gravity in the stated pose.

There are no robot drivers and no motor commands. This is an educational static model. It does not select a safe motor, validate a gearbox, calculate dynamic peak torque or certify a robot.

## Start from zero

Install Python 3.10 or newer from https://www.python.org/downloads/ . Download and extract this project. Open a terminal in the folder containing main.py, then run `python --version`. On Windows, use `py` if python is missing. On Linux and macOS use `python3` if required. Substitute that interpreter command in all the steps below.

Run `python main.py`. The default configuration is examples/horizontal.json. No pip install, network connection, GPU, camera or hardware is needed after downloading the files.

Run `python main.py --config examples/folded.json`, then `python main.py --config examples/vertical.json`. The output is JSON that you can copy into a report or inspect in a text editor. Run `python -m unittest discover -s tests -v` to check the implementation.

## Run the browser calculator

From the project root run `python -m http.server 8000 --bind 127.0.0.1`, then open http://127.0.0.1:8000/. Stop the server with Ctrl+C when finished. This serves only to your own computer. Do not double-click index.html because file-URL module loading may be blocked. The browser form takes relative angles in degrees; the JSON configurations and Python API use radians. Input edits clear previous results.

For optional cross-language checks, install Node.js 20 or newer from https://nodejs.org/ and run `node --test tests/model.test.mjs`. Four Node tests include parity with Python. On Windows PowerShell set `$env:PYTHON_BIN = "python"` first, or use `"py"` as appropriate. No npm install is needed.

## Define the arm before entering numbers

The base joint is at x=0, y=0. The x axis points right and y points upward. Gravity acts downward. Every joint rotates about the axis perpendicular to this vertical plane. The first angle is measured counterclockwise from positive x. Each later angle is relative to the preceding link, not relative to the world.

The calculator adds relative angles to find each link's absolute direction. For example, [0, pi] puts link one to the right and link two back to the left. [pi/2, 0] puts both links vertically upward. Angles are radians: degrees multiplied by pi/180 gives radians.

Lengths are metres, masses kilograms and gravity is 9.81 metres per second squared by default. A 300 mm link must be entered as 0.3 m. The default center-of-mass fraction is 0.5, appropriate only for an ideal uniform link. For a real assembly, measure or calculate the center of mass including mounted components. Fractions range from 0 at the proximal joint to 1 at the distal end. This implementation does not represent mass centers outside that segment.

## The calculation

For a joint, each downstream mass creates a gravity moment equal to mass times gravity times its horizontal lever arm from that joint. The actuator holding torque is the opposite of that gravity moment. Positive output means the actuator must apply counterclockwise torque in our coordinate convention.

```text
absolute_angle[k] = sum(relative_angles[0:k+1])
end_x[k] = start_x[k] + length[k] * cos(absolute_angle[k])
end_y[k] = start_y[k] + length[k] * sin(absolute_angle[k])
center[k] = start[k] + com_fraction[k] * (end[k] - start[k])

holding_torque[j] = g * sum(mass[k] * (center_x[k] - joint_x[j]))
                   + g * payload * (tip_x - joint_x[j])
                   for downstream links k >= j

potential_energy = g * sum(mass[k] * center_y[k]) + g * payload * tip_y
```

A negative torque is not an error. It means gravity's moment changed direction. The geometric distance to a mass is not the correct lever for gravity: use its horizontal offset in this vertical-plane model.

## Example 1: a horizontal arm

Use lengths 0.3 m and 0.2 m, masses 1.0 kg and 0.5 kg, angles [0, 0], and a 0.4 kg point payload. The uniform-link mass centers are x=0.15 m and x=0.4 m. The tip is at x=0.5 m.

The shoulder torque is `9.81 * (1*0.15 + 0.5*0.4 + 0.4*0.5) = 5.3955 N m`. The elbow sees only the second link and payload, so its torque is `9.81 * (0.5*0.1 + 0.4*0.2) = 1.2753 N m`. Do not add the two output torques together to choose one motor; they belong to different joints.

## Example 2: fold the elbow back

Keep the same arm but set angles to [0, pi]. The tip moves to x=0.1 m and the second link center moves to x=0.2 m. The shoulder now needs 2.8449 N m. The elbow output becomes -1.2753 N m because the downstream weights are left of the elbow.

This pose reduces the shoulder's static gravity torque in this simplified model. It does not establish collision clearance, reachability of a real mechanism or a safe path between poses.

## Example 3: point the arm upward

Set angles to [pi/2, 0]. Ideal horizontal lever arms are zero, so both holding torques approach zero to numerical precision. This does not mean the arm can move without torque, remain balanced after a disturbance or operate without a brake. Acceleration, friction, flexibility, joint limits and loss of power remain outside the model.

## Run and understand the tests

The ten tests include known one-link and two-link calculations, folded and vertical poses, zero mass, changed payload, a reversed shoulder direction, a center of mass at the joint and invalid inputs. A separate check uses 20 seeded three-link poses and differentiates potential energy numerically for every joint.

At rest, required holding torque equals the derivative of potential energy with respect to that joint angle. The finite-difference test checks this relationship using a small positive and negative angle perturbation. It uses a different calculation from the direct horizontal-lever formula. The test tolerance is 0.0000001 N m for these specific examples; it is a numerical check, not a measurement accuracy claim.

Run tests from the project root so Python can import main.py. If a failure appears after editing a configuration, first check the distinction between relative and absolute angles and the metre-to-millimetre conversion. A passing test suite only supports the software and stated static model.

## Make your own configuration

Copy examples/horizontal.json to a new file and edit one parameter at a time. Keep the three arrays the same length. To use a nonuniform link, add a com_fractions array with one fraction per link. Keep a note of where every mass and center-of-mass estimate came from.

Try doubling only the payload. Predict the torque increase at each joint using its tip lever arm before running the program. Next compare the three supplied poses without changing mass. Record the sign as well as the magnitude so you understand which way gravity tends to move the joint.

## What a motor-sizing project still needs

This calculator omits acceleration, Coriolis effects, friction, gearbox efficiency, reflected inertia, thermal duty cycle, brake holding capacity, external process loads and structural strength. Output is at the joint, not automatically at the motor shaft. A generic multiplier on these numbers does not replace those analyses or manufacturer torque-speed and duty-cycle data.

Do not connect the example to a powered machine. Use it as an offline calculation and compare against an independently prepared static free-body diagram. Any later hardware experiment requires appropriate guarding, support for falling links, competent supervision and the actual manufacturer's procedures.

## Troubleshooting

If the file cannot be found, open the terminal in the project root and check the --config path. JSON uses dots for decimal numbers, square brackets for arrays and no comments. Empty arrays, mismatched array sizes, negative masses, invalid center-of-mass fractions and nonfinite numbers are rejected. A large unexpected result often means millimetres were entered as metres. A negative result often means the lever arm changed sign.

## Further reading

The dynamics background is [Modern Robotics Chapter 8](https://modernrobotics.northwestern.edu/chapters/chapter8/), particularly gravity terms, open-chain dynamics and gearing. The WIFA Academy has a separate [shoulder gravity-torque guide](https://wifarobotics.com/academy/robot-design/estimate-gravity-torque-for-a-robot-shoulder-joint/) and a [robot design path](https://wifarobotics.com/academy/robot-design/). This project adds a reusable multiple-joint calculation and independent numerical tests to that introductory material.

Original educational implementation by WIFA Robotics. No license grant is implied; contact the owner for reuse permission.
