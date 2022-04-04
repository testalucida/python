# see: https://readthedocs.org/projects/python-fints/downloads/pdf/latest/

import logging
from datetime import date
import getpass
from fints.client import FinTS3PinTanClient
from fints.utils import minimal_interactive_cli_bootstrap


def test_consors():
    """
    Ausprobieren, was man von Consors ermitteln kann
    :return:
    """
    #logging.basicConfig(level=logging.DEBUG)
    try:
        f = FinTS3PinTanClient( '76030080', # Your bank's BLZ
                            '970715353', # Your login name
                            getpass.getpass('PIN:'), # Your banking PIN
                            "https://brokerage-hbci.consorsbank.de/hbci",
                            #'https://hbci-pintan.gad.de/cgi-bin/hbciservlet',
                            product_id=None )
        print( f )
    except Exception as ex:
        print( str( ex ) )

    #minimal_interactive_cli_bootstrap( f )

    #with f:
    # Since PSD2, a TAN might be needed for dialog initialization. Let's check if there is one required
    if f.init_tan_response:
        print( "A TAN is required", f.init_tan_response.challenge )
        tan = input( 'Please enter TAN:' )
        f.send_tan( f.init_tan_response, tan )


        # Fetch accounts
    accounts = f.get_sepa_accounts()
    print( accounts )