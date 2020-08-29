import numpy as np
import matplotlib.pyplot as plt

import json

class World():
    """Simulation of the world
    
    This simulation is based on the SIRD model and the transitions are based
    on its system of differential equations.
    
    Attributes:
        beta: number of people infected by 1 infected person
        D: number of days a person is infectious
        gamma = 1/D: recovery rate
        alpha: fatality rate
        rho: 1/3
        R0 = self.beta*self.D: basic reproduction number
   
        N: total population
        S: susceptible
        E: exposed
        I: infected
        R: recovered
        D: dead
        
        history: statistics about I, R, D
    """
    
    def __init__(self, data):
        """
        Args:
            N: total population
            initial_cases: number of initial cases assignated to E or I
        
        """
        super(World, self).__init__()

        self.beds = 100_000
        
        self.age_class = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80+"]
        self.age_class_proportions = [0.1, 0.15, 0.15, 0.15, 0.15, 0.1, 0.1, 0.05, 0.05]
        
        self.sectors = {"Agriculture": dict(), "Production": dict(), "Services": dict()}
        self.N = {"Agriculture": data["population"] * data["sector_proportion"][0],
                  "Production":  data["population"] * data["sector_proportion"][1],
                  "Services":    data["population"] * data["sector_proportion"][2]}
        self.production_value = {"Agriculture": data["production_value"][0],
                                 "Production":  data["production_value"][1],
                                 "Services":    data["production_value"][2]}
        self.stringency = {"Agriculture": data["stringency"][0],
                           "Production":  data["stringency"][1],
                           "Services":    data["stringency"][2]}
        
        
        for sector_name in self.sectors:
            self.sectors[sector_name]["N"] = self.N[sector_name]
            
            self.sectors[sector_name]["S"] = self.N[sector_name] - data["initial_cases"]
            self.sectors[sector_name]["E"] = data["initial_cases"]
            self.sectors[sector_name]["I"] = 0
            self.sectors[sector_name]["R"] = 0
            self.sectors[sector_name]["D"] = 0
            self.sectors[sector_name]["F"] = 0
            
            self.sectors[sector_name]["beta"]  = data["beta"]       # number of people infected by 1 infected person
            self.sectors[sector_name]["D_epi"] = data["D_epi"]      # number of days a person is infectious
            self.sectors[sector_name]["gamma"] = data["gamma"]      # recovery rate (= 1/D_epi)
            self.sectors[sector_name]["mu"]    = data["mu"]         # fatality rate
            self.sectors[sector_name]["sigma"] = 1/data["inv_sigma"]
            self.sectors[sector_name]["rho"]   = 1/data["inv_rho"]
            self.sectors[sector_name]["nu"]    = data["nu"]
#             self.sectors[sector_name]["R0"]    = self.sectors[sector_name]["beta"]*self.sectors[sector_name]["D_epi"]
            
            self.sectors[sector_name]["cout_beta"] = data["cost_beta"]
            self.sectors[sector_name]["cout_mu"] = data["cost_mu"]
            
            self.sectors[sector_name]["production_value"] = self.production_value[sector_name]
            self.sectors[sector_name]["stringency"] = self.stringency[sector_name]
            
#         self.C = 0                        # critical

        self.compartiments = ["infected", "recovered", "dead", "quarantined"]
        
        self.history = []
        self.history_eco = []
        self.history_c = []
        self.history_c1 = []
        self.history_c2 = []
        
    def observe(self):
        I, R, D = 0, 0, 0
        state_eco = 0
        
        for sector_name in self.sectors:
            I += self.sectors[sector_name]["I"]
            R += self.sectors[sector_name]["R"]
            D += self.sectors[sector_name]["D"]
            state_eco += (self.sectors[sector_name]["S"] + self.sectors[sector_name]["R"]) * self.sectors[sector_name]["production_value"]
            
        state_epi = (I, R, D)

        self.history.append(state_epi)
        self.history_eco.append(state_eco)

        return state_epi, state_eco
    

        
    def step(self, action):
        d_beta, d_mu = action
        reward = 0
        
#         for s in self.sectors:
# #             self.sectors[sector_name]["beta"] *= action
#             if action == 1:
#                 if self.sectors[s]["S"] == 0:
#                     self.sectors[s]["S"] = self.sectors[sector_name]["Q"]
#                     self.sectors[s]["Q"] = 0
#             else:
#                 if self.sectors[s]["Q"] == 0:
#                     self.sectors[s]["Q"] = self.sectors[sector_name]["S"]
#                     self.sectors[s]["S"] = 0
         
        for s in self.sectors:
            S, E, I, R = self.sectors[s]["S"], self.sectors[s]["E"], self.sectors[s]["I"], self.sectors[s]["R"]
            D, F, N    = self.sectors[s]["D"], self.sectors[s]["F"], self.sectors[s]["N"]

            pse = (S + R) * self.sectors[s]["production_value"]
            
            self.sectors[s]["S"] = S - ((self.sectors[s]["beta"]-d_beta) * I * S/N) - (self.sectors[s]["nu"] * I * S/N)
            self.sectors[s]["E"] = E + ((self.sectors[s]["beta"]-d_beta) * I * S/N) - self.sectors[s]["sigma"]*E
            self.sectors[s]["I"] = I + self.sectors[s]["sigma"]*E - (self.sectors[s]["gamma"]+(self.sectors[s]["mu"]-d_mu))*I
            self.sectors[s]["R"] = R + self.sectors[s]["gamma"] * I
            self.sectors[s]["D"] = D + (self.sectors[s]["mu"]-d_mu) * I
            self.sectors[s]["F"] = F + self.sectors[s]["nu"] * I * S/N
            
            S_next, R_next = self.sectors[s]["S"], self.sectors[s]["R"]
            I_next, D_next = self.sectors[s]["I"], self.sectors[s]["D"]
            nse = (S_next + R_next) * self.sectors[s]["production_value"]
            
            c1 = (I_next-I) + (D_next-D)
            if c1 < 0:
                c1 = 0
            c2 = self.sectors[s]["cout_beta"]*d_beta + self.sectors[s]["cout_mu"]*d_mu 
            c = c1 + c2  
            
        self.history_c.append(c)
        self.history_c1.append(c1)
        self.history_c2.append(c2)
        return c
    
    def print_graphs(self):
        """Print graphs representing the infected, recovered and dead people over time
        """
        stats = list(zip(*self.history))
        I, R, D = stats
        f, ax = plt.subplots(1, 1, figsize=(10,4))
#         ax.plot(S, 'b', label='Susceptible')
        ax.plot(I, 'r', label='Infected')
        ax.plot(R, 'g', label='Recovered')
        ax.plot(D, 'black', label='Dead')

        ax.set_xlabel('Time (days)')
        legend = ax.legend()
        for spine in ('top', 'right', 'bottom', 'left'):
            ax.spines[spine].set_visible(False)
        plt.show()
        
    def print_statistics(self):
        print(f"Simulation: {len(self.history)} days\n")
        print("---")

        
        stats = list(zip(*self.history))
        I, R, D = stats
        
        print("Peak infected number", int(np.max(I)))
        print("Average infected number", np.mean(I))
        print("---")
        
        print("Final recovered number", int(np.max(R)))
        print("Final dead number", int(np.max(D)))
        print("---")

        print("Average number of beds used in ICU:",)
        print("Number of days of surpopulation in ICU:",)