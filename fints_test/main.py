
import logging
from datetime import date
import getpass
from fints.client import FinTS3PinTanClient
from fints.utils import minimal_interactive_cli_bootstrap

def test():
    logging.basicConfig(level=logging.DEBUG)
    f = FinTS3PinTanClient(
        #'BYLADEM1001',  # Your bank's BLZ
        '12030000',
        '15475833',  # Your login name
        getpass.getpass('PIN:'),  # Your banking PIN
        'https://banking-dkb.s-fints-pt-dkb.de/fints30'  #(Port 443) sagt https://www.dkb.de/DkbTransactionBanking/content/security/UserInfo/UserIdInfo.xhtml
        #'https://hbci-pintan.gad.de/cgi-bin/hbciservlet' #,
        #product_id='DC333D745719C4BD6A6F9DB6A'
        #product_id = '529900K16YGKC8BES892'
    )
    #accounts = f.get_sepa_accounts()  # or whatever
    #minimal_interactive_cli_bootstrap(f)

    with f:
        # Since PSD2, a TAN might be needed for dialog initialization. Let's check if there is one required
        if f.init_tan_response:
            print("A TAN is required", f.init_tan_response.challenge)
            tan = input('Please enter TAN:')
            f.send_tan(f.init_tan_response, tan)

        # Fetch accounts
        accounts = f.get_sepa_accounts()
        print( accounts )

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
