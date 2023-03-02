from argparse import ArgumentParser
from src.base import configure_logger_and_queue,\
    handle_SERPENT_config
from src.back_end import SERPENT
import os,\
    sys
from logging import getLogger
from traceback import format_exc

class CLI_helper():

    def __init__(self):
        self.config_SERPENT = handle_SERPENT_config()

    def return_configured_coins(self):
        return [entry[0] for entry in self.config_SERPENT.items()]

    def check_valid_coin(self,
                         coin):
        if coin not in [entry[0] for entry in self.config_SERPENT.items()]:
            return False
        return True

parser = ArgumentParser(description='CLI: SERPENT |'
                                    ' ' + open(os.path.join(os.path.dirname(__file__),'version.txt'), 'r').read())

parser.add_argument('-c',
                    '--coin',
                    type=str,
                    help='Coin (asset) to be processed, Can be one of the following: {}'.format('|'.join(coin for coin in CLI_helper().return_configured_coins())))

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

parser.add_argument('--farmerSK', dest='farmerSK', action='store_true')
parser.set_defaults(farmerSK=False)

def main():

    configure_logger_and_queue()

    _log = getLogger()

    args = parser.parse_args()

    SERPENTobj = CLI_helper()

    if not SERPENTobj.check_valid_coin(coin=args.coin):
        sys.exit('Your coin is not in the config: {}'.format(args.coin))

    if not args.mnemonic:
        sys.exit('You need a mnemonic to sign the transaction !')

    if not args.sendToAddr:
        sys.exit('Where should I send the funds ? Please provide a send to address !')

    if not args.amount:
        sys.exit('How much shall I send ? Please provide an amount !')

    try:
        print(args.mnemonic)
        snake = SERPENT(asset=args.coin,
                       mnemonic=args.mnemonic,
                       send_to_address=args.sendToAddr,
                       amount_to_transfer=args.amount,
                       fee = args.fees,
                       use_farmer_sk = args.farmerSK
                       )
        snake.create_unsigned_transaction()
        snake.sign_tx()
        snake.push_tx()
    except:
        _log.error(f"Failed to execute SERPENT:\n{format_exc(chain=False)}")

if __name__ == '__main__':
    main()