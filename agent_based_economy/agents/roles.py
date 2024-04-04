# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 16:20:52 2022

@author: ABE
"""

import math 
import numpy as np
    
class DepositIssuer:  
    __slots__ = ()
    
    def __init__(self):
        self._deposit_interest_rate = 0          
        self.liability_keys = self.liability_keys + ['_deposit_liabilities']
        self.asset_keys = self.asset_keys + ['_overdraft_assets']
    
    @property
    def deposit_interest_rate(self):
         return self._deposit_interest_rate
     
    @deposit_interest_rate.setter
    def deposit_interest_rate(self, rate):
         self._deposit_interest_rate = rate
         self._assign_deposit_rate()
         
    def open_deposit_account(self, holder, overdraft = 0):        
        if holder.bank == None:
            idx = self.model.deposit_ledger.create(self, holder, 0,
                                        self.deposit_interest_rate,
                                        overdraft)

            holder.bank = self
            holder.deposit_account_number = idx               
            return idx
        else:
            raise Exception("Agent already has an existing bank account") 
    
    def close_deposit_account(self, unique_id):
        account = self.model.deposit_ledger.get(unique_id)
        if account.issuer == self:
            self.model.deposit_ledger.drop(unique_id)
            return True
        else:
            return False
    
    def authenticate_deposit_account(self, account_number):
        return True if self.model.deposit_ledger.issuer(account_number) == self else False
    
    def clear_payment(self, from_account, to_account, value):
        if self.model.deposit_ledger.account_exists(from_account) and \
           self.model.deposit_ledger.account_exists(to_account) and \
           self.authenticate_deposit_account(from_account):
               
            return True if (self.model.deposit_ledger.available_funds(from_account) >= value) else False
        else:
            raise Exception('Specified accounts cannot be identified')
               
    def settle_payment(self, from_account_number, to_account_number, value):
        
        if self.clear_payment(from_account_number, to_account_number, value):
            '''
            1. Both accounts at this bank (whether commercial or central)
            2. Other account at other bank (both commercial)
            3. Credit a commercial bank account and reserves (government spending)
            4. Debit a commercial account and reserves (taxation)
            5. Central bank credit a commercial (bond purchase, no end customer)
            '''
                              
            to_bank = self.model.deposit_ledger.issuer(to_account_number)
            
            if self == to_bank:            
                '''Simple ledger update within single bank'''
                
                self.model.deposit_ledger.transfer(from_account_number, to_account_number, value)
                
            elif (self.is_commercial and to_bank.is_commercial):
                '''
                Different banks. 
                Update individual deposit ledger records as two separate steps
                Then settle between banks mutual reserve accounts
                '''
                
                self.debit(from_account_number, value, authenticated=True) 
                to_bank.credit(to_account_number, value, authenticated=True)
                self.bank.settle_payment(self.deposit_account_number, to_bank.deposit_account_number, value)
                
            elif (self.is_central and to_bank.is_commercial):
                '''
                This is central bank making payment to an account at a commercial bank
                  e.g. government paying firms
                Central bank account holder credited reserves
                And target bank marks up recipient account
                '''
                
                to_bank.credit(to_account_number, value, authenticated=True)
                self.settle_payment(from_account_number, to_bank.deposit_account_number, value)
                
            elif (self.is_commercial and to_bank.is_central):
                '''
                This is commercial bank making payment to an account at a central bank
                   e.g. firm paying tax
                Central bank account holder depoited reserves
                Paying bank debits paying account
                '''
                
                self.debit(from_account_number, value, authenticated=True) 
                self.bank.settle_payment(self.deposit_account_number, to_bank.deposit_account_number, value)
        else:
            raise Exception('Insufficient funds for requested transfer')
            
    def credit(self, idx, value, authenticated=False):
        if authenticated | self.authenticate_deposit_account(idx):
            self.model.deposit_ledger.credit(idx, value)
            return True
        else:
            return False
        
    def debit(self, idx, value, authenticated=False):
        if authenticated | self.authenticate_deposit_account(idx):
            self.model.deposit_ledger.debit(idx, value)
            return True
        else:
            return False
    
    def pay_interest(self):
        self.model.deposit_ledger.apply_daily_interest(issuer=self)
        
    def get_all_issued_deposit_accounts(self, except_counterparties=[]):
        return self.model.deposit_ledger.df.iloc[np.where((self.model.deposit_ledger.df.issuer == self)&(~self.model.deposit_ledger.df.holder.isin(except_counterparties)))[0]]
    
    def _deposit_liabilities(self, except_counterparties=[]):
        all_accounts = self.get_all_issued_deposit_accounts(except_counterparties=except_counterparties)
        return ('deposits', all_accounts.iloc[np.where(all_accounts['value']>=0)[0]].value.sum())
    
    def _overdraft_assets(self, except_counterparties=[]):
        all_accounts = self.get_all_issued_deposit_accounts(except_counterparties=except_counterparties)
        return ('overdrafts', np.abs(all_accounts.iloc[np.where(all_accounts['value']<0)[0]].value.sum()))
    
    def _assign_deposit_rate(self):
        self.model.deposit_ledger.update_interest_rate_by_issuer(self, self.deposit_interest_rate)

#%%

class DepositHolder:     
    __slots__ = ()
    
    def __init__(self): 
        self.bank = None
        self.deposit_account_number = None            
        self.asset_keys = self.asset_keys + ['_deposit_asset']           
        self.liability_keys = self.liability_keys + ['_overdraft_liability']
    
    def open_deposit_account(self, bank, overdraft=0):
        idx = bank.open_deposit_account(self, overdraft)
        return idx
    
    @property
    def has_deposit_account(self):
        return True if self.deposit_account_number is not None else False  # check if in ledger?
    
    @property
    def deposit_balance(self):
        return self.model.deposit_ledger.current_balance(self.deposit_account_number) if self.has_deposit_account else 0
    
    @property
    def agreed_overdraft(self):
        return self.model.deposit_ledger.df.at[self.deposit_account_number, 'overdraft'] if self.has_deposit_account else 0
    
    @property   
    def available_funds(self):
        return self.deposit_balance + self.agreed_overdraft
        
    def has_available_funds(self, value):
        return True if value < self.available_funds else False
    
    def pay(self, recipient_account_number, value):
        self.bank.settle_payment(self.deposit_account_number, recipient_account_number, value)

    def _deposit_asset(self, except_counterparties=[]):
        return ('deposit', self.deposit_balance if (self.bank not in except_counterparties) and (self.deposit_balance > 0) else 0)

    def _overdraft_liability(self, except_counterparties=[]):    
        return ('overdraft', np.abs(self.deposit_balance) if (self.bank not in except_counterparties) and (self.deposit_balance < 0) else 0)
    
#%%

class ReserveHolder(DepositHolder):       
    __slots__ = ()
      
    def __init__(self): 
        self.bank = None
        self.deposit_account_number = None            
        self.asset_keys = self.asset_keys + ['_reserve_asset']         
        self.liability_keys = self.liability_keys + ['_overdraft_liability']
    
    def _reserve_asset(self, except_counterparties=[]):
        return ('reserves', self.deposit_balance if (self.bank not in except_counterparties) and (self.deposit_balance > 0) else 0)

    def _overdraft_liability(self, except_counterparties=[]):    
        return ('overdraft', np.abs(self.deposit_balance) if (self.bank not in except_counterparties) and (self.deposit_balance < 0) else 0)
    
class ReserveIssuer(DepositIssuer):      
    __slots__ = ()
          
    def __init__(self):
        self.deposit_interest_rate = 0         
        self.liability_keys = self.liability_keys + ['_reserve_liabilities']
        self.asset_keys = self.asset_keys + ['_overdraft_assets']
    
    def _reserve_liabilities(self, except_counterparties=[]):
        all_accounts = self.get_all_issued_deposit_accounts(except_counterparties=except_counterparties)
        return ('reserves', all_accounts.iloc[np.where(all_accounts['value']>=0)[0]].value.sum())
    
    def _overdraft_assets(self, except_counterparties=[]):
        all_accounts = self.get_all_issued_deposit_accounts(except_counterparties=except_counterparties)
        return ('overdrafts', np.abs(all_accounts.iloc[np.where(all_accounts['value']<0)[0]].value.sum()))
    
#%%

class Lender:              
    __slots__ = ()
    
    def __init__(self):                 
        self._loan_interest_rate = 0 
        self._default_loan_maturity_days = self.model.schedule.days_in_year
        self.asset_keys = self.asset_keys + ['_loan_assets']
     
    @property
    def loan_interest_rate(self):
         return self._loan_interest_rate
     
    @loan_interest_rate.setter
    def loan_interest_rate(self, rate):
         self._loan_interest_rate = rate
    
    @property
    def default_loan_maturity_days(self):
         return self._default_loan_maturity_days
     
    @default_loan_maturity_days.setter
    def default_loan_maturity_days(self, days):
         self._default_loan_maturity_days = days
         self._assign_loan_rate()
         
    def open_lending_account(self, borrower):
        if (borrower.has_deposit_account):
            if (self.has_lending_account_with_borrower(borrower)):
                return self.get_lending_account_number_by_borrower(borrower)
            else:
                idx = self.model.loan_ledger.create(borrower, self, 0,
                                                    self.model.schedule.day,
                                                    np.inf,
                                                    self.loan_interest_rate
                                                    )
                return idx
        else:
            raise Exception("Agent doesn't have an existing bank account") 
    
    def authenticate_lending_account(self, account_number):
        return True if self.model.loan_ledger.holder(account_number) == self else False
    
    def has_lending_account_with_borrower(self, borrower):
        return np.any((self.model.loan_ledger.df.holder == self)&(self.model.loan_ledger.df.issuer == borrower))
    
    def get_lending_account_by_borrower(self, borrower):
        account_number = self.get_lending_account_number_by_borrower(borrower)
        return self.get_lending_account_by_account_number(account_number)
        
    def get_lending_account_by_account_number(self, unique_id):
        return self.model.loan_ledger.df.loc[unique_id]
        
    def get_lending_account_number_by_borrower(self, borrower):
        return self.model.loan_ledger.df.index[np.where((self.model.loan_ledger.df.holder == self)&(self.model.loan_ledger.df.issuer == borrower))[0]][0]
    
    def grant_loan_to_borrower(self, borrower, value, interest_rate, maturity_days=None):
        loan_account_number = self.get_lending_account_number_by_borrower(borrower)
        deposit_account_number = borrower.deposit_account_number
        return self.grant_loan(loan_account_number, deposit_account_number, value, interest_rate, maturity_days)
    
    def grant_loan(self, loan_account_number, deposit_account_number, value, interest_rate, maturity_days=None):
        '''
        First ensure the loan can be extended and then settled in bank deposits.
        Either the lender is a bank in which case a deposit account is credited as an 
        overall balance sheet expansion of both parties
        Or the lender is just a deposit holder in which deposits are transferred. This 
        enables simple systems of IOUs to be supported as loans exchanged for deposits
        '''        
        
        if maturity_days is None:
            maturity_days = self.default_loan_maturity_days
        
        borrower = self.get_lending_account_by_account_number(loan_account_number).issuer
        
        if self.authenticate_lending_account(loan_account_number):    
            if (self.is_bank & self.is_central) | (self.is_bank & self.is_commercial & ~borrower.is_bank):
                if self.authenticate_deposit_account(deposit_account_number):
                    self.model.loan_ledger.extend_loan(loan_account_number, value, interest_rate, maturity_days)
                    self.credit(deposit_account_number, value)
                    return True
                else:
                    raise Exception("Loan and deposit account must be held at lending bank")  
            else:
                if self.has_deposit_account:
                    self.model.loan_ledger.extend_loan(loan_account_number, value, interest_rate, maturity_days)
                    self.pay(deposit_account_number, value)
                    return True
                else:
                    raise Exception("Funds not available to support loan")  
                    
        else:
            raise Exception("Loan and deposit account must be held at this bank")    
    
    def writedown_loan(self, account_number, value, authenticated=False):
        if authenticated | self.authenticate_lending_account(account_number):
            self.model.loan_ledger.writedown_loan(account_number, value)
            return True
        else:
            return False
        
    def get_all_held_lending_accounts(self, except_counterparties=[]):
        return self.model.loan_ledger.df.iloc[np.where((self.model.loan_ledger.df.holder == self)&(~self.model.loan_ledger.df.issuer.isin(except_counterparties)))[0]]
    
    def _loan_assets(self, except_counterparties=[]):
        return ('loans', self.get_all_held_lending_accounts(except_counterparties=except_counterparties).value.sum())
    
    def _assign_loan_rate(self):
        self.model.loan_ledger.update_interest_rate_by_lender(self, self.loan_interest_rate)
    
#%%
    
class Borrower:     
    __slots__ = ()
    
    def __init__(self):    
        self.liability_keys = self.liability_keys + ['_loan_liabilities']
        
    def open_borrowing_account(self, lender):
        idx = lender.open_lending_account(self)
        return idx    
    
    def arrange_loan(self, lender, value, maturity_days=None):
        if self.has_loan_account(lender):
            self.bank.grant_loan(self.loan_account_number, self.deposit_account_number, value, maturity_days)
            return True
        else:
            raise Exception("Agent doesn't have an existing bank account") 
    
    def has_borrowing_account_with_lender(self, lender):
        return np.any((self.model.loan_ledger.df.issuer == self)&(self.model.loan_ledger.df.holder == lender))
    
    def get_borrowing_account_by_lender(self, lender):
        account_number = self.get_borrowing_account_number_by_lender(lender)
        return self.get_borrowing_account_by_account_number(account_number)
        
    def get_borrowing_account_by_account_number(self, unique_id):
        return self.model.loan_ledger.df.loc[unique_id]
        
    def get_borrowing_account_number_by_lender(self, lender):
        return self.model.loan_ledger.df.index[np.where((self.model.loan_ledger.df.issuer == self)&(self.model.loan_ledger.df.holder == lender))[0]][0]
    
    def loan_balance_by_lender(self, lender):
        return self.get_borrowing_account_by_lender(lender).value if self.has_borrowing_account_with_lender(lender) else 0
    
    def loan_balance_by_account_number(self, unique_id):
        return self.model.loan_ledger.df.at[unique_id, 'value']
            
    def make_loan_repayment(self, value, lender=None, account_number=None):
        if lender is not None:
            loan_account = self.get_borrowing_account_by_lender(lender)
        elif account_number is not None:
            loan_account = self.get_borrowing_account_by_account_number(account_number)
        else:
            raise ValueError('Must specify a lender or a loan account number')
            
        loan_balance = loan_account.value
        
        if loan_balance < value:
            value = loan_balance
            
        if self.has_available_funds(value):
            if loan_account.holder.is_bank:
                self.bank.debit(self.deposit_account_number, value)
                loan_account.holder.writedown_loan(loan_account.name, value)
                return True
            elif loan_account.holder.has_deposit_account:
                self.pay(loan_account.holder.deposit_account_number, value)                
                loan_account.holder.writedown_loan(loan_account.name, value)
                return True
            else:
                raise ValueError('Cannot arrange repayment')
        else:
            raise ValueError('Insufficient funds available')
    
    # def net_off_loan_and_deposit(self):
    #     deposit_balance = self.deposit_balance
    #     loan_balance    = self.loan_balance
        
    #     if deposit_balance < 0:
    #         self.arrange_loan(np.abs(deposit_balance))
    #     elif deposit_balance >= loan_balance:
    #         self.make_loan_repayment(loan_balance)
    #     else:
    #         self.make_loan_repayment(deposit_balance)
    
    def get_all_issued_borrowing_accounts(self, except_counterparties=[]):
        return self.model.loan_ledger.df.iloc[np.where((self.model.loan_ledger.df.issuer == self)&(~self.model.loan_ledger.df.holder.isin(except_counterparties)))[0]]
    
    def _loan_liabilities(self, except_counterparties=[]):
        return ('loans', self.get_all_issued_borrowing_accounts(except_counterparties=except_counterparties).value.sum())
    
#%%

class BondIssuer:     
    __slots__ = ()
    
    # Cant be a bond hold and a bond issuer at present
    # Both ledgers/portfolios are called .bonds
    
    def __init__(self):
        self.liability_keys = self.liability_keys + ['_bond_liabilities']
    
    def create_bonds(self, value, rate, maturity_years):
        new_bond_references = self.model.bond_ledger.create_bulk_value(self, value, rate, maturity_years)
        example_bond = self.model.bond_ledger.get(new_bond_references[0])
        self.model.bond_exchange.register_bond_issue(example_bond['maturity_date'], rate)
        return new_bond_references
    
    def buy_bond(self, seller, price, idx):
        # assume only buy back own bonds for now
        seller.sell_bond(self, price, idx)
    
    def sell_bond(self, buyer, price, idx):
        # Only sell own bonds
        buyer.pay(self.deposit_account_number, price)
        self.model.bond_ledger.transfer(idx,buyer)
        
    def offer_bonds(self, maturity_date, coupon_rate, quantity, price):
        market = self.model.bond_exchange.get_market(maturity_date, coupon_rate)
        market.register_offer(self, quantity, price)
        
    def close_bond(self, idx):
        self.model.bond_ledger.close(idx)
        
    def close_self_owned_bonds(self):
        idxs = self.bonds.self_owned_ids()
        for i in idxs:
            self.bonds.close(i)
    
    def get_all_issued_bonds(self, except_counterparties=[]):
        return self.model.bond_ledger.df.iloc[np.where((self.model.bond_ledger.df.issuer == self)&(~self.model.bond_ledger.df.holder.isin(except_counterparties)))[0]]
    
    def _bond_liabilities(self, except_counterparties=[]):
        all_bonds = self.get_all_issued_bonds(except_counterparties=except_counterparties)
        return ('bonds', all_bonds.iloc[np.where(all_bonds['holder']!=self)[0]].mark_to_market_value.sum())
        # return ('bonds', all_bonds.iloc[np.where(all_bonds['holder']!=self)[0]].hold_to_maturity_value.sum())
 
#%%

class BondHolder:     
    __slots__ = ()
    
    
    def __init__(self):
        self.asset_keys = self.asset_keys + ['_bond_assets']
    
    def buy_bond(self, seller, price, idx):
        seller.sell_bond(self, price, idx)
    
    def sell_bond(self, buyer, price, idx):
        buyer.pay(self.deposit_account_number, price)
        self.model.bond_ledger.transfer(idx,buyer)
    
    def get_all_held_bonds(self, except_counterparties=[]):
        return self.model.bond_ledger.df.iloc[np.where((self.model.bond_ledger.df.holder == self)&(~self.model.bond_ledger.df.issuer.isin(except_counterparties)))[0]]
    
    def _bond_assets(self, except_counterparties=[]):        
        all_bonds = self.get_all_held_bonds(except_counterparties=except_counterparties)
        return ('bonds', all_bonds.iloc[np.where(all_bonds['issuer']!=self)[0]].mark_to_market_value.sum())
        # return ('bonds', all_bonds.iloc[np.where(all_bonds['issuer']!=self)[0]].hold_to_maturity_value.sum())
    
#%%

class StockIssuer:     
    __slots__ = ()
    
    def __init__(self):
        pass
   
#%%
  
class StockHolder:     
    __slots__ = ()
    
    def __init__(self):
        pass
 
#%%

class TaxAuthority:     
    __slots__ = ()
    
    def __init__(self):
        pass
  
#%%

class TaxPayer:     
    __slots__ = ()
    
    def __init__(self):
        pass













