# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 19:42:44 2022

@author: ABE
"""

from agent_based_economy.ledger import Ledger
import numpy as np

class Portfolio(Ledger):
    
    columns = ['unique_id',          # Unique ID in portfolio
               'issuer',             # Issuer
               'account',            # Unique ID at issuer (account number)
               ]
    
    def __init__(self, holder):
        super().__init__(holder)
        delattr(self, 'issuer')
        self.holder = holder
               
    def get_idx_from_issuer_and_account(self, issuer, account):
        idx = np.where(np.logical_and(self.df['issuer'] == issuer, self.df['account'] == account))[0][0]
        return idx    
        
    def append(self, **kwargs):
        return self.create(**kwargs)
    
    def remove(self):
        pass
    

class BondPortfolio(Portfolio):
        
    columns = Portfolio.columns.append(['purchase_date', 'purchase_price', 'pledged'])

    def __init__(self, holder):
        super().__init__(holder)
        
    def append(self, issuer, account, price):
        purchase_date = self.holder.model.day
        purchase_price = price
        pledged = False
        
        return super().append(issuer=issuer,account=account,purchase_date=purchase_date,
                           purchase_price=purchase_price, pledged=pledged)
    
    def remove(self, issuer, account):        
        row_idx = self.get_idx_from_issuer_and_account(issuer, account)
        
        self.df.drop([row_idx], inplace=True)
        self.df.index = range(len(self.df))
        return True
        