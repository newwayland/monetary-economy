# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 15:38:46 2023

@author: andre
"""

import pandas as pd
from agent_based_economy.agents.agent import Agent 
from agent_based_economy.agents.roles import DepositHolder 

class StockRegistrar(Agent, DepositHolder):  

    """

    """
    
    __slots__ = ('model', 'unique_id', 'dividend_ledger')

    def __init__(self, model) -> None:
        """
        Customize the agent
        """
        super().__init__(model)
        self.dividend_ledger = pd.DataFrame(columns=['Dividends due'], index=model.households)        
        self.dividend_ledger['Dividends due'] = 0      
        DepositHolder.__init__(self)        
        
    def update_ledger(self, values_per_household):
        self.dividend_ledger['Dividends due'] += values_per_household
        
    def pay_dividends(self):
        for idx in self.dividend_ledger.index:
            self.pay(idx.deposit_account_number, self.dividend_ledger.at[idx, 'Dividends due'])
               
        self.dividend_ledger['Dividends due'] = 0        