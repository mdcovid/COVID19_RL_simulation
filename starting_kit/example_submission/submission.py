
class Submission():
    """
    Agent class: takes decisions regarding the pandemic
    Template to use to build new agents
    Policy: no action
    """
    
    def __init__(self):
        super(Submission, self).__init__()
        self.day = 1
        
    def update(self, observation, action, reward):
        self.day += 1

    def action(self, observation):
        return 0, 0
