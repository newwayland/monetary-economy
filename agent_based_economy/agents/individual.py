# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 15:33:55 2023

@author: andre
"""
from agent_based_economy.agents.agent import Agent
from agent_based_economy.agents.roles import DepositHolder, Lender, Borrower, BondHolder

class Individual(Agent, DepositHolder, Borrower, Lender, BondHolder):    
    def __init__(self, model):        
        super().__init__(model)           
        DepositHolder.__init__(self)            
        Borrower.__init__(self)                 
        Lender.__init__(self)      
        BondHolder.__init__(self)      
        