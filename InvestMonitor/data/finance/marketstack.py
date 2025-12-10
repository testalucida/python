import ast
import json
from typing import Dict, List

import requests

def testSearch():
    url = "http://api.marketstack.com/v1/tickers?access_key=370166fdb51e99c48ce83fd03691f180&search=BMW"
    response = requests.get( url )
    print( "done." )
    """
    { "pagination": { "limit": 100, "offset": 0, "count": 8, "total": 8 }, "data": [
        { "name": "BMW", "symbol": "BMW.XMIL", "has_intraday": false, "has_eod": true, "country": null,
          "stock_exchange": { "name": "Borsa Italiana", "acronym": "MIL", "mic": "XMIL", "country": "Italy",
                              "country_code": "IT", "city": "Milano", "website": "www.borsaitaliana.it" } },
        { "name": "BMW I", "symbol": "BMW.XSWX", "has_intraday": false, "has_eod": false, "country": null,
          "stock_exchange": { "name": "SIX Swiss Exchange", "acronym": "SIX", "mic": "XSWX", "country": "Switzerland",
                              "country_code": "CH", "city": "Zurich", "website": "www.six-swiss-exchange.com" } },
        { "name": "BAY.MOTOREN WERKE AG ST", "symbol": "BMW.XFRA", "has_intraday": false, "has_eod": true,
          "country": null,
          "stock_exchange": { "name": "Deutsche B\u00f6rse", "acronym": "FSX", "mic": "XFRA", "country": "Germany",
                              "country_code": "DE", "city": "Frankfurt", "website": "www.deutsche-boerse.com" } },
        { "name": "BAYERISCHE MOTOREN WERKE AG STAMMAKTIEN EO 1", "symbol": "BMW.XSTU", "has_intraday": false,
          "has_eod": true, "country": null,
          "stock_exchange": { "name": "B\u00f6rse Stuttgart", "acronym": "XSTU", "mic": "XSTU", "country": "Germany",
                              "country_code": "DE", "city": "Stuttgart", "website": "www.boerse-stuttgart.de" } },
        { "name": "BAY.MOTOREN WERKE AG ST", "symbol": "BMW.XETRA", "has_intraday": false, "has_eod": true,
          "country": null, "stock_exchange": { "name": "Deutsche B\u00f6rse Xetra", "acronym": "XETR", "mic": "XETRA",
                                               "country": "Germany", "country_code": "DE", "city": "Frankfurt",
                                               "website": "" } },
        { "name": "BMW INDUSTRIES LIMITED", "symbol": "BMW.XBOM", "has_intraday": false, "has_eod": true,
          "country": null,
          "stock_exchange": { "name": "Bombay Stock Exchange", "acronym": "MSE", "mic": "XBOM", "country": "India",
                              "country_code": "IN", "city": "Mumbai", "website": "www.bseindia.com" } },
        { "name": "BMWB", "symbol": "BMWB.XSTU", "has_intraday": false, "has_eod": true, "country": "Germany",
          "stock_exchange": { "name": "B\u00f6rse Stuttgart", "acronym": "XSTU", "mic": "XSTU", "country": "Germany",
                              "country_code": "DE", "city": "Stuttgart", "website": "www.boerse-stuttgart.de" } },
        { "name": "BMW Industries Ltd.", "symbol": "542669.XBOM", "has_intraday": false, "has_eod": true,
          "country": "India",
          "stock_exchange": { "name": "Bombay Stock Exchange", "acronym": "MSE", "mic": "XBOM", "country": "India",
                              "country_code": "IN", "city": "Mumbai", "website": "www.bseindia.com" } }] }
    """

def testEodData():
    url = "http://api.marketstack.com/v1/eod?access_key=370166fdb51e99c48ce83fd03691f180&symbols=BMW.XSWX&date_from=2024-01-10&date_to=2024-01-19"
    response = requests.get(url)
    print( "done.")

def testDividend():
    url = "https://api.marketstack.com/v2/tickers/IBTS.SW/dividends?access_key=370166fdb51e99c48ce83fd03691f180&date_from=2025-01-01&date_to=2025-10-31"
    response = requests.get( url )
    print( response.status_code )
    print( response.text )

def test2():
    url = "http://api.marketstack.com/v1/tickers?access_key=370166fdb51e99c48ce83fd03691f180"
    response = requests.get( url )
    print( "done." )

def test3():
    url = "http://api.marketstack.com/v1/eod?access_key=370166fdb51e99c48ce83fd03691f180&symbols=VDJP.L,ISPA.DE&date_from=2025-10-24&date_to=2025-10-24"
    response = requests.get( url )
    if response.status_code == 200:
        print( "done." )
    else:
        print( "failed: ", response.status_code)
        exit(1)
    f = open( "text.txt", "w" )
    f.write( response.text )
    f.close()
    print("")

def testAst():
    f = open( "text.txt", "r" )
    s = f.read()
    f.close()

    try:
        dic = json.loads( s )
        print( dic )
    except:
        dic = ast.literal_eval( s )
    print( dic )

if __name__ == "__main__":
    testDividend()
    # test3()
    # testAst()