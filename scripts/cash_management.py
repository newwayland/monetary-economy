# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 12:30:00 2024

@author: andre
"""


import numpy as np
from agent_based_economy.model  import Model
from agent_based_economy.accounting import BalanceSheet

#%% Aim

'''
####################################################################################
The logic below needs to be incorporated into the daily behaviours of the government
and banks. This is just work in progress of the logic.
####################################################################################

Set up economy with n banks

Government spends an amount into each bank each day
    This is intended to represent a deficit spend without the complication
    a real economy and taxation

At the end of each day, the cash management remit is calculated simply as the 
overdraft on the government's account at the central bank. The aim of the government
is to extinguish that overdraft due to something akin to the UK Full Funding Rule.

This example assumes a single type of bond issue each year based upon a single maturity
and coupon. This is intended to simplify portfolio management of both the government and 
the banks as there is basically only one choice (the underlying model architecture does 
support multiple bond issues but portfolio choice on the part of the agents would need
defining).

First government decides what yield it intends to sell. This is in order to set the
target selling price. In this case this is just made equal to central bank rate though
it should probably additionally include some sort of mark up above that rate to attract
bidders away from reserves (mark UP in yield, mark DOWN in price).

The quantity of bonds to be sold is maximum the number of discrete £100 bonds that can be 
bought using the value of the cash management remit at the proposed selling price. This
invariably results in a total selling value that is less than the total cash management 
remit (simply due to the discrete nature of the bonds).

Next, the banks identify their buying price for bonds, which, again, for simplicity is just
central bank rate in this case, but should probably include some mark down below the equivalent
yield on reserves. The quantity and price of bonds desired is registered with the market.

Next, the bond market clears, and the model is iterated to the next day.

Note that the day stepping function in the model includes the payment of interest 
on loans, deposits, payment of coupons on bonds as well as principal for maturing 
bonds and includes the overnight interbank market. In this case, on some days there 
are residual reserves left over from the bonds sales but these shouldnt be loaned as 
all banks are in excess.

If this is run for a few years, the rolling over of all bonds at the start of each 
year takes a greater and greater time to compute given that the stock is increasing
(linearly, at least for the first few years). This will proabbly needs to be improved.

'''

#%% Configure model

n_banks                            = 3    # number of banks to include
n_years                            = 1    # number of years to simulate
central_bank_policy_rate           = 5    # central bank rate
daily_government_spending_per_bank = 1000 
proposed_coupon                    = 0    # percent per year (across two coupons)
proposed_maturity                  = 1    # bond maturity in years

#%% Set up model

model        = Model(num_banks=n_banks, real=False)
central_bank = model.central_bank
government   = model.government
central_bank.target_interest_rate = central_bank_policy_rate

# 1 day more than the year so that maturity bonds are rolled over
days = model.schedule.days_in_year*n_years + 2

#%% Iterate days

for day in np.arange(days):
    print(f"YEAR {model.schedule.year}, DAY {model.schedule.day}")

    # Government spending
    for bank in model.banks:
        government.pay(bank.deposit_account_number, daily_government_spending_per_bank)
    
    # Organise cash management quantities 
    cash_management_requirement = np.abs(government.deposit_balance)
    proposed_yield              = central_bank.deposit_interest_rate  
    proposed_price              = model.bond_exchange.yield_to_price(model.schedule.day, model.schedule.start_of_next_year, proposed_yield, proposed_coupon)
    bonds_required              = np.floor(cash_management_requirement/proposed_price)
    bond_value_required         = bonds_required*100 # face value
    
    # Create bonds for sale
    bonds = government.create_bonds(bond_value_required, proposed_coupon, 1) # value, coupon, maturity (years)
    
    # Grab an example of one of the offered bonds
    # This is the easiest way to get the maturity date
    example_bond = model.bond_ledger.get(bonds[0])
    # Offer bonds for sale
    # Bonds are identified in the bond market by their coupon and maturity date
    government.offer_bonds(example_bond['maturity_date'], example_bond['interest_rate'], bond_value_required, proposed_price)
    
    # Banks register interest in bonds equal to entire reserve balance
    for b in model.banks:
        desired_minimum_yield = central_bank.deposit_interest_rate  
        desired_maximum_price = model.bond_exchange.yield_to_price(model.schedule.day, model.schedule.start_of_next_year, desired_minimum_yield, proposed_coupon)
        model.bond_exchange(example_bond['maturity_date'],proposed_coupon).register_interest(b, b.deposit_balance, desired_maximum_price)
    
    # Clear bond market
    model.bond_exchange(example_bond['maturity_date'],proposed_coupon).clear_market()  
    
    print(f"Bond MARKET PRICE: {model.bond_exchange(example_bond['maturity_date'],proposed_coupon).market_price}")
    
    # Iterate model day
    model.step()

#%% Output balance sheets

print(government.balance_sheet())
print(central_bank.balance_sheet())
print(BalanceSheet.consolidated_balance_sheet(model.banks, 'Banking sector'))

# Balance sheets for individual commercial banks
for b in model.banks:
    print(b.balance_sheet())

#%% Check to total quantity of final assets reflect interest level

government_balance_sheet = government.balance_sheet()
total_spending = daily_government_spending_per_bank * model.schedule.day * n_banks
print(np.abs(government_balance_sheet.equity)/total_spending)

'''
Checking the total amount of equity in the system, it comprises bonds and a residual
quantity of reserves, all based upon the government spending.

Dividing that equity by the total spending, should show how much interest has
crept into the system.

For a 5% bank rate (and bond yields based upon only that) there ends up being added
interest of about 2.5% over a year. This is half of the annual policy rate, which 
makes sense as the average age of the money injected by the government spending over 
the course of a year is half-a-year.

Running for two years pushes this to the full 5%, as in that case, the average age of 
the spending injected is 1 year.

For 3 years this increases to 7.9%
For 4 years this increases to 10.8% 

'''

#%% Check latest bond market price

bond_issues = model.bond_exchange.list_bond_issues()
print(bond_issues)
model.bond_exchange(*bond_issues[1]).market_price
# we need to clean out the earlier one as its lapsed

#%%
