import pprint, pickle

def getTickers():

  file = open('csv_list.pkl', 'rb')
  csv_list = pickle.load(file)
  file.close()
  return (csv_list)

def getAuthToken():
  file = open('authtoken.pkl', 'rb')
  _authtoken = pickle.load(file)
  file.close()
  return (_authtoken)

  # tickers = np.genfromtxt('WIKI_tickers.csv', delimiter=' ',usecols=0,dtype=str, comments=',',skip_header=1)
