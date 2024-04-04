# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 17:46:17 2023

@author: andre
"""

#%%

import os
import numpy as np
import matplotlib.pyplot as plt
import agent_based_economy
from agent_based_economy.model import Model
from agent_based_economy.agents.firm import Firm
from agent_based_economy.agents.household import Household
from agent_based_economy.animate import TimeseriesAnimation
import matplotlib.animation as animation

file_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(file_path)

plt.style.use('seaborn-v0_8-muted')
plt.ion()

#%%

def household_planned_consumption_units(model):
    return np.sum([h.planned_consumption for h in model.households])

def household_planned_consumption_cost(model):
    return np.sum([h.planned_consumption*h.average_goods_price/1000 for h in model.households])

def current_demand_units(model):
    return np.sum([f.current_demand for f in model.firms])

def current_demand_cost(model):
    return np.sum([f.current_demand*f.goods_price/1000 for f in model.firms])

def mean_months_since_hire_failure(model):
    return np.mean([f.months_since_hire_failure for f in model.firms])

def has_lowered_wage(model):
    return np.sum([f.lowered_wage for f in model.firms])

def has_raised_wage(model):
    return np.sum([f.raised_wage for f in model.firms])

def has_lowered_goods_price(model):
    return np.sum([f.lowered_goods_price for f in model.firms])

def has_raised_goods_price(model):
    return np.sum([f.raised_goods_price for f in model.firms])

def has_inventories_too_low(model):
    return np.sum([f.inventories_too_low for f in model.firms])

def has_inventories_too_high(model):
    return np.sum([f.inventories_too_high for f in model.firms])

def is_unhappy_at_work(model):
    return np.sum([h.is_unhappy_at_work() for h in model.households])

def total_profit(model):
    return np.sum([f.profit for f in model.firms])

#%%

days_in_month       = 21                    # working days only
num_households      = 1000
num_firms           = 100
num_banks           = 1                     # One bank, removes need for settlement
household_liquidity = 2500
firm_liquidity      = 0
firm_goods_price    = 10                    # per unit
firm_wage_rate      = 50*days_in_month      # per month 

# Firm.lambda_val = 3
# Firm.gamma      = 24
# Firm.delta      = 0.019  # wage
# Firm.upsilon    = 0.02   # price
# Household.alpha = 0.9

model_reporters={
    "Firms raising wages": has_raised_wage,
        "Employed": agent_based_economy.model.count_employed,
            "Wage": agent_based_economy.model.average_wage_rate,
    "Firms lowering wages": has_lowered_wage,
        "Inventory (units)": agent_based_economy.model.sum_inventory,
            "Price": agent_based_economy.model.average_goods_price,
    "Firms raising prices": has_raised_goods_price,
        "Houshold planned consumption (units)": household_planned_consumption_units,
            "Houshold planned consumption (cost, k)": household_planned_consumption_cost,
    "Firms lowering prices": has_lowered_goods_price,
        "Current demand (units)": current_demand_units,
            "Current demand (cost, k)": current_demand_cost,
    "Firms inventories too low": has_inventories_too_low,
        "Mean months since hire failure": mean_months_since_hire_failure,
            "Household planned saving": agent_based_economy.model.sum_hh_saving,
    "Firms inventories too high": has_inventories_too_high,
        "Household unhappy at work": is_unhappy_at_work,
            "Total firm profits": total_profit,
}

colors = ['y','r','g',
          'y','k','g',
          'y','k','g',
          'y','k','g',
          'y','y','g',
          'y','y','g']

model = Model(num_households=num_households, 
              num_firms=num_firms, 
              num_banks=num_banks, 
              firm_goods_price=firm_goods_price, 
              firm_wage_rate=firm_wage_rate,
              days_in_month=days_in_month,
              model_reporters=model_reporters
              )

model.randomly_allocate_banks(model.firms)
model.randomly_allocate_banks(model.households)
model.government_helicopter_drop(model.firms, firm_liquidity)
model.government_helicopter_drop(model.households, household_liquidity)

#%% Run and animate

'''
This is pretty slow and can probably be optimised. The first year is particularly slow
because of the significnat hiring that needs to take place to get all households employed.
'''

ani = TimeseriesAnimation(model, 
                          steps=12*50,
                          skip_days=model.schedule.days_in_year*1, 
                          n_cols=3, 
                          figsize=(10,7), 
                          colors=colors,
                          repeat=False)

plt.show()

# stop using ani.pause()
# restart using ani.resume()

#%%

#%%
