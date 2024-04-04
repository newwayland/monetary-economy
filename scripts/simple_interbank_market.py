# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 19:47:51 2024

@author: andre
"""

from agent_based_economy.model  import Model
from agent_based_economy.accounting import BalanceSheet

#%% Aim

'''
The point of this is to show one bank making a payment to another and then that
money being loaned back overnight on the interbank market.
'''

#%% Configure model

n_banks = 2
central_bank_rate = 2

#%% Set up model

model  = Model(num_banks=n_banks, real=False)

central_bank = model.central_bank
central_bank.target_interest_rate = central_bank_rate

#%% First check the balance sheets

# central bank
print(central_bank.balance_sheet()) 

# Commercial banks
for b in model.banks:               
    print(b.balance_sheet())

# Consolidated banking sector
print(BalanceSheet.consolidated_balance_sheet(model.banks, 'Banking sector'))

'''All balance sheets are entirely zero'''

#%% Make a payment from one bank to another
 
# This occurs at the central bank reserve level
model.banks[0].pay(model.banks[1].deposit_account_number, 100)
    
#%% Check the balance sheets again

# central bank
print(central_bank.balance_sheet()) 

# Commercial banks
for b in model.banks:               
    print(b.balance_sheet())

# Consolidated banking sector
print(BalanceSheet.consolidated_balance_sheet(model.banks, 'Banking sector'))

'''
Central bank has expanded, now has 100 reserve liabilities and 100 overdraft asset
The paying commercial bank as an overdraft liability of 100
The recipient bank has a reserve asset of 100

The consolidated banking sector balance sheet mirrors the central banks, reserve
assets and overdraft liabilities
'''

#%% Iterate to the next day

# This triggers the interbank market clearing
model.step()
    
#%% Check the balance sheets again

# central bank
print(central_bank.balance_sheet()) 

# Commercial banks
for b in model.banks:               
    print(b.balance_sheet())

# Consolidated banking sector
print(BalanceSheet.consolidated_balance_sheet(model.banks, 'Banking sector'))

'''
Central bank balance sheet has contracted to all zeros
The paying commercial bank as a loan liability of 100
The recipient bank has a loan asset of 100

Consolidated banking sector is at zero - assets and liabilities cancelling
within the sector.
'''
    
#%%
    
#%%