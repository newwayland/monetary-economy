# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 14:52:07 2024

@author: andre
"""

import numpy as np
import pandas as pd

'''
Reserves
    Quantity offered
    Price offered
    Offering bank
    
    Quantity sought
    Price sought
    Seeking bank
    
Bonds
    Quantity offered
    Maturity date and coupon
    Offering party
    Price offered
    
    Quantity sought
    Maturity range
    Price sought
    Seeking party
    
Stocks

############

BASE MARKET CLASS

INTERBANK MARKET SUBCLASS
    MATCH NEXT HAS LOAN ISSUANCE
    
BOND MARKET SUBCLASS
    MATCH NEXT HAS BOND TRANSFER AND PAY
    QUANTITY MUST BE MULTIPLE OF 100 AND INDIVIDUAL BONDS IDENTIFIED
    
BOND EXCHANGE OBJECT FOR MANAGING EACH MARKET
    SIMILAR FUNCTIONS TO MARKET BUT ALLOW MATURITY AND COUPON TO BE SPECIFIED

'''


class Market:
    
    '''
    Quantity must be in second column as index 1 is referenced when clearing fulfilled transactions
    
    Market price is based on mean of last n transactions
        Should this be weighted by volume?
    '''
    
    def __init__(self, model, n_price_track=50, use_offered_price=True):   
        self.model             = model
        self.offering_df       = pd.DataFrame(columns = ['offerer', 'quantity', 'price'])
        self.seeking_df        = pd.DataFrame(columns = ['seeker',  'quantity', 'price'])
        self.offering_counter  = int(0) # for unique ID purposes, not indexing
        self.seeking_counter   = int(0) # for unique ID purposes, not indexing
        self.n_price_track     = n_price_track
        self.recent_prices     = np.full(n_price_track, np.nan)
        self.recent_quantities = np.full(n_price_track, np.nan)
        self.use_offered_price = use_offered_price
    
    @property
    def market_price(self):
        return np.nansum(self.recent_prices*(self.recent_quantities/np.nansum(self.recent_quantities)))
    
    def register_offer(self, seller, quantity, price):   
        data = {'offerer': seller, 'quantity': quantity, 'price': price}  
        self.offering_counter += 1    
        new_row = pd.DataFrame(data, index=[self.offering_counter])
        self.offering_df = pd.concat([self.offering_df, new_row], ignore_index=False, axis=0)  
        self.offering_df.sort_values('price', ascending=True, inplace=True)
    
    def register_interest(self, buyer, quantity, price):  
        data = {'seeker': buyer, 'quantity': quantity, 'price': price}  
        self.seeking_counter += 1    
        new_row = pd.DataFrame(data, index=[self.seeking_counter])
        self.seeking_df = pd.concat([self.seeking_df, new_row], ignore_index=False, axis=0)  
        self.seeking_df.sort_values('price', ascending=False, inplace=True)
        
    def match_next(self):
        status = False
        if (len(self.offering_df) > 0) & (len(self.seeking_df) > 0):
            if (self.offering_df.iloc[0]['price'] <= self.seeking_df.iloc[0]['price']):
                seeker = self.seeking_df.iloc[0]['seeker']
                offerer   = self.offering_df.iloc[0]['offerer']
                quantity = np.min([self.offering_df.iloc[0]['quantity'], self.seeking_df.iloc[0]['quantity']])
                price    = self.offering_df.iloc[0]['price'] if self.use_offered_price else self.seeking_df.iloc[0]['price']
                self.transact(offerer, seeker, quantity, price)
                
                self.offering_df.iat[0, 1]   -= quantity
                self.seeking_df.iat[0, 1] -= quantity
                self.remove_fulfilled()
                self.track_price(price, quantity)
                
                status = True
            
        return status
    
    def transact(self, offerer, seeker, quantity, price):
        # Define in subclass
        pass
            
    def remove_fulfilled(self):
        self.offering_df.drop(self.offering_df.index[np.where(self.offering_df['quantity']==0)[0]], inplace=True)
        self.seeking_df.drop(self.seeking_df.index[np.where(self.seeking_df['quantity']==0)[0]], inplace=True)
        
    def track_price(self, price, quantity):
        self.recent_prices = np.roll(self.recent_prices, 1)
        self.recent_prices[0] = price
        self.recent_quantities = np.roll(self.recent_quantities, 1)
        self.recent_quantities[0] = quantity
    
    def clear_market(self):
        market_active = True
        while market_active:
            market_active = self.match_next()
        return True
    
    def close_market(self):
        self.offering_df.drop(self.offering_df.index, inplace=True)
        self.seeking_df.drop(self.seeking_df.index, inplace=True)


class InterBankMarket(Market):    
    def transact(self, offerer, seeker, quantity, price):
        if offerer.has_lending_account_with_borrower(seeker) == False:
            offerer.open_lending_account(seeker)   
        print(f'EXTEND LOAN {quantity}')  
        print(f'#############################################################')
        offerer.grant_loan_to_borrower(seeker, quantity, price, maturity_days=1)
    

class BondMarket(Market):
    
    '''
    Quantity is the amount of money desiered to be invested
    Price is per 100 face value unit
    
    So if a 5% bond has 1 year left
        Hold to maturity = 100 + (5/2)*1 = 105
        If desired yield is 10% then price = 105 * (100-10)/100 = 94.5?
        
    C = coupon_rate * 100 / coupon frequency
    n = remaining coupons
    
    price = C * (1-((1+r)^-n)/r) + 100/(1+r)^n
    '''
    
    def __init__(self, model, maturity_date, coupon_rate, n_price_track=50, use_offered_price=True):    
        super().__init__(model, n_price_track=n_price_track, use_offered_price=use_offered_price)
        self.maturity_date = maturity_date
        self.coupon_rate   = coupon_rate
        
    def get_bond_indexes_by_holder(self, holder):
        holder_mask   = self.model.bond_ledger.df['holder'] == holder
        maturity_mask = self.model.bond_ledger.df['maturity_date'] == self.maturity_date
        coupon_mask   = self.model.bond_ledger.df['interest_rate'] == self.coupon_rate
        records       = self.model.bond_ledger.df.loc[holder_mask & maturity_mask & coupon_mask]
        return records
    
    def transact(self, offerer, seeker, quantity, price):        
        records = self.get_bond_indexes_by_holder(offerer)        
        n_bonds = int((quantity)//price)
        
        if len(records) < n_bonds:
            n_bonds = len(records)
            
        idxs = records.index[:(n_bonds)]
        
        for idx in idxs:
            offerer.sell_bond(seeker, price, idx)
        
class BondExchange:
    
    # @staticmethod
    # def yield_to_price(desired_yield, coupon_rate, remaining_coupon_payments, bond_face_value=100, coupon_frequency=2):  #
    #     '''
    #     yield is in percentage points
    #     coupon is in percentage points
        
    #     Calculation is simplified version of Excel PRICE() function
    #     https://support.microsoft.com/en-us/office/price-function-3ea9deac-8dfa-436f-a7c8-17ea02c21b0a
    #     No consideration of days through coupon period is taken. Just the absolute remaining coupons are 
    #     considered, and no proportionate handling of the coupon/coupon period is made.
    #     '''
    #     desired_yield /= 100 # convert to decimal fraction
    #     coupon_rate /= 100   # convert to decimal fraction
    #     coupon_value = coupon_rate * bond_face_value / coupon_frequency
                
    #     # Formulation changed to ensure that the principal is only compunded annually but
    #     # the coupon compounds bi-annually with each payment.
    #     # years_to_maturity   = np.ceil(remaining_coupon_payments/coupon_frequency)
    #     years_to_maturity   = np.ceil(remaining_coupon_payments/coupon_frequency)
    #     principal_component = (bond_face_value*((1+(desired_yield))**(-years_to_maturity))) 
    #     # principal_component = (bond_face_value*((1+(desired_yield/coupon_frequency))**(-remaining_coupon_payments))) 
        
    #     # handle divide by 0 error for 0 target yield
    #     coupon_numerator   = (1-(1+(desired_yield/coupon_frequency))**(-remaining_coupon_payments))
    #     coupon_denominator = desired_yield/coupon_frequency
    #     coupon_component   = coupon_value*np.divide(coupon_numerator, coupon_denominator, out=np.zeros_like(coupon_numerator), where=coupon_denominator!=0)
        
    #     individual_bond_price = principal_component + coupon_component        
        
    #     return individual_bond_price
  
    @staticmethod
    def yield_to_price(settlement_date, maturity_date, desired_yield, coupon_rate, bond_face_value=100, 
                        coupon_frequency=2, days_in_year=252):  #
        '''
        yield is in percentage points
        coupon is in percentage points
        
        Calculation is simplified version of Excel PRICE() function
        https://support.microsoft.com/en-us/office/price-function-3ea9deac-8dfa-436f-a7c8-17ea02c21b0a
        No consideration of days through coupon period is taken. Just the absolute remaining coupons are 
        considered, and no proportionate handling of the coupon/coupon period is made.
        '''
        desired_yield = desired_yield/100 # convert to decimal fraction
        coupon_rate = coupon_rate/100   # convert to decimal fraction
        coupon_value = coupon_rate * bond_face_value / coupon_frequency
                
        # Formulation changed to ensure that the principal is only compunded annually but
        # the coupon compounds bi-annually with each payment.
        # years_to_maturity   = np.ceil(remaining_coupon_payments/coupon_frequency)
        years_to_maturity   = (maturity_date - settlement_date)/days_in_year
        principal_component = (bond_face_value*((1+(desired_yield))**(-years_to_maturity))) 
        # principal_component = (bond_face_value*((1+(desired_yield/coupon_frequency))**(-remaining_coupon_payments))) 
        
        
        # handle divide by 0 error for 0 target yield
        remaining_coupon_payments = np.ceil(years_to_maturity*coupon_frequency)
        coupon_numerator   = (1-(1+(desired_yield/coupon_frequency))**(-remaining_coupon_payments))
        coupon_denominator = desired_yield/coupon_frequency
        coupon_component   = coupon_value*np.divide(coupon_numerator, coupon_denominator, out=np.zeros_like(coupon_numerator), where=coupon_denominator!=0)
        
        individual_bond_price = principal_component + coupon_component        
        
        return individual_bond_price
    
    def price_to_yield(price, coupon_rate, remaining_coupon_payments, bond_face_value=100, coupon_frequency=2):
        pass
    
    def __init__(self, model):
        self.model = model
        self.markets = []
        
    def register_bond_issue(self, maturity_date, coupon_rate):
        if not self.market_exists(maturity_date, coupon_rate):
            self.markets.append(BondMarket(self.model, maturity_date, coupon_rate)) 
        return self.get_market(maturity_date, coupon_rate)
        
    def list_bond_issues(self):
        # add offered and sought prices?
        return np.array([[x.maturity_date, x.coupon_rate] for x in self.markets])

    def get_market(self, maturity_date, coupon_rate):
        boolean = [((x.maturity_date == maturity_date) & (x.coupon_rate == coupon_rate)) for x in self.markets]
        if np.any(boolean):
            return self.markets[np.where(boolean)[0][0]]
        else:
            return None
        
    def market_exists(self, maturity_date, coupon_rate):
        return False if self.get_market(maturity_date, coupon_rate) is None else True
    
    def __call__(self, maturity_date, coupon_rate):
        return self.get_market(maturity_date, coupon_rate)


