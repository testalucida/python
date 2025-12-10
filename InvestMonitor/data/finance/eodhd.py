import requests

def testDividend():
    url = f'http://eodhd.com/api/div/AAPL?from=2023-01-01&api_token=6224bfc9283350.13970601'
    data = requests.get(url)
    print(data)

def test1():
    url = f'https://eodhd.com/api/eod/LQDE.SW?api_token=6224bfc9283350.13970601&fmt=json'
    data = requests.get( url ).json()
    print( data )

def listofsupportedtickers():
    url = f'https://eodhd.com/api/exchange-symbol-list/US?api_token=6224bfc9283350.13970601&fmt=json'
    data = requests.get( url )
    print( data )

if __name__ == "__main__":
    test1()
    #testDividend()
    #listofsupportedtickers()