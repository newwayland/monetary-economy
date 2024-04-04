# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 20:41:17 2024

@author: andre
"""

from agent_based_economy.model  import Model
from agent_based_economy.accounting import BalanceSheet

#%% Aim

'''Highlight balance sheet outputs'''

#%% Configure model

firm_liquidity = 100
household_liquidity = 50

#%% Setup model

model = Model()
model.randomly_allocate_banks(model.firms)
model.randomly_allocate_banks(model.households)
model.government_helicopter_drop(model.firms, firm_liquidity)
model.government_helicopter_drop(model.households, household_liquidity)

#%% Print agent balance sheets

_ = [print(x.balance_sheet()) for x in model.households]
_ = [print(x.balance_sheet()) for x in model.firms]
_ = [print(x.balance_sheet()) for x in model.banks]
print(model.central_bank.balance_sheet())
print(model.government.balance_sheet())

#%% Print consolidated sector balance sheets

# Takes a minute to accumulate over some sectors

print(BalanceSheet.consolidated_balance_sheet(model.households, 'Household sector'))
print(BalanceSheet.consolidated_balance_sheet(model.firms, 'Firm sector'))
print(BalanceSheet.consolidated_balance_sheet(model.banks, 'Banking sector'))
print(BalanceSheet.consolidated_balance_sheet([model.central_bank], 'Central bank'))
print(BalanceSheet.consolidated_balance_sheet([model.government], 'Government'))
print(BalanceSheet.consolidated_balance_sheet([model.central_bank, model.government], 'Consolidated government sector'))
print(BalanceSheet.consolidated_balance_sheet(model.banks + [model.central_bank], 'Consolidated banking sector'))

#%% Drill down in to balance sheet items

# Get as dictionaries
government_liabilities = model.government.balance_sheet().liabilities
government_assets = model.government.balance_sheet().assets

print(government_liabilities)
print(government_assets)

# Alternative
government_liabilities = model.government.liabilities_dict()
government_assets = model.government.assets_dict()

print(government_liabilities)
print(government_assets)

#%%

#%%