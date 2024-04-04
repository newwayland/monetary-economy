# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 20:29:11 2022

@author: ABE
"""

from __future__ import annotations
import pandas as pd
import numpy as np

class Ledger:
    
    __slots__ = ('model', 'df', 'counter')
    
    columns = ['issuer',             # Object reference of issuer
               'holder',             # Object reference of holder
               'value',              # Value in pounds sterling
               'interest_rate',      # Rate as percentage per annum
               ]
    
           
    def __init__(self, model):
        self.model   = model
        # self.columns = type(self).columns
        self.df      = pd.DataFrame(columns = self.columns)
        self.counter = int(0) # for unique ID purposes, not indexing
    
    def next_id(self) -> int:
        this_id = self.counter
        self.counter += 1
        return this_id
    
    def __len__(self):
        return self.n_records
    
    @property
    def n_records(self):
        return self.df.shape[0]
        
    def create(self, **kwargs):
        data = kwargs
        
        # validate keys with columns here?
        
        unique_id = self.next_id()    
        new_row = pd.DataFrame(data, columns=self.columns, index=[unique_id])
        self.df = pd.concat([self.df, new_row], ignore_index=False, axis=0)  
        return unique_id 
    
    def account_exists(self, unique_id):
        return True if unique_id in self.df.index else False
    
    def get(self, unique_id):
        if self.account_exists(unique_id):
            return self.df.loc[unique_id]
        else:
            raise ValueError(f'ID {unique_id} does not exist in this ledger')
    
    def drop(self, unique_id):
        if self.account_exists(unique_id):
            self.df.drop(unique_id, inplace=True)
            return True
        else:
            return False
    
    def issuer(self, unique_id):
        return self.df.at[unique_id, 'issuer'] # self.get(unique_id).issuer
    
    def holder(self, unique_id):
        return self.df.at[unique_id, 'holder'] # self.get(unique_id).holder
    
    def records_by_issuer(self, issuer):
        return self.df.loc[self.indexes_by_issuer(issuer)]
    
    def records_by_holder(self, holder):
        return self.df.loc[self.indexes_by_holder(holder)]
    
    def indexes_by_issuer(self, issuer):
        return self.df.index[np.where(self.df.issuer == issuer)[0]]
    
    def indexes_by_holder(self, holder):
        return self.df.index[np.where(self.df.holder == holder)[0]]
    
#%%
    
class DepositLedger(Ledger):
        
    columns = Ledger.columns.copy() + list(['overdraft'])
        
    def __init__(self, model):
        super().__init__(model)
        
    def create(self, issuer, holder, value, 
                     interest_rate=0,         # value as percentage
                     overdraft=0):
        
        return super().create(issuer=issuer, holder=holder,value=value,
                              interest_rate=interest_rate,
                              overdraft=overdraft)
    
    def current_balance(self, unique_id):
        return self.df.at[unique_id,'value']
    
    def available_funds(self, unique_id):
        return self.df.at[unique_id,'value'] + self.df.at[unique_id,'overdraft']
    
    def transfer(self,from_unique_id, to_unique_id, value):
        if (self.account_exists(from_unique_id)) & (self.account_exists(to_unique_id)):
            self.debit(from_unique_id, value)
            self.credit(to_unique_id, value)
            return True
        else:
            invalid_ids = [x for x in [from_unique_id, to_unique_id] if x not in self.df.index]
            invalid_ids = ', '.join(invalid_ids)
            raise ValueError("The following IDs do not exist in this ledger: {invalid_ids}")
    
    def credit(self, unique_id, value):        
        if self.account_exists(unique_id):
            self.df.at[unique_id, 'value'] += value
            return True
        else:
            raise ValueError(f'ID {unique_id} does not exist in this ledger')
        
    def debit(self, unique_id, value):      
        if self.account_exists(unique_id):
            self.df.at[unique_id, 'value'] -= value
            return True
        else:
            raise ValueError(f'ID {unique_id} does not exist in this ledger')
    
    def apply_daily_interest(self, issuer=None):
        if issuer is None:
            indexes = self.df.index
        else:
            indexes = self.df.index[np.where(self.df.issuer == issuer)[0]]
        
        daily_rate = (self.df.loc[indexes, 'interest_rate']/100.0)/self.model.schedule.days_in_year
        self.df.loc[indexes, 'value'] *= (1 + (daily_rate))
        
    def update_interest_rate_by_issuer(self, issuer, rate):
        indexes = self.df.index[np.where(self.df.issuer == issuer)[0]]
        
        if len(indexes)>0:
            self.df.loc[indexes, 'interest_rate'] = rate
            return True
        else:
            return False
        
#%%
   
class LoanLedger(Ledger):
        
    columns = Ledger.columns.copy() + list(['issue_date', 
                                            'maturity_date', 
                                            'mark_to_market_value',
                                            'hold_to_maturity_value'])
        
    def __init__(self, model):
        super().__init__(model)
    
    def create(self, issuer, holder, value, issue_date, maturity_date,
                     interest_rate=0,         # value as percentage
                     ):

        return super().create(issuer=issuer, holder=holder,value=value,
                              interest_rate=interest_rate,
                              issue_date=issue_date, 
                              maturity_date=maturity_date)
    
    def current_balance(self, unique_id):
        return self.df.at[unique_id, 'value']   
        
    def extend_loan(self, unique_id, value, interest_rate, maturity_days):        
        if self.account_exists(unique_id):
            self.df.at[unique_id, 'value'] += value
            self.df.at[unique_id, 'maturity_date'] = self.model.schedule.day + maturity_days
            self.df.at[unique_id, 'interest_rate'] = interest_rate
            return True
        else:
            raise ValueError(f'ID {unique_id} does not exist in this ledger')
            
    def writedown_loan(self, unique_id, value):      
        if self.account_exists(unique_id):
            self.df.at[unique_id, 'value'] -= value
            self.df.at[unique_id, 'interest_rate'] = 0
            self.df.at[unique_id, 'maturity_date'] = np.inf
            return True
        else:
            raise ValueError(f'ID {unique_id} does not exist in this ledger')
    
    def loans_due(self, date=None):
        if date == None:
            date = self.model.schedule.day
        
        return self.df.index[self.df['maturity_date'] == date]
        
        
    def apply_daily_interest(self, lender=None):
        if lender is None:
            indexes = self.df.index
        else:
            indexes = self.df.index[np.where(self.df.holder == lender)[0]]
        
        daily_rate = (self.df.loc[indexes, 'interest_rate']/100.0)/self.model.schedule.days_in_year
        self.df.loc[indexes, 'value'] *= (1 + (daily_rate))
        
    def update_interest_rate_by_lender(self, lender, rate):
        indexes = self.df.index[np.where(self.df.holder == lender)[0]]

        if len(indexes)>0:
            self.df.loc[indexes, 'interest_rate'] = rate
            return True
        else:
            return False
        
    def revalue_all(self):
        self.df.mark_to_market_value   = self.df.value
        self.df.hold_to_maturity_value = self.df.value * ((1 + (self.df.interest_rate/100))/self.model.schedule.days_in_year)**(self.maturity_date-self.model.schedule.day)
          
#%%

class BondLedger(Ledger):
        
    columns = Ledger.columns.copy() + list(['issue_date', 
                                            'maturity_date', 
                                            'maturity_days',
                                            'days_to_maturity',
                                            'number_of_outstanding_coupon_payments', 
                                            'next_coupon_date', 
                                            'mark_to_market_value', 
                                            'hold_to_maturity_value'])
    

    def __init__(self, model, annual_coupon_frequency=2):
        super().__init__(model)
        self.annual_coupon_frequency = annual_coupon_frequency
    
    @property
    def coupon_interval_days(self):
        return self.model.schedule.days_in_year/self.annual_coupon_frequency
    
    @property 
    def is_short_term(self):
        return self.df.maturity_days < self.model.schedule.days_in_year
    
    @property 
    def is_long_term(self):
        return self.df.maturity_days >= self.model.schedule.days_in_year
    
    def create(self, issuer, interest_rate, maturity_years):
        
        holder = issuer
        value = 100
        
        '''
        Maturity must be a multiple of 1 year or either 1, 3 or 6 months
        
        For maturities less than 1 year, rate must be 0 (i.e. Treasury bill)
        
        We want the maturities of similarly timed bonds to be the same regardless
        of the precise creation date. So, for example, 5 year bonds issued in one
        year all mature on the same date at the end of the 5th year. That way, we 
        dont have bonds maturing on any and every day possible. Instead they resemble
        the UK system where bonds have a particular reference year for maturation.
        
        So the issue date is fixed to the start of the current month/year depending
        on the duration
        '''
                
        if maturity_years < 0.75:
            interest_rate = 0
            issue_date = self.model.schedule.start_of_this_month
            
            if maturity_years not in [1/12, 1/4, 1/2]:
                raise ValueError('Bonds maturity must be whole number of years or 1/2, 1/4, or 1/12 years')
                
            # Round to integer number of days
            maturity_days    = np.ceil(maturity_years*self.model.schedule.days_in_year)
            maturity_date    = issue_date + maturity_days
            days_to_maturity = maturity_date - self.model.schedule.day
            number_of_outstanding_coupon_payments = 0
            next_coupon_date       = np.nan
            
        else:
            issue_date = self.model.schedule.start_of_this_year
            # Round to integer number of years and adjust for end of year maturity
            maturity_days    = np.ceil(maturity_years)*self.model.schedule.days_in_year        
            maturity_date    = issue_date + maturity_days
            days_to_maturity = maturity_date - self.model.schedule.day
            number_of_outstanding_coupon_payments = np.ceil(days_to_maturity/self.coupon_interval_days)
            next_coupon_date       = maturity_date - (number_of_outstanding_coupon_payments-1)*self.coupon_interval_days
        
        mark_to_market_value   = self.model.bond_exchange.yield_to_price(
                                                    self.model.schedule.day,
                                                    maturity_date,
                                                    self.model.central_bank.deposit_interest_rate, 
                                                    interest_rate,
                                                    bond_face_value=value, 
                                                    coupon_frequency=self.annual_coupon_frequency, 
                                                    days_in_year=self.model.schedule.days_in_year)
        
        hold_to_maturity_value = value + (value * ((interest_rate/100)/self.annual_coupon_frequency) * number_of_outstanding_coupon_payments)
            
        return super().create(issuer = issuer, 
                              holder = holder, 
                              value  = value,
                              interest_rate    = interest_rate,
                              issue_date       = issue_date, 
                              maturity_date    = maturity_date, 
                              maturity_days    = maturity_days, 
                              days_to_maturity = days_to_maturity, 
                              number_of_outstanding_coupon_payments=number_of_outstanding_coupon_payments, 
                              next_coupon_date = next_coupon_date,
                              mark_to_market_value   = mark_to_market_value, 
                              hold_to_maturity_value = hold_to_maturity_value)
    
    def create_bulk_value(self, issuer, bulk_value, interest_rate, maturity_years):
        number_of_bonds = np.ceil(bulk_value/100.0).astype(int)       
        reference_numbers = [self.create(issuer, interest_rate, maturity_years) for x in range(number_of_bonds)]
        return reference_numbers
    
    def transfer(self, idval, new_holder):
        bond = self.get(idval)
            
        if bond.holder != new_holder:
            self.df.at[idval,'holder'] = new_holder            
        else:
            raise ValueError('Bond already owned by new holder')
    
    def close(self, idval):        
        if self.account_exists(idval):
            if(self.df.at[idval, 'holder'] == self.df.at[idval, 'issuer']):
                return self.drop(idval)
            else:
                return False
        else:
            return False
        
    def recalculate(self):    
        self.df['days_to_maturity'] = self.df.maturity_date - self.model.schedule.day
        self.df['number_of_outstanding_coupon_payments'] = np.ceil(self.df.days_to_maturity/self.coupon_interval_days)
        self.df['next_coupon_date'] = self.df.maturity_date - (self.df.number_of_outstanding_coupon_payments-1)*self.coupon_interval_days
        
        self.df.loc[self.df.index[np.where(self.is_short_term)[0]], 'number_of_outstanding_coupon_payments'] = 0
        self.df.loc[self.df.index[np.where(self.is_short_term)[0]], 'next_coupon_date'] = np.nan
        
        self.df['mark_to_market_value']   = self.model.bond_exchange.yield_to_price(            
                                                    self.model.schedule.day,
                                                    self.df['maturity_date'].values,
                                                    self.model.central_bank.deposit_interest_rate, 
                                                    self.df['interest_rate'].values,
                                                    bond_face_value=self.df['value'].values, 
                                                    coupon_frequency=self.annual_coupon_frequency, 
                                                    days_in_year=self.model.schedule.days_in_year)
        
        self.df['hold_to_maturity_value'] = self.df['value'] + self.df['value'] * ((self.df['interest_rate'].values / 100) / self.annual_coupon_frequency) * self.df['number_of_outstanding_coupon_payments']
        return True
    
    def coupon_due(self, date=None):
        if date == None:
            date = self.model.schedule.day

        if len(self) == 0:
            due = False
        else:
            due = (date % (self.model.schedule.days_in_year/self.annual_coupon_frequency)) == 0
        return due
    
    def bonds_maturing(self, date=None):
        if date == None:
            date = self.model.schedule.day
        
        return self.df.index[self.df['maturity_date'] == date]


    # def self_owned_ids(self):
    #     return self.df.iloc[self.self_owned_idxs()]['unique_id'].values
        
    # def self_owned_idxs(self):
    #     return np.where(self.df['holder'] == self.issuer)[0]
    
#%%
   
class StockLedger(Ledger):
        
    columns = ['unique_id',          # Unique ID, mapped to issuers and holders
               'holder',             # Unique ID of holder
               'value',              # Value in pounds sterling
               ]
        
    def __init__(self, model):
        super().__init__(model)

#%%
   
class TaxLedger(Ledger):
        
    columns = ['unique_id',          # Unique ID, mapped to issuers and holders
               'holder',             # Unique ID of holder
               'value',              # Value in pounds sterling
               'due_date',           # Which day is tax due
               ]
        
    def __init__(self, model):
        super().__init__(model)

