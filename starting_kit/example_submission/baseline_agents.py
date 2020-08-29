import numpy as np

       
class NoActions():
    """
    Agent class: takes decisions regarding the pandemic...
    Policy: no action
    """
    
    def __init__(self):
        super(Agent, self).__init__()
        self.day = 1
        
    def update(self, observation, action, reward):
        self.day += 1

    def action(self, observation):
        return 0, 0

class RandomLineSwitch(Agent):
    def __init__(self, environment):
        super().__init__(environment)

        self.ioman = ActIOnManager(destination_path='saved_actions_RandomLineSwitch.csv')

    def act(self, observation):

        return action