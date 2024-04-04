# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 20:57:35 2024

@author: andre
"""

import numpy as np
from agent_based_economy.model import Model
from agent_based_economy.accounting import BalanceSheet

#%% Aim

'''
Just show a series of government payments to the private sector
These could be social security or job guarantee or regular wages
'''

#%% Configure

n_banks = 3

#%% Set up

model  = Model(num_banks=n_banks, real=False)

model.randomly_allocate_banks(model.firms)
model.randomly_allocate_banks(model.households)

#%% make daily payments to everyone

for d in np.arange(100):
    [model.government.pay(hh.deposit_account_number, 1) for hh in model.households]
    model.step()

#%% inspect balance sheets

print(model.government.balance_sheet())
print(model.central_bank.balance_sheet())
print(BalanceSheet.consolidated_balance_sheet(model.banks, 'Banking sector'))

for b in model.banks:
    print(b.balance_sheet())

#%%