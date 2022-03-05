from argparse import ArgumentParser
from asyncio import run
from logging import getLogger
from _00_base import configure_logger_and_queue
from _00_back_end import SERPENT_back_end
import os,\
    sys

class SERPENTcli(configure_logger_and_queue,
                SERPENT_back_end):

    def __init__(self):
        super(SERPENTcli, self).__init__()

    def return_configured_coins(self):
        return [entry[0] for entry in self.config_SERPENT.items()]

    def check_valid_coin(self,
                         coin):
        if coin not in [entry[0] for entry in self.config_SERPENT.items()]:
            return False
        return True

parser = ArgumentParser(description='CLI: WILLOW-chia-forks-offline-wallet-balance |'
                                    ' ' + open(os.path.join(os.path.dirname(__file__),'version.txt'), 'r').read())

parser.add_argument('-c',
                    '--coin',
                    type=str,
                    help='Coin (asset) to be processed, Can be one of the following: {}'.format('|'.join(coin for coin in SERPENTcli().return_configured_coins())))

parser.add_argument('-m',
                    '--mnemonic',
                    type=str,
                    help='The mnemonic to be used to generate the addresses.',
                    default = None)

parser.add_argument('-s',
                    '--sendToAddr',
                    help='The addresses to send the funds to.',
                    default=None)

parser.add_argument('-a',
                    '--amount',
                    type=float,
                    help='The amount to send.',
                    default = 0)

parser.add_argument('-f',
                    '--fees',
                    type=float,
                    help='Fees to attach to the transaction.',
                    default = 0)

parser.add_argument('--logger', dest='logger', action='store_true')
parser.add_argument('--no-logger', dest='logger', action='store_false')
parser.add_argument('--farmerSK', dest='farmerSK', action='store_true')
parser.set_defaults(logger=True)
parser.set_defaults(farmerSK=False)

if __name__ == '__main__':

    os.system("color") # enable color in the console

    args = parser.parse_args()

    SERPENTobj = SERPENTcli()

    if not SERPENTobj.check_valid_coin(coin=args.coin):
        sys.exit('Your coin is not in the config: {}'.format(args.coin))

    if not args.mnemonic:
        sys.exit('You need a mnemonic to sign the transaction !')

    if not args.sendToAddr:
        sys.exit('Where should I send the funds ? Please provide a send to address !')

    if not args.amount:
        sys.exit('How much shall I send ? Please provide an amount !')

    message_payload = run(SERPENTobj.initiate_transfer(asset=args.coin,
                                                       mnemonic=args.mnemonic,
                                                       send_to_address=args.sendToAddr,
                                                       amount_to_send=args.amount,
                                                       fees_to_attach=args.fees,
                                                       use_farmer_sk=args.farmerSK))

    if not args.logger:
        print('$${}$$'.format(str(message_payload)))
    else:
        log = getLogger()
        for message in message_payload:
            # getattr seems to fail here ...
            if message[0] == 'info':
                log.info(message[1])
            elif message[0] == 'error':
                log.error(message[1])
            else:
                log.info(message[1])
