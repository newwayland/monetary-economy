# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 15:33:59 2023

@author: andre
"""
import numpy as np
from agent_based_economy.agents.agent import Agent
from agent_based_economy.agents.roles import Lender, ReserveIssuer, ReserveHolder, DepositIssuer, BondHolder, Borrower

class Bank(Agent, Lender, BondHolder):       
    __slots__ = ()
        
    def __init__(self, model):             
        super().__init__(model)  
        
        Lender.__init__(self)  
        BondHolder.__init__(self)     
    

class CentralBank(Bank, ReserveIssuer):
    __slots__ = ('model', 'unique_id', '_target_interest_rate', '_deposit_interest_rate', '_loan_interest_rate', 
                 '_interest_rate_spread')  
    
    def __init__(self, model, target_interest_rate=2, lending_rate_spread=0.25):             
        super().__init__(model)          
        ReserveIssuer.__init__(self)  
        self._lending_rate_spread = lending_rate_spread
        self.target_interest_rate = target_interest_rate
        
    @property
    def target_interest_rate(self):
         return self._target_interest_rate
     
    @target_interest_rate.setter
    def target_interest_rate(self, rate):
         self._target_interest_rate = rate
         self.deposit_interest_rate = self.target_interest_rate # floor, not corridor
         self.loan_interest_rate    = self.target_interest_rate + self.lending_rate_spread
       
    @property
    def lending_rate_spread(self):
         return self._lending_rate_spread
     
    @lending_rate_spread.setter
    def lending_rate_spread(self, spread):
         self._lending_rate_spread = spread
         self.target_interest_rate = self.target_interest_rate # refresh other rates
    
    def open_account(self, holder, overdraft = 0):
        if (holder.is_commercial) or (holder.is_government):
            super().open_deposit_account(holder, overdraft)
        else:
            raise Exception("Only government or commercial banks can hold accounts with the central bank")             
    
    def open_standing_lending_facility(self):
        self.model.interbank_market.register_offer(self, np.inf, self.loan_interest_rate) 
        
    def pay(self, recipient_account_number, value):
        # special case since the central bank is not a deposit holder
        to_bank = self.model.deposit_ledger.issuer(recipient_account_number)
        
        if to_bank == self:
            self.credit(recipient_account_number, value, authenticated=True) 
        else:
            self.credit(to_bank.deposit_account_number, value, authenticated=True) 
            to_bank.credit(recipient_account_number, value, authenticated=True)
                

class CommercialBank(Bank, DepositIssuer, ReserveHolder, Borrower):  
    __slots__ = ('model', 'unique_id', '_deposit_interest_rate', '_loan_interest_rate') 
    
    def __init__(self, model):   
        super().__init__(model)    
        DepositIssuer.__init__(self)     
        ReserveHolder.__init__(self)     
        Borrower.__init__(self)  
    
    def register_with_central_bank(self, overdraft=np.inf):        
        idx = self.model.central_bank.open_account(self, overdraft=overdraft)        
        return idx
    
    def open_account(self, holder, overdraft = 0):
        
        if (holder.is_firm) or (holder.is_individual):
            
            # Check overdraft and other terms here?
            
            super().open_deposit_account(holder, overdraft)
        else:
            raise Exception("Only firms or individuals can hold accounts with commercial banks")             
        