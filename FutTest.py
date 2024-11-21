from main2 import Backtest
from typing import List
from datetime import datetime , timedelta
from HelperInfra import get_target_date , last_friday_of_previous_month , last_thursday
import pandas as pd
import numpy as np

global_val=[]
class FutTest(Backtest):
    criteria_month:int=0
    def __init__(self, uid: str, stock_list: List[str], start_date: datetime, end_date: datetime, criteria_months: int,exposure:int,stock_number:int):
        # Initialize parent Backtest class
        super().__init__(uid, stock_list, start_date, end_date,exposure)
        self.criteria_month=criteria_months
        self.stock_number=stock_number

       
    def give_std_number(self,ticker,start_date,end_date):
        arr=[]
        prev_close=None
        data = self.stock_data[ticker]
        while start_date <= end_date:
            close=data[data['Date'] == pd.to_datetime(start_date)].iloc[-1:]['Close']
            if len(close)==0:
                start_date+=timedelta(days=1)
                continue
            if prev_close is None:
                prev_close=close.values[0]
            else:
                percentage_change = round(((close.values[0] - prev_close) / prev_close) * 100, 2)
                arr.append(percentage_change)
            prev_close=close.values[0]
            start_date+=timedelta(days=1)

        std_dev = np.std(np.array(arr))
        return std_dev

    def give_stock_criteria(self, criteria_months: int):
        arr = []
        previous_date = get_target_date(self.current_date, f'-{criteria_months}F', 2)
        print("Searching Stocks For ",self.current_date," ",previous_date)
        
        for stock in self.stock_data.keys():
            data = self.stock_data[stock]
            try:
                prev=data[data['Date'] >= pd.to_datetime(previous_date)].iloc[0:1]
                curr=data[data['Date'] >= pd.to_datetime(self.current_date)].iloc[0:1]
                previous_date_close = prev['Close'].values[0]
                current_date_close = curr['Close'].values[0]
                previous_date_2 = prev['Date'].values[0]
                current_date_2 = curr['Date'].values[0]
                
                if current_date_2-previous_date_2>60:
                    percentage_change = round((( current_date_close-previous_date_close) / previous_date_close ) * 100, 2)
                    std=self.give_std_number(stock,previous_date,self.current_date)
                    ratio=percentage_change/std
                    arr.append({
                        'Symbol': stock, 
                        'Previous Price':previous_date_close,
                        'Current Price':current_date_close,
                        'Previous Date':previous_date_2,
                        'Previous Check':previous_date,
                        'Current Date':current_date_2,
                        'Current Check':self.current_date,
                        'Change %':percentage_change,
                        'Std':std,
                        'Ratio':ratio,
                    })
                
               
            except IndexError:
                print(f"Missing data for stock: {stock}")
        top_30 = sorted(arr, key=lambda x: x['Ratio'], reverse=True)[:self.stock_number]
        for i in top_30:
            global_val.append(i)
        return top_30
    
    def give_trades_for_each_month(self,start_date,end_date,valid_stocks):
        
        while start_date <= end_date:
            
            last_month_friday=last_friday_of_previous_month(start_date.year, start_date.month)
            current_month_thursday=last_thursday(start_date.year, start_date.month)
            for stock in valid_stocks:
                data = self.stock_data[stock['Symbol']]
                thursday_close = data[data['Date'] <= pd.to_datetime(current_month_thursday)].iloc[-1:]['Close'].values[0]
                last_friday_open = data[data['Date'] <= pd.to_datetime(last_month_friday)].iloc[-1:]['Open'].values[0]
                lot=self.exposure/last_friday_open
                pnl=(thursday_close-last_friday_open)*lot
                self.trades.append({
                    'Symbol': stock['Symbol'],
                    'Entry Date': last_month_friday,
                    'Entry Price': last_friday_open,
                    'Exit Date': current_month_thursday,
                    'Exit Price': thursday_close,
                    'Lots': lot,
                    'PnL': pnl
                })
            start_date = get_target_date(start_date, '0L', 2) + timedelta(days=1)
        

    def __next__(self):
        """Move to the next date range."""
        if self.current_date > self.end_date:
            raise StopIteration
        selected_stocks=self.give_stock_criteria(self.criteria_month)
        # Get next date based on a 3-months offset
        end_date = get_target_date(self.current_date, self.Strat_Data.expiry, 2)
        print(self.current_date," ",end_date)
        self.give_trades_for_each_month(self.current_date,end_date,selected_stocks)
      
        
        # Update current_date for the next iteration
        self.current_date = end_date + timedelta(days=1)

        # Ensure we don't iterate past the end date
        if self.current_date > self.end_date:
            raise StopIteration

        return self.current_date  # Return current date for demonstration


