from typing import Dict
from urllib.request import urlopen
import certifi
import json

class XFund:
    def __init__( self ):
        self.ISIN = ""
        self.Name = ""
        self.Exchange = ""
        self.Currency = ""
        self.previousCloseDate = ""
        self.previousClose = 0.0

    def toString( self ) -> str:
        s = "ISIN: %s -- Name: %s -- Exchange: %s -- Currency: %s -- previousCloseDate: %s -- previousClose: %.2f" \
            % ( self.ISIN, self.Name, self.Exchange, self.Currency, self.previousCloseDate, self.previousClose )
        return s

def findBestExchange( diclist ):
    def convertToXFund( dic ):
        x = XFund()
        x.ISIN = dic["ISIN"]
        x.Name = dic["Name"]
        x.Exchange = dic["Exchange"]
        x.previousCloseDate = dic["previousCloseDate"]
        x.previousClose = dic["previousClose"]
        x.Currency = dic["Currency"]
        return x

    bestEx:Dict = None
    for dic in diclist:
        if dic["Currency"] == "EUR":  # statt EUR die in der DB gespeicherte Währung einsetzen
            bestEx = dic # vorläufig
            if dic["Exchange"] == "XETRA":
                return convertToXFund( bestEx )
    return convertToXFund( bestEx )

def my_urlopen( url ):
    response = urlopen( url, cafile=certifi.where() )
    data = response.read().decode( "utf-8" )
    diclist = json.loads( data )
    #print( diclist )
    bestXFund = findBestExchange( diclist )
    print( bestXFund.toString() )


def test1():
    #id = "LU1881477043.EUFUND"
    #id = "DE0008478116"
    #id = "DE000A0F5UH1"
    id = "IE00B4X9L533"
    #id = "DWS" # Invest Enhanced Commodity Strategy LC"
    url = "https://eodhistoricaldata.com/api/search/" + id + "?api_token=6224bfc9283350.13970601"
    my_urlopen( url )

def test2():
    url = "https://eodhistoricaldata.com/financial-apis/search-api-for-stocks-etfs-mutual-funds-and-indices/"
    my_urlopen( url )
