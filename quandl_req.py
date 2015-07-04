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
    date_close = {item[0].date(): item[4] for item in data}
    return date_close   # returns the complete record of the stock


def getPerc(cur, prev):
    perc = 100*round(((cur-prev)/prev), 6)
    return perc


def getValdata(stock_list, data_pt):

    '''
    Returns
    '''

    unif_dates = set()  # unified list of all date data points
    data_struct = dict()  # {ticker: {date:close, date:close}, ...}

    for st in stock_list:
        hist_data = getHistoricData(st, data_pt)  # get date:price data
        dates = set(hist_data.keys())  # current stock list of dates

        if unif_dates:  # reconcile with universal list of dates
            unif_dates = unif_dates.intersection(dates)
        else:
            unif_dates = unif_dates.union(dates)

        data_struct[st] = hist_data  # {tick:{date:price,date:price}, ...}

    dat_table = np.zeros((len(unif_dates), len(stock_list)))
    unif_dates = sorted(unif_dates, reverse=True)

    # Clean up the complete data structure based on unified dates
    # Create a storage matrix
    for st in stock_list:
        dates = sorted(data_struct[st].keys(), reverse=True)
        dates = sorted([d for d in dates if d in unif_dates], reverse=True)
        data_struct[st] = {d: data_struct[st][d]*100 for d in dates}
        for d in dates:
            ind_d = dates.index(d)
            ind_st = stock_list.index(st)
            dat_table[ind_d, ind_st] = data_struct[st][d]

    return [data_struct, unif_dates, dat_table, stock_list]


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

    # Signal is most recent set of price differences
    signal = dict()
    for k, v in all_data.items():
        signal[k] = v[0][0]

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

    return corr_mat, covar_mat, signal


if __name__ == '__main__':
    [dt_struct, dates, dt_table, st_list] = getValdata(['AAPL', 'MYE'], 10)

    corr_mat, covar_mat, signal = buildCorr(dt_struct)

    print(covar_mat)
    print("Covariance matrix built with: {0} data points".format(len(dates)))
    print(corr_mat)
    print("Correlation matrix built with: {0} data points".format(len(dates)))
