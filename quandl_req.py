import Quandl
import requests as req
import numpy as np
from datetime import date, timedelta
import pdb

def _cleanNames(name):
    name = name.upper() #convert to uppercase
    name = name.replace(" ", "") #remove all whitespace
    return name


def getHistoricData(ticker, data_pt):

    '''
    Gets historic data from an input stock for the last dp-days
    '''
    curr = date.today()
    past = curr - timedelta(days = data_pt)

    #Craft the Quandl Request
    data = Quandl.get(('WIKI/' + ticker), authtoken='xxxxxxxxxxxxxx', trim_start=str(past),
    trim_end=str(curr), exclude_headers='true', returns='numpy', sort_order = 'desc')

    cleaned_rec = {item[0].date():item[4] for item in data} # {date: close price}
    return cleaned_rec   # returns the complete record of the stock

def getPerc(cur, prev):

    perc = round(100*((cur-prev)/prev),3)
    return perc


def getValdata(stock_list,data_pt):
    unif_dates = set() #unified list of all date data points
    data_struct = dict() # {ticker: {date:close, date:close}, ...}

    for stock in stock_list:
        hist_data = getHistoricData(stock, data_pt) #get the data for each stock in the list
        dates = set(hist_data.keys()) #get the dates

        if unif_dates:
            unif_dates = unif_dates.intersection(dates)
        else:
            unif_dates = unif_dates.union(dates)

        data_struct[stock] = hist_data #dictionary to store {ticker:{date:price,date:price}}

    #Clean up the complete data structure based on unified dates
    for stock in stock_list:
        dates = data_struct[stock].keys()
        mod = data_struct[stock]
        data_struct[stock] = {d:round(mod[d]*100) for d in dates if d in unif_dates}

    return [data_struct, unif_dates]

def buildCorr(data_struct):

    st_list = list(data_struct.keys())
    #Instantiate the correlation matrix
    corr_mat = np.zeros((len(st_list),len(st_list)))
    covar_mat = np.zeros((len(st_list),len(st_list)))

    for a in st_list:
        for b in st_list:

            a_tuples = list(data_struct[a].items())
            b_tuples = list(data_struct[b].items())

            a_tuples.sort(key=lambda x: x[0], reverse=True)
            b_tuples.sort(key=lambda y: y[0], reverse=True)

            a_pr = [pr for (date,pr) in a_tuples]
            b_pr = [pr for (date,pr) in b_tuples]


            a_dif = [getPerc(cur,prev) for cur, prev in zip(a_pr,a_pr[1:])]
            a_avg = sum(a_dif)/len(a_dif)

            b_dif = [getPerc(cur,prev) for cur, prev in zip(b_pr,b_pr[1:])]
            b_avg = sum(b_dif)/len(b_dif)

            if(len(a_dif)==len(b_dif)):
                sample = len(a_dif)
            else:
                print("CATASTROPHIC ERROR\n Somehow different sized data")

            covar = sum((x[0]-a_avg)*(x[1]-b_avg) for x in zip(a_dif,b_dif))/sample
            corr = covar/(np.std(a_dif)*np.std(b_dif))

            corr_mat[st_list.index(a),st_list.index(b)] = corr
            covar_mat[st_list.index(a),st_list.index(b)] = covar

    return corr_mat


if __name__ == '__main__':
    [data_struct, dates] = getValdata(['AAPL','GOOGL','MSFT'],1000)
    print("Got Data!\n")
    corr_mat = buildCorr(data_struct)
    print(corr_mat)
    print("Correlation matrix produced with: {0} data points".format(len(dates))
)
##########

