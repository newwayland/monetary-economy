# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 15:32:50 2023

@author: andre
"""


import random 
import math
from typing import List, Tuple
import pandas as pd
import numpy as np
# from agent_based_economy.agents.roles import DepositHolder, ReserveHolder, DepositIssuer, ReserveIssuer, Lender, Borrower, BondIssuer, BondHolder
from agent_based_economy.accounting import BalanceSheet

class Agent:    
    
    asset_keys = []
    liability_keys = []
    
    def __init__(self, model):
        self.model = model
        self.unique_id = model.next_id()
   
    def superclasses(self):
        return [x.__name__ for x in self.__class__.__mro__]
    
    @property
    def is_firm(self):
        return 'Firm' in self.superclasses()
    
    @property
    def is_individual(self):
        return 'Individual' in self.superclasses()

    @property
    def is_bank(self):
        return 'Bank' in self.superclasses()
    
    @property
    def is_central(self):
        return 'CentralBank' in self.superclasses()
    
    @property
    def is_commercial(self):
        return 'CommercialBank' in self.superclasses()     
    
    @property
    def is_government(self):
        return 'Government' in self.superclasses()
    
    @property
    def issues_deposits(self):
        return 'DepositIssuer' in self.superclasses()
    
    @property
    def holds_deposits(self):
        return 'DepositHolder' in self.superclasses()    
    
    @property
    def borrows(self):
        return 'Borrower' in self.superclasses()
    
    @property
    def lends(self):
        return 'lender' in self.superclasses()
    
    @property
    def issues_bonds(self):
        return 'BondIssuer' in self.superclasses()
    
    @property
    def holds_bonds(self):
        return 'BondHolder' in self.superclasses()
    
    @property
    def issues_stock(self):
        return 'StockIssuer' in self.superclasses()
    
    @property
    def holds_stock(self):
        return 'StockHolder' in self.superclasses()
    
    @property
    def levies_taxes(self):
        return 'TaxAuthority' in self.superclasses()
    
    @property
    def pays_taxes(self):
        return 'Taxpayer' in self.superclasses()
    
    @property
    def is_employable(self):
        return 'Employee' in self.superclasses()
    
    @property
    def is_employer(self):
        return 'Employer' in self.superclasses()
    
    def __str__(self):
        return f'{self.__class__.__name__}: {id(self)}'
    
    def assets_dict(self, except_counterparties=[]):
        assets = {}
        for key in self.asset_keys:
            asset = getattr(self, key)(except_counterparties=except_counterparties)
            assets[asset[0]] = np.round(float(asset[1]),2)
            
        return assets
    
    def liabilities_dict(self, except_counterparties=[]):
        liabilities = {}
        for key in self.liability_keys:
            liability = getattr(self, key)(except_counterparties=except_counterparties)
            liabilities[liability[0]] = np.round(float(liability[1]),2)
            
        return liabilities
    
    def balance_sheet(self, **kwargs):
        return BalanceSheet.from_owner(self, **kwargs)
    
    def with_probability(self, chance: float) -> bool:
        """
        Random check between 0 and 1
        """
        return random.random() < chance