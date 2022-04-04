import yfinance, json

def test1():
    # siehe https://ingo-janssen.de/aktienkurse-abfragen-mit-python-schritt-fuer-schritt/
    # Ticker zu Firma, Ticker zu ISIN finden: https://finance.yahoo.com
    #t = yfinance.Ticker( "MSF.DE" )
    #t = yfinance.Ticker( "EUSRI.PA" )
    t = yfinance.Ticker( "LU0831568729.SG" )
    print( t.info["regularMarketPrice"], " ", t.info["currency"] )
    print( "------------------------------" )
    print( t.history( period='1d', interval='1d' ) )
    print( "-------------------------------" )
    hist = t.history( period='1d', interval='1d' )
    print( "Close: ", hist["Close"] )
    print( hist )
    #print( json.dumps( t.history, indent=4 ) )
    #print( json.dumps( t.info, indent=4 ) )