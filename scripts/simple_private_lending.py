# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 20:14:23 2024

@author: andre
"""

import numpy as np
from agent_based_economy.model  import Model
from agent_based_economy.agents.banks import CommercialBank
from agent_based_economy.agents.household import Household
from agent_based_economy.accounting import BalanceSheet

#%% Aim

'''
The point of this is to show households lending to each other.
'''

#%% Create model

# firms, households and banks must be at least of size 1
model = Model(num_households=2, num_firms=1, num_banks=1)

bank  = model.banks[0]
neil  = model.households[0]
andy  = model.households[1]

#%% Inspect balance sheets

print(bank.balance_sheet()) 
print(neil.balance_sheet()) 
print(andy.balance_sheet()) 

'''Entirely zeros'''

#%% Open accounts for both households and credit 100 to each

deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
[bank.credit(x, 100) for x in deposit_account_numbers]

print(bank.balance_sheet()) 
print(neil.balance_sheet()) 
print(andy.balance_sheet()) 

'''
Bank has deposit liabilities
Households have deposit assets
'''

#%%

loan_account_number = neil.open_borrowing_account(andy)       
andy.grant_loan(loan_account_number, deposit_account_numbers[0], 50, 1) # value, interest rate

print(bank.balance_sheet()) 
print(neil.balance_sheet()) 
print(andy.balance_sheet()) 

'''
Bank has deposit liabilities
Households have deposit assets but also a loan relationship between each other
'''

#%%