from urllib.request import urlopen
import certifi
import json

def my_urlopen( url ):
    response = urlopen( url, cafile=certifi.where() )
    data = response.read().decode( "utf-8" )
    d = json.loads( data )
    print( d )

def test1():
    #id = "LU1881477043.EUFUND"
    id = "DE0008478116"
    #id = "DWS" # Invest Enhanced Commodity Strategy LC"
    url = "https://eodhistoricaldata.com/api/search/" + id + "?api_token=6224bfc9283350.13970601"
    my_urlopen( url )

def test2():
    url = "https://eodhistoricaldata.com/financial-apis/search-api-for-stocks-etfs-mutual-funds-and-indices/"
    my_urlopen( url )
