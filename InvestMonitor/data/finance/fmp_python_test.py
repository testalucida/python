from fmp_python.fmp import FMP

# fmp = FMP(output_format='json', write_to_file=False, api_key='554aa031d25c1457115803e9c2562cb8')  ODER
fmp = FMP(output_format='pandas', write_to_file=False, api_key='554aa031d25c1457115803e9c2562cb8')
# resp = fmp.get_quote('AAPL')
# resp2 = fmp.get_quote_short( 'AAPL' )
resp3 = fmp.get_historical_price( 'AAPL', '2025-01-01', '2025-02-10' )
print( resp3 )

