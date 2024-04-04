# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 13:36:29 2022

@author: andre
"""

import pandas as pd
import numpy as np

class TaxRegister:
    
    columns = ['id',                 # Unique ID, mapped to issuers and holders
               'issuer',             # Unique ID of issuer
               'holder',             # Unique ID of holder
               'value',              # Value in pounds sterling
               'interest_rate',      # Rate as percentage per annum
               'interest_frequency', # Times per year interest accrued
               'interest_day',       # Which day in period interest paid
               'issue_date'          # 
               'maturity_date'       # 
               'payment_frequency',  # Times per year payments made
               'payment_day',        # Which day in period payment paid
               'payment_amount',     # How much paid off
               ]
    
    def __init__(self, holder):
        self.df = pd.DataFrame(columns = TaxRegister.columns)
        self.counter = int(0) # for unique ID purposes, not indexing
        self.holder = holder
        
    def create_loan(self, issuer, holder, value, rate, maturity_date):
        # Defaults, for now
        interest_frequency = 12   # times per year, i.e. monthly
        interest_day       = 1   # first day of period (i.e. month)
        
        idx = self.counter
        issue_date = self.model.day
        
        new_row = {'id': idx, 'issuer': issuer, 'holder': holder, 'value': value, 
                   'interest_rate': rate, 'interest_frequency': interest_frequency, 
                   'interest_day': interest_day, 'issue_date': issue_date, 
                   'maturity_date': maturity_date}

        self.df = self.df.append(new_row, ignore_index=True)
        self.counter += 1
        
        return idx
    
    def close_loan(self, idval):
        idx = self.get_idx_from_id(idval)
        
        if self.current_balance(idx) == 0:
            self.df.drop([idx], inplace=True)
            self.df.index = range(len(self.df))
            return True
        else:
            return False
    
    def get_idx_from_id(self, idval):
        idx = np.where(self.df['id'] == idval)[0][0]
        return idx
    
#    def current_balance(self, idval):
#        idx = self.get_idx_from_id(idval)
#        return self.df.iloc[idx]['value']
#        
#    def transfer(self,from_idx,to_idx,value):
#        pass
#        
#    def credit(self,idx,value):
#        pass
#    
#    def debit(self,idx,value):
#        pass
#        
    def interest_due(self, date=None):
        if date == None:
            date == self.model.day
        
        return self.df[date % (self.model.year_days/self.df['interest_frequency'])==0] 
        
    
    def loan_maturing(self, date=None):
        if date == None:
            date == self.model.day
        return self.df[self.df['maturity_date']==date] 
    
        
