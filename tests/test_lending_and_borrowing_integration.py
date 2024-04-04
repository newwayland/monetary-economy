# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 19:13:27 2023

@author: andre
"""



import pytest
import pandas as pd
import numpy as np

from agent_based_economy.agents.individual import Individual
from agent_based_economy.agents.banks import CommercialBank
from agent_based_economy.model import Model

def test_no_lending_relationship():    
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    assert neil.has_borrowing_account_with_lender(andy) == False
    assert andy.has_borrowing_account_with_lender(neil) == False
    assert neil.has_lending_account_with_borrower(andy) == False
    assert andy.has_lending_account_with_borrower(neil) == False
    
def test_open_loan_account():     
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    neil.open_borrowing_account(andy)
    
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    assert neil.has_borrowing_account_with_lender(andy) == True
    assert andy.has_borrowing_account_with_lender(neil) == False
    assert neil.has_lending_account_with_borrower(andy) == False
    assert andy.has_lending_account_with_borrower(neil) == True
    
    neil.loan_balance_by_lender(andy) == 0
    
def test_loan_account_access():    
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    neil.open_borrowing_account(andy)
    assert andy.get_lending_account_number_by_borrower(neil) == neil.get_borrowing_account_number_by_lender(andy)
    
    account_number = neil.get_borrowing_account_number_by_lender(andy)
    assert andy.get_lending_account_number_by_borrower(neil) == account_number
    
    assert neil.get_borrowing_account_by_account_number(account_number).holder == andy
    assert andy.get_lending_account_by_account_number(account_number).issuer == neil

def test_cant_open_multiple_accounts_with_same_lender():   
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
    rich  = model.households[2]
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy, rich]]
    [bank.credit(x, 100) for x in account_numbers]
    
    # government already has first borrowing acc with CB
    assert neil.open_borrowing_account(andy) == 1 # new account number
    assert rich.open_borrowing_account(andy) == 2 # new account number
    assert neil.open_borrowing_account(andy) == 1 # existing account number
    
def test_cant_open_borrowing_accounts_with_no_bank_access():
    # This is not because banks are the only lenders but because loans are
    # settled with bank deposits between counterparties 
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
    rich  = model.households[2]
    
    # NO ACCOUNT FOR RICH
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    assert neil.open_borrowing_account(andy) == 1 # new account number
    with pytest.raises(Exception):
        rich.open_borrowing_account(andy) # new account number
    assert neil.has_borrowing_account_with_lender(andy) == True
    assert rich.has_borrowing_account_with_lender(andy) == False
    
def test_default_loan_rate():
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
      
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    account_number = neil.open_borrowing_account(andy)  
    account_record = neil.get_lending_account_by_account_number(account_number)
    assert andy.loan_interest_rate == 0
    assert account_record.interest_rate == 0
    
def test_custom_loan_rate():
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
     
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    andy.loan_interest_rate = 5
    
    account_number = neil.open_borrowing_account(andy)  
    account_record = neil.get_lending_account_by_account_number(account_number)
    assert andy.loan_interest_rate == 5
    assert account_record.interest_rate == 5

def test_grant_loan():    
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
        
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    loan_account_number = neil.open_borrowing_account(andy)     
    
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    assert neil.loan_balance_by_lender(andy) == 0
     
    andy.grant_loan(loan_account_number, deposit_account_numbers[0], 50, 1)
    
    assert neil.deposit_balance == 150
    assert andy.deposit_balance == 50
    assert neil.loan_balance_by_lender(andy) == 50

def test_grant_loan_helper_method():    
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
       
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    neil.open_borrowing_account(andy)     
    
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    assert neil.loan_balance_by_lender(andy) == 0
     
    andy.grant_loan_to_borrower(neil, 50, 1)
    
    assert neil.deposit_balance == 150
    assert andy.deposit_balance == 50
    assert neil.loan_balance_by_lender(andy) == 50
    
def test_grant_loan_assets_and_liabilities():    
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
      
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    loan_account_number = neil.open_borrowing_account(andy)       
    andy.grant_loan(loan_account_number, deposit_account_numbers[0], 50, 1)
    
    neil_liabilities = neil.liabilities_dict()
    neil_assets      = neil.assets_dict()
    andy_liabilities = andy.liabilities_dict()
    andy_assets      = andy.assets_dict()
    
    assert neil_liabilities == {'loans': 50.0, 'overdraft': 0.0}
    assert neil_assets == {'bonds': 0.0, 'deposit': 150.0, 'loans': 0.0}
    assert andy_liabilities == {'loans': 0.0, 'overdraft': 0.0}
    assert andy_assets == {'bonds': 0.0, 'deposit': 50.0, 'loans': 50.0}
    
def test_repay_loan():
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
     
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    loan_account_number = neil.open_borrowing_account(andy)       
    andy.grant_loan(loan_account_number, deposit_account_numbers[0], 50, 1)
    
    assert neil.deposit_balance == 150
    assert andy.deposit_balance == 50
    assert neil.loan_balance_by_lender(andy) == 50

    neil.make_loan_repayment(25, andy)
    
    assert neil.deposit_balance == 125
    assert andy.deposit_balance == 75
    assert neil.loan_balance_by_lender(andy) == 25

def test_overpaying_loan_just_settles_balance():
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
       
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    loan_account_number = neil.open_borrowing_account(andy)       
    andy.grant_loan(loan_account_number, deposit_account_numbers[0], 50, 1)
    
    assert neil.deposit_balance == 150
    assert andy.deposit_balance == 50
    assert neil.loan_balance_by_lender(andy) == 50

    neil.make_loan_repayment(70, andy)
    
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    assert neil.loan_balance_by_lender(andy) == 0
    
def test_no_lending_relationship_with_bank():    
    model = Model()
    bank  = model.banks[0]   
    andy  = model.households[1] 
       
    account_number = bank.open_deposit_account(andy)
    bank.credit(account_number, 100)
    
    assert andy.deposit_balance == 100
    assert andy.has_borrowing_account_with_lender(bank) == False
    
def test_open_loan_account_with_bank():     
    model = Model()
    bank  = model.banks[0]   
    andy  = model.households[1] 
    
    account_number = bank.open_deposit_account(andy)
    bank.credit(account_number, 100)
    
    andy.open_borrowing_account(bank)
    
    assert andy.deposit_balance == 100
    assert andy.has_borrowing_account_with_lender(bank) == True
    assert bank.has_lending_account_with_borrower(andy) == True
    
    andy.loan_balance_by_lender(bank) == 0
    
def test_loan_account_access_with_bank():     
    model = Model()
    bank  = model.banks[0]   
    andy  = model.households[1] 
    
    account_number = bank.open_deposit_account(andy)
    bank.credit(account_number, 100)
    
    andy.open_borrowing_account(bank)
    
    assert bank.get_lending_account_number_by_borrower(andy) == andy.get_borrowing_account_number_by_lender(bank)
    
    account_number = andy.get_borrowing_account_number_by_lender(bank)
    assert bank.get_lending_account_number_by_borrower(andy) == account_number
    
    assert andy.get_borrowing_account_by_account_number(account_number).holder == bank
    assert bank.get_lending_account_by_account_number(account_number).issuer == andy

def test_cant_open_multiple_accounts_with_same_bank():
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
    rich  = model.households[2]

    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy, rich]]
    
    assert neil.open_borrowing_account(bank) == 1 # new account number
    assert rich.open_borrowing_account(bank) == 2 # new account number
    assert neil.open_borrowing_account(bank) == 1 # existing account number
    
def test_cant_open_borrowing_accounts_with_bank_if_no_bank_access():
    # This is not because banks are the only lenders but because loans are
    # settled with bank deposits between counterparties
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    
    rich  = model.households[2] 
    
    # NO ACCOUNT FOR RICH
    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    assert neil.open_borrowing_account(bank) == 1 # new account number
    with pytest.raises(Exception):
        rich.open_borrowing_account(bank) # new account number
    assert neil.has_borrowing_account_with_lender(bank) == True
    assert rich.has_borrowing_account_with_lender(bank) == False
    
def test_default_loan_rate_with_bank():   
    model = Model()
    bank  = model.banks[0]
    andy  = model.households[1]    
    
    account_number = bank.open_deposit_account(andy)
    bank.credit(account_number, 100)
    
    account_number = andy.open_borrowing_account(bank)
    account_record = andy.get_lending_account_by_account_number(account_number)
    assert bank.loan_interest_rate == 0
    assert account_record.interest_rate == 0
    
def test_custom_loan_rate_with_bank():
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]    

    account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in account_numbers]
    
    bank.loan_interest_rate = 5
    
    account_number = andy.open_borrowing_account(bank)  
    account_record = andy.get_lending_account_by_account_number(account_number)
    assert bank.loan_interest_rate == 5
    assert account_record.interest_rate == 5

def test_grant_loan_with_bank():    
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]  
    
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    loan_account_number = neil.open_borrowing_account(andy)     
    
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    assert neil.loan_balance_by_lender(andy) == 0
     
    andy.grant_loan(loan_account_number, deposit_account_numbers[0], 50, 1)
    
    assert neil.deposit_balance == 150
    assert andy.deposit_balance == 50
    assert neil.loan_balance_by_lender(andy) == 50

def test_grant_loan_helper_method_with_bank():    
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]  
    
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    loan_account_number = neil.open_borrowing_account(bank)     
    
    assert neil.deposit_balance == 100
    assert andy.deposit_balance == 100
    assert neil.loan_balance_by_lender(bank) == 0
     
    bank.grant_loan_to_borrower(neil, 50, 1)
    
    assert neil.deposit_balance == 150
    assert andy.deposit_balance == 100 ### ADD CHECK ON BANK LEDGER AND RESERVES?
    assert neil.loan_balance_by_lender(bank) == 50
    
def test_grant_loan_assets_and_liabilities_with_bank():    
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]  
    
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    neil.open_borrowing_account(bank)          
    bank.grant_loan_to_borrower(neil, 50, 1)
    
    neil_liabilities = neil.liabilities_dict()
    neil_assets      = neil.assets_dict()
    bank_liabilities = bank.liabilities_dict()
    bank_assets      = bank.assets_dict()
        
    assert neil_liabilities == {'loans': 50.0, 'overdraft': 0.0}
    assert neil_assets == {'bonds': 0.0, 'deposit': 150.0, 'loans': 0.0}
    assert bank_liabilities == {'deposits': 250.0, 'loans': 0.0, 'overdraft': 0.0}
    assert bank_assets == {'loans': 50.0, 'bonds': 0.0, 'overdrafts': 0.0, 'reserves': 0.0}
    
def test_repay_loan_with_bank():
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]  
    
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    loan_account_number = neil.open_borrowing_account(bank)       
    bank.grant_loan(loan_account_number, deposit_account_numbers[0], 50, 1)
    
    assert neil.deposit_balance == 150
    assert neil.loan_balance_by_lender(bank) == 50

    neil.make_loan_repayment(25, bank)
    
    assert neil.deposit_balance == 125
    assert neil.loan_balance_by_lender(bank) == 25

def test_overpaying_loan_just_settles_balance_with_bank():
    model = Model()
    bank  = model.banks[0]
    neil  = model.households[0]    
    andy  = model.households[1]  
    
    deposit_account_numbers = [bank.open_deposit_account(x) for x in [neil, andy]]
    [bank.credit(x, 100) for x in deposit_account_numbers]
    
    loan_account_number = neil.open_borrowing_account(bank)       
    bank.grant_loan(loan_account_number, deposit_account_numbers[0], 50, 1)
    
    assert neil.deposit_balance == 150
    assert neil.loan_balance_by_lender(bank) == 50

    neil.make_loan_repayment(70, bank)
    
    assert neil.deposit_balance == 100
    assert neil.loan_balance_by_lender(andy) == 0
    
    
#%%
    
    