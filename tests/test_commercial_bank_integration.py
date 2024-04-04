# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 20:53:51 2023

@author: andre
"""


import pytest
import pandas as pd
import numpy as np
from agent_based_economy.agents.individual import Individual
from agent_based_economy.agents.banks import CommercialBank, CentralBank
from agent_based_economy.model import Model

def test_open_deposit_account():
    model      = Model(num_banks=1, num_households=1, num_firms=10)
    bank       = model.banks[0]
    individual = model.households[0]
    
    assert individual.has_deposit_account == False
    assert individual.bank == None
    assert individual.deposit_account_number == None
    
    account_number = bank.open_deposit_account(individual)
    
    assert individual.has_deposit_account == True
    assert individual.bank == bank
    assert individual.deposit_account_number == account_number
    assert individual.deposit_balance == 0

def test_open_multiple_accounts():
    model = Model(num_banks=1, num_households=2, num_firms=10)
    bank  = model.banks[0]
    neil  = model.households[0]
    andy  = model.households[1]
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    assert neil.has_deposit_account == True
    assert andy.has_deposit_account == True
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    
def test_credit_deposit_account():
    model      = Model(num_banks=1, num_households=1, num_firms=10)
    bank       = model.banks[0]
    individual = model.households[0]
    account_number = bank.open_deposit_account(individual)
    
    assert individual.deposit_balance == 0
    bank.credit(account_number, 100)
    assert individual.deposit_balance == 100

def test_debit_deposit_account():
    model      = Model(num_banks=1, num_households=1, num_firms=10)
    bank       = model.banks[0]
    individual = model.households[0]
    account_number = bank.open_deposit_account(individual)
    bank.credit(account_number, 100)
    
    assert individual.deposit_balance == 100
    bank.debit(account_number, 39)
    assert individual.deposit_balance == 61

def test_transfer_deposit():
    model = Model(num_banks=1, num_households=2, num_firms=10)
    bank       = model.banks[0]
    neil  = model.households[0]
    andy  = model.households[1] 
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    
    bank.settle_payment(neil.deposit_account_number, andy.deposit_account_number, 24)

    assert neil.deposit_balance == 76
    assert andy.deposit_balance == 124
    
def test_transfer_deposit_between_banks():
    model = Model(num_banks=2, num_households=2, num_firms=10)
    central_bank = model.central_bank
    barclays = model.banks[0]
    natwest  = model.banks[1]
    
    assert barclays.has_deposit_account == True
    assert natwest.has_deposit_account == True
    
    assert barclays.deposit_balance == 0
    assert natwest.deposit_balance == 0
    
    central_bank.credit(barclays.deposit_account_number, 100)

    assert barclays.has_deposit_account == True
    assert natwest.has_deposit_account == True
    assert barclays.deposit_balance == 100
    assert natwest.deposit_balance == 0
    
    neil  = model.households[0]
    andy  = model.households[1]    
    barclays.open_deposit_account(neil)
    barclays.credit(neil.deposit_account_number, 100)
    natwest.open_deposit_account(andy)
    natwest.credit(andy.deposit_account_number, 100)
    
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    
    barclays.settle_payment(neil.deposit_account_number, andy.deposit_account_number, 24)

    assert neil.deposit_balance == 76
    assert andy.deposit_balance == 124   
    assert barclays.deposit_balance == 76
    assert natwest.deposit_balance == 24

#test overdraft
#test sectoral balance sheet











































    