# Example usage
if __name__ == "__main__":
    stock_list =  ['AARTIIND', 'ABAN', 'ABBOTINDIA', 'ABB', 'ABCAPITAL', 'ABFRL', 'ABGSHIP', 'ABIRLANUVO', 'ACC', 'ADANIENT', 'ADANIPORTS', 'ADANIPOWER', 'AIL', 'AJANTPHARM', 'ALBK', 'ALKEM', 'ALOKTEXT', 'AMARAJABAT', 'AMBUJACEM', 'AMTEKAUTO', 'ANDHRABANK', 'APIL', 'APLLTD', 'APOLLOHOSP', 'APOLLOTYRE', 'ARVIND', 'ASHOKLEY', 'ASIANPAINT', 'ASTRAL', 'ATUL', 'AUBANK', 'AUROPHARMA', 'AXISBANK', 'BAJAJFINSV', 'BAJAJHIND', 'BAJAJHLDNG', 'BAJAJ_AUTO', 'BAJFINANCE', 'BALKRISIND', 'BALRAMCHIN', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'BATAINDIA', 'BEL', 'BEML', 'BERGEPAINT', 'BFUTILITIE', 'BGRENERGY', 'BHARATFIN', 'BHARATFORG', 'BHARTIARTL', 'BHEL', 'BHUSANSTL', 'BIOCON', 'BOMDYEING', 'BOSCHLTD', 'BPCL', 'BRFL', 'BRITANNIA', 'BSOFT', 'CADILAHC', 'CAIRN', 'CANBK', 'CANFINHOME', 'CAPF', 'CASTROLIND', 'CEATLTD', 'CENTRALBK', 'CENTURYTEX', 'CESC', 'CGPOWER', 'CHAMBLFERT', 'CHENNPETRO', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'COFORGE', 'COLPAL', 'CONCOR', 'COREEDUTEC', 'COREPROTEC', 'COROMANDEL', 'CROMPGREAV', 'CROMPTON', 'CUB', 'CUMMINSIND', 'DABUR', 'DALBHARAT', 'DALMIABHA', 'DCBBANK', 'DCB', 'DCHL', 'DEEPAKNTR', 'DELTACORP', 'DENABANK', 'DHANBANK', 'DHFL', 'DISHTV', 'DIVISLAB', 'DIXON', 'DLF', 'DRREDDY', 'EDUCOMP', 'EICHERMOT', 'EKC', 'ENGINERSIN', 'EQUITAS', 'ESCORTS', 'ESSAROIL', 'EXIDEIND', 'FEDERALBNK', 'FINANTECH', 'FORTIS', 'FRL', 'FSL', 'GAIL', 'GESHIP', 'GITANJALI', 'GLAXO', 'GLENMARK', 'GMDCLTD', 'GMRINFRA', 'GNFC', 'GODFRYPHLP', 'GODREJCP', 'GODREJIND', 'GODREJPROP', 'GRANULES', 'GRASIM', 'GSFC', 'GSKCONS', 'GSPL', 'GTLINFRA', 'GTL', 'GTOFFSHORE', 'GUJFLUORO', 'GUJGASLTD', 'GVKPIL', 'HAL', 'HAVELLS', 'HCC', 'HCLTECH', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HDFC', 'HDIL', 'HEROHONDA', 'HEROMOTOCO', 'HEXAWARE', 'HINDALCO', 'HINDCOPPER', 'HINDOILEXP', 'HINDPETRO', 'HINDUNILVR', 'HINDZINC', 'HONAUT', 'HOTELEELA', 'IBREALEST', 'IBULHSGFIN', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'ICIL', 'IDBI', 'IDEA', 'IDFCBANK', 'IDFCFIRSTB', 'IDFC', 'IEX', 'IFCI', 'IGL', 'INDHOTEL', 'INDIACEM', 'INDIAINFO', 'INDIAMART', 'INDIANB', 'INDIGO', 'INDUSINDBK', 'INDUSTOWER', 'INFIBEAM', 'INFOSYSTCH', 'INFRATEL', 'INFY', 'INTELLECT', 'IOB', 'IOC', 'IPCALAB', 'IRB', 'IRCTC', 'ISPATIND', 'ITC', 'IVRCLINFRA', 'JETAIRWAYS', 'JINDALSAW', 'JINDALSTEL', 'JINDALSWHL', 'JISLJALEQS', 'JKCEMENT', 'JPASSOCIAT', 'JPPOWER', 'JSWENERGY', 'JSWISPAT', 'JSWSTEEL', 'JUBLFOOD', 'JUSTDIAL', 'KAJARIACER', 'KFA', 'KOTAKBANK', 'KPIT', 'KSCL', 'KSOILS', 'KTKBANK', 'LALPATHLAB', 'LAURUSLABS', 'LICHSGFIN', 'LITL', 'LTIM', 'LTI', 'LTTS', 'LT', 'LUPIN', 'MANAPPURAM', 'MARICO', 'MARUTI', 'MAX', 'MCLEODRUSS', 'MCX', 'MERCATOR', 'METROPOLIS', 'MFSL', 'MGL', 'MINDTREE', 'MLL', 'MOSERBAER', 'MOTHERSON', 'MOTHERSUMI', 'MPHASIS', 'MRF', 'MRPL', 'MTNL', 'MUTHOOTFIN', 'NAGARCONST', 'NAGARFERT', 'NAGAROIL', 'NATIONALUM', 'NAUKRI', 'NAVINFLUOR', 'NBCC', 'NCC', 'NESTLEIND', 'NEYVELILIG', 'NHPC', 'NIITTECH', 'NMDC', 'NTPC', 'OBEROIRLTY', 'OFSS', 'OIL', 'ONGC', 'ONMOBILE', 'OPTOCIRCUI', 'ORBITCORP', 'ORCHIDCHEM', 'ORIENTBANK', 'PAGEIND', 'PANTALOONR', 'PATELENG', 'PATNI', 'PCJEWELLER', 'PEL', 'PERSISTENT', 'PETRONET', 'PFC', 'PFIZER', 'PIDILITIND', 'PIIND', 'PIRHEALTH', 'PNB', 'POLARIS', 'POLYCAB', 'POWERGRID', 'PRAJIND', 'PTC', 'PUNJLLOYD', 'PVR', 'RAIN', 'RAMCOCEM', 'RANBAXY', 'RAYMOND', 'RBLBANK', 'RCOM', 'RDEL', 'RECLTD', 'RELCAPITAL', 'RELIANCE', 'RELINFRA', 'RELMEDIA', 'RENUKA', 'REPCOHOME', 'RNAVAL', 'ROLTA', 'RPOWER', 'RUCHISOYA', 'SAIL', 'SBICARD', 'SBILIFE', 'SBIN', 'SCI', 'SHREECEM', 'SHRIRAMFIN', 'SIEMENS', 'SINTEX', 'SKSMICRO', 'SKUMARSYNF', 'SOBHA', 'SOUTHBANK', 'SREINFRA', 'SRF', 'SRTRANSFIN', 'SSLT', 'STAR', 'STERLINBIO', 'STER', 'STRTECH', 'SUNPHARMA', 'SUNTV', 'SUZLON', 'SYNDIBANK', 'SYNGENE', 'TATACHEM', 'TATACOFFEE', 'TATACOMM', 'TATACONSUM', 'TATAELXSI', 'TATAGLOBAL', 'TATAMOTORS', 'TATAMTRDVR', 'TATAPOWER', 'TATASTEEL', 'TCS', 'TECHM', 'TH_IINFOTECH', 'TITAN', 'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'TRIVENI', 'TTKPRESTIG', 'TTML', 'TULIP', 'TVSMOTOR', 'TV_ETBRDCST', 'TV_ET', 'UBL', 'UCOBANK', 'UJJIVAN', 'ULTRACEMCO', 'UNIONBANK', 'UNIPHOS', 'UNITECH', 'UPL', 'VEDL', 'VGUARD', 'VIDEOIND', 'VIJAYABANK', 'VIPIND', 'VOLTAS', 'WELCORP', 'WHIRLPOOL', 'WIPRO', 'WOCKPHARMA', 'YESBANK', 'ZEEL', 'ZYDUSLIFE']


    criteria_month = 5
    obj={
        "symbol_list": stock_list,
        "expiry": "2L",
        "session": "M",
    }
    stock_number=30
    exposure=700000

    # Create an instance of FutTest
    a = FutTest(obj, stock_list, datetime(2019, 6, 1), datetime(2024, 1, 1), criteria_month,exposure,stock_number)


    #Iterate through the dates
    try:
        while True:
            current = next(a)
            print(f"Processed for date: {current}")
    except StopIteration:
        print("Iteration complete.")


    print(a.trades)
    df=pd.DataFrame(a.trades)
    # Converting Exit Date to datetime format
    df["Exit Date"] = pd.to_datetime(df["Exit Date"], format="%d-%m-%Y")

    # Extracting Month and Year
    df["Month"] = df["Exit Date"].dt.month
    df["Year"] = df["Exit Date"].dt.year

    # Calculating Monthly and Yearly PnL
    monthly_pnl = df.groupby(["Year", "Month"])["PnL"].sum().reset_index()
    yearly_pnl = df.groupby("Year")["PnL"].sum().reset_index()

    #Saving all data to an Excel file with separate sheets
    file_path = "./future_trades_analysis 30 days 376 Stocks Select 15.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name="All Trades", index=False)
        monthly_pnl.to_excel(writer, sheet_name="Monthly PnL", index=False)
        yearly_pnl.to_excel(writer, sheet_name="Yearly PnL", index=False)

    file_path


dfglobal=pd.DataFrame(global_val)
dfglobal.to_csv('global_val_15_Stocks_Out_of_376_stocks.csv', index=False)
