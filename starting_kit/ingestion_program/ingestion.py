import os
import sys

import logging
import pydoc
import time
import json

import csv

overall_start = time.time()

PHASE_NUMBER = 1  # Numbering starts at 1

VERBOSE = True

import world

def main():
    # read arguments
    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])
    program_dir = os.path.abspath(sys.argv[3])
    submission_dir = os.path.abspath(sys.argv[4])
    log_file = list()
    
    # create output dir if not existing
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if VERBOSE:
        print("input dir: {}".format(input_dir))
        print("output dir: {}".format(output_dir))
        print("program dir: {}".format(program_dir))
        print("submission dir: {}".format(submission_dir))

        print("input content", os.listdir(input_dir))
        print("output content", os.listdir(output_dir))
        print("program content", os.listdir(program_dir))
        print("submission content", os.listdir(submission_dir))

    # add proper directories to path
    sys.path.append(program_dir)
    sys.path.append(submission_dir)

    try:
        import submission
    except ImportError:
        raise ImportError('The submission folder should contain a file submission.py containing your controler named '
                          'as the class Submission.')


    # Instantiate and run the agents on both validation and test sets (simultaneously)
    
    with open(os.path.abspath(os.path.join(input_dir, "country1.json")), 'r') as read_file:
        data = json.load(read_file)
        
    DAYS = 150

    world_env = world.World(data)
    try:
        agent = submission.Submission()
    except:
        raise Exception('Did not find a class named Submission within submission.py; your submission controler should'
                        ' be a class named Submission in submission.py file directly within the ZIP submission file.')

    for i in range(DAYS):
        print("\nDays:", i)
        
        observation, eco = world_env.observe()
        print("I:", int(observation[0]))
        print("R:", int(observation[1]))
        print("D:", int(observation[2]))
        print("Production:", eco)
        
        action = agent.action(observation)
        reward = world_env.step(action)
        agent.update(observation, action, reward)
        print("Cost:", reward)
        log_file.append(reward)
        
    
    
    with open(os.path.abspath(os.path.join(output_dir,'log_file.json')), 'w') as file:
        json.dump(log_file, file)

    overall_time_spent = time.time() - overall_start
    if VERBOSE:
        print("Overall time spent %5.2f sec " % overall_time_spent)

if __name__ == "__main__":
    main()
