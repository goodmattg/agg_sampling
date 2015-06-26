import quandl_req as qr
from setup import getTickers

tickers = getTickers()

user_stocks = input("Enter a comma separated list of tickers: ")
user_stocks = user_stocks.split(",") #Convert input to list

user_stocks = [qr._cleanNames(item) for item in user_stocks] #clean up the input

user_stocks = [st for st in user_stocks if (st in tickers)] #Get all valid tickers from input stocks

valid_dates = qr.buildCorrelation(user_stocks,20)

print(valid_dates)

#print("\n")
#print("What sector would you like to visualize today?")
#print("To see a list of sectors, type 'LIST'")

