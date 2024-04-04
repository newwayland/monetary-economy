# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 20:32:00 2024

@author: andre
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 20:14:23 2024

@author: andre
"""

from agent_based_economy.model  import Model

#%% Aim

'''
The point of this is to show households borrowing from a bank.
'''

#%% Create model

# firms, households and banks must be at least of size 1
model = Model(num_households=1, num_firms=1, num_banks=1)

bank  = model.banks[0]
andy  = model.households[0]

#%% Inspect balance sheets

print(bank.balance_sheet()) 
print(andy.balance_sheet()) 

'''Entirely zeros'''

#%% Open accounts for both households and credit 100 to each

deposit_account_number = bank.open_deposit_account(andy)
loan_account_number    = andy.open_borrowing_account(bank)           
bank.grant_loan(loan_account_number, deposit_account_number, 50, 1) # value, interest rate

print(bank.balance_sheet()) 
print(andy.balance_sheet()) 

'''
Bank has loan asset and deposit liabilities
Household has loan laibility and deposit asset
'''

#%% Get loan details

loans = andy.get_all_issued_borrowing_accounts() # returns dataframe slice

print(loans.iloc[0])
# issuer                         Household: 2875566484944
# holder                    CommercialBank: 2875570737552
# value                                                50
# interest_rate                                       1.0
# issue_date                                            0
# maturity_date                                     252.0
# mark_to_market_value                                NaN
# hold_to_maturity_value                              NaN

#%%

#%%

