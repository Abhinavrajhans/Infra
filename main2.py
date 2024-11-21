from pydantic import BaseModel
from typing import Optional , List
import pandas as pd
from datetime import datetime
from HelperInfra import calculate_historical_volatility


class Strategy(BaseModel):
    symbol_list:List[str]=[]
    expiry:str=""
    dte:Optional[int]=0
    is_hedge:Optional[bool]=False
    hedge_underlying:Optional[str]=""
    option_Type:Optional[str]=""
    sl:Optional[int]=0
    hedge_option_type:Optional[str]=""
    session:Optional[str]="M"
    trades:Optional[List[dict]]=[]
    

class Backtest:
    Strat_Data:Strategy
    stock_data:dict={}
    future_data:dict={}
    options_data:dict={}
    current_position={}
    trades=[]
    start_date:datetime=""
    end_date:datetime=""
    current_date:datetime=""
    exposure:int=0


    def __init__(self, uid,stock_list,start_date,end_date,exposure):
        self.load_stock_data(stock_list)
        self.load_future_data(stock_list)
    
        self.Strat_Data=Strategy(**uid)
        self.start_date=start_date
        self.end_date=end_date
        self.current_date=start_date
        self.exposure=exposure

    def give_stock_criteria(self,**args):
        pass
    

    def __next__(self):
        pass

    

    def load_stock_data(self, stock_list):
        for stock in stock_list:
            df = pd.read_csv(f"./Stocks Data/{stock}_EQ_EOD.csv")
            df = df.rename(columns={
                "EQ_Open": "Open",
                "EQ_High": "High",
                "EQ_Low": "Low",
                "EQ_Close": "Close",
                "EQ_Volume": "Volume"
            })
            result =calculate_historical_volatility(df)
            df['Volatility'] = result['volatility']
            df['Date'] = pd.to_datetime(df['Date'])
            self.stock_data[stock] = df


    def load_options_data(self,stock_list):
        for stock in stock_list:
            self.options_data[stock]=pd.read_csv(f"./Stocks Data/{stock}_Opt_EOD.csv")

    def load_future_data(self,stock_list):
        fut_data=pd.read_csv('./Fut_Stock_Continously.csv')
        for stock in stock_list:
            self.future_data[stock]=fut_data[fut_data['Ticker_Short']==stock]





        
        





        
