# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 15:33:59 2023

@author: andre
"""
import math
from agent_based_economy.agents.agent import Agent
from agent_based_economy.agents.roles import ReserveHolder, Lender, Borrower, BondIssuer

class Government(Agent, ReserveHolder, Borrower, BondIssuer):  
    
    def __init__(self, model):      
        super().__init__(model)         
        # self.tax   = TaxRegister(self)  # asset, claim on individuals    
        
        ReserveHolder.__init__(self)             
        Borrower.__init__(self)      
        BondIssuer.__init__(self)     
        
    def open_account_at_central_bank(self):
        idx = self.open_deposit_account(self.model.central_bank, overdraft=math.inf)        
        return idx 
    
    def buy_goods(self):
        pass