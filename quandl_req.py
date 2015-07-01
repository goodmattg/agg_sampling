import Quandl
import numpy as np
from datetime import date, timedelta
import pdb


def _cleanNames(name):
    name = name.upper()  # convert to uppercase
    name = name.replace(" ", "")  # remove all whitespace
    return name


def getHistoricData(ticker, data_pt):
    curr = date.today()
    past = curr - timedelta(days=data_pt)

    # Craft the Quandl Request
    data = Quandl.get(('WIKI/' + ticker),
                      authtoken='xxxxxxxxxxxxxx',
                      trim_start=str(past),
                      trim_end=str(curr),
                      exclude_headers='true',
                      returns='numpy',
                      sort_order='desc')
    # {date: close price}
    cleaned_rec = {item[0].date(): item[4] for item in data}

    return cleaned_rec   # returns the complete record of the stock


def getPerc(cur, prev):
    perc = round(100*((cur-prev)/prev), 3)
    return perc


def getValdata(stock_list, data_pt):
    unif_dates = set()  # unified list of all date data points
    data_struct = dict()  # {ticker: {date:close, date:close}, ...}

    for stock in stock_list:
        # get the data for each stock in the list
        hist_data = getHistoricData(stock, data_pt)
        # get the dates
        dates = set(hist_data.keys())

        if unif_dates:
            unif_dates = unif_dates.intersection(dates)
        else:
            unif_dates = unif_dates.union(dates)
        # dictionary to store {ticker:{date:price,date:price}}
        data_struct[stock] = hist_data

    # Clean up the complete data structure based on unified dates
    for stock in stock_list:
        dates = data_struct[stock].keys()
        mod = data_struct[stock]
        data_struct[stock] = {d: round(mod[d]*100)
                              for d in dates if d in unif_dates}

    return [data_struct, unif_dates]


def buildCorr(data_struct):

    st_list = list(data_struct.keys())  # stock list
    all_data = dict()

    # Instantiate the correlation and covariance matrix
    corr_mat = np.zeros((len(st_list), len(st_list)))
    covar_mat = np.zeros((len(st_list), len(st_list)))

    for st in st_list:
        # List of date:price tuples stock st
        st_tuples = list(data_struct[st].items())
        # Most recent dates first
        st_tuples.sort(key=lambda x: x[0], reverse=True)
        # List of prices for "st"
        st_pr = [pr for (date, pr) in st_tuples]
        # Close percentages of "st"
        st_dif = [getPerc(cur, prev) for cur, prev in zip(st_pr, st_pr[1:])]
        # Average close percentage of "st"
        st_avg = sum(st_dif)/len(st_dif)
        # Add to storage dict
        all_data[st] = (st_dif, st_avg, st_pr)

    for a in st_list:
        for b in st_list:

            a_dif, a_avg, _ = all_data[a]
            b_dif, b_avg, _ = all_data[b]

            if(len(a_dif) == len(b_dif)):
                num_samples = len(a_dif)
            else:
                print("CATASTROPHIC ERROR\n Somehow different sized data")

            # Calculate covariance and correlation
            covar = sum((x[0]-a_avg)*(x[1]-b_avg)
                        for x in zip(a_dif, b_dif))/num_samples

            corr = covar/(np.std(a_dif)*np.std(b_dif))

            # Insert values into matrices
            corr_mat[st_list.index(a), st_list.index(b)] = corr
            covar_mat[st_list.index(a), st_list.index(b)] = covar

    return corr_mat, covar_mat


if __name__ == '__main__':
    [data_struct, dates] = getValdata(['AAPL', 'GOOGL', 'MSFT'], 100)
    print("Got Data!\n")
    corr_mat, covar_mat = buildCorr(data_struct)
    print(covar_mat)
    print("Covariance matrix built with: {0} data points".format(len(dates)))
    print(corr_mat)
    print("Correlation matrix built with: {0} data points".format(len(dates)))
