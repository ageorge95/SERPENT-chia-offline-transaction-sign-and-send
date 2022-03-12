from logging import basicConfig,\
    INFO, DEBUG, WARNING, ERROR, CRITICAL,\
    Formatter,\
    StreamHandler, FileHandler, Handler,\
    getLogger
from sys import stdout
from queue import Queue
from os import path as os_path

def configure_logger():
    class CustomFormatter(Formatter):
        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format = '%(asctime)s,%(msecs)d %(levelname)-4s [%(filename)s:%(lineno)d -> %(name)s - %(funcName)s] ___ %(message)s'

        FORMATS = {
            DEBUG: grey + format + reset,
            INFO: grey + format + reset,
            WARNING: yellow + format + reset,
            ERROR: red + format + reset,
            CRITICAL: bold_red + format + reset
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = Formatter(log_fmt)
            return formatter.format(record)

    ch = StreamHandler(stream=stdout)
    ch.setLevel(DEBUG)
    ch.setFormatter(CustomFormatter())
    fh = FileHandler("runtime_log.log")
    fh.setLevel(DEBUG)
    fh.setFormatter(Formatter('%(asctime)s,%(msecs)d %(levelname)-4s [%(filename)s:%(lineno)d -> %(name)s - %(funcName)s] ___ %(message)s'))

    basicConfig(datefmt='%Y-%m-%d:%H:%M:%S',
                level=DEBUG,
                handlers=[
                    fh,
                    ch
                ])

class QueueHandler(Handler):
    """Class to send logging records to a queue
    It can be used from different threads
    The ConsoleUi class polls this queue to display records in a ScrolledText widget
    """
    # Example from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    # (https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe!
    # See https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

class configure_logger_and_queue():
    def __init__(self):

        super(configure_logger_and_queue, self).__init__()

        configure_logger()

        self._log = getLogger()

        # Create a logging handler using a queue
        self.log_queue = Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = Formatter('%(asctime)s %(levelname)-4s %(message)s')
        self.queue_handler.setFormatter(formatter)
        self._log.addHandler(self.queue_handler)

initial_config = {'XJK': {'root': '{userdir}\\.joker\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 100000000,
                         'friendly_name': 'joker',
                         'AGG_SIG_ME_ADDITIONAL_DATA': 'e361525c6797d147dcee1de0363ccd465ea11f92c6606f23dfb561456d746586'},
                  'GL': {'root': '{userdir}\\.gold\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'gold',
                         'AGG_SIG_ME_ADDITIONAL_DATA': 'ecbf4458b47e39c60afec66e245fccb042871417ffc5200cb0140346c2e044d0'},
                  'BPX': {'root': '{userdir}\\.bpx\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'bpx',
                         'AGG_SIG_ME_ADDITIONAL_DATA': 'ac43cd6665c8c034621a22243e0c9b14d5441e6cd987f23a5201fb24537183d6'},
                  'AEC': {'root': '{userdir}\\.aedge\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'aedge',
                         'AGG_SIG_ME_ADDITIONAL_DATA': '18825eb33dda33a5ee862a5add9d83c55471312d10866ebe08550a6f401c21dd'},
                 'APPLE': {'root': '{userdir}\\.apple\\mainnet'.format(userdir=os_path.expanduser("~")),
                           'denominator': 1000000000000,
                           'friendly_name': 'apple',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '7e35d673f1ee96ca5993034cd5a7b1cd7cba51826a99287e9f51e6962c3b7a68'},
                 'AVO': {'root': '{userdir}\\.avocado\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'avocado',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '973ddbed6ba5f961c6fac579046afdc54cada260f14652a2f3fd643f60086e1d'},
                 'CAC': {'root': '{userdir}\\.cactus\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'cactus',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '55830f14be472f67c4fc19825ac22ae785204c539bb43169d5ff47a9c7b2ae2a'},
                 'CANS': {'root': '{userdir}\\.cannabis\\mainnet'.format(userdir=os_path.expanduser("~")),
                          'denominator': 1000000000000,
                          'friendly_name': 'cannabis',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '5f96ac6cf90d112d755ee36ddef2a047917a4ecbe098c600e383cddfc34ed01a'},
                 'CGN': {'root': '{userdir}\\.chaingreen\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'chaingreen',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '0235e47be80dbba72e8e105f87776fe16690838dde7f71e8a77086c0374bcaf3'},
                 'COV': {'root': '{userdir}\\.covid\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'covid',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '11d8513356cee3cd17832ecfcb3ad6a3cea24971f6b6f9699e0dfa1e090a8cf0'},
                 'GDOG': {'root': '{userdir}\\.greendoge\\mainnet'.format(userdir=os_path.expanduser("~")),
                          'denominator': 1000000000000,
                          'friendly_name': 'greendoge',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'eb92c7d03986dc221ba5032cf9664f896666012b8b78bc8909089b30938862dd'},
                 'HDD': {'root': '{userdir}\\.hddcoin\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'hddcoin',
                         'AGG_SIG_ME_ADDITIONAL_DATA': '49f4afb189342858dba5c1bb6b50b0deaa706088474f0c5431d65b857d54ddb5'},
                 'LCH': {'root': '{userdir}\\.lotus\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'lotus',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'MELON': {'root': '{userdir}\\.melon\\mainnet'.format(userdir=os_path.expanduser("~")),
                           'denominator': 1000000000,
                           'friendly_name': 'melon',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'c093d9d15164df3859abb049136f84456ece91d373dd3ca4e1cd1595632763f1'},
                 'MGA': {'root': '{userdir}\\.mogua\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'mogua',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'c9c3ba2d62e4358c204fc513092f0c020117f0a360c11b11496df75fed2adf4c'},
                 'NCH': {'root': '{userdir}\\.chia\\ext9'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'n-chain_ext9',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'OZT': {'root': '{userdir}\\.goldcoin\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'Goldcoin',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '02f7d5a0399c86fa61fd560fd380b7f8911ed8fdfa3511ea00110346376189c3'},
                 'PEA': {'root': '{userdir}\\.peas\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'peas',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'd7e422a7ffafe4a0d5ea22e0922ab0493df0ff782bd8d4c01808649248b4cde1'},
                 'PIPS': {'root': '{userdir}\\.pipscoin\\mainnet'.format(userdir=os_path.expanduser("~")),
                          'denominator': 1000000000000,
                          'friendly_name': 'Pipscoin',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ee8b944de335e63d5e4f301e5dec0c8e0d6f227007deb4ba47be7e0ae353437a'},
                 'ROLLS': {'root': '{userdir}\\.rolls\\mainnet'.format(userdir=os_path.expanduser("~")),
                           'denominator': 1000000000000,
                           'friendly_name': 'rolls',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '37989cc5d5b2f0979399ffe0d0b8192cb5969ce9bb74fa5a0c6140d33c36f17a'},
                 'SCM': {'root': '{userdir}\\.scam\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'Scamcoin',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '11d8513356cee3cd17832ecfcb3ad6a3cea24971f6b6f9699e0dfa1e090a8cf0'},
                 'SIT': {'root': '{userdir}\\.sit\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'silicoin',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ecbf4458b47e39c60afec66e245fccb042871417ffc5200cb0140346c2e044d0'},
                 'SIX': {'root': '{userdir}\\.lucky\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'lucky',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'SOCK': {'root': '{userdir}\\.socks\\mainnet'.format(userdir=os_path.expanduser("~")),
                          'denominator': 1000000000000,
                          'friendly_name': 'socks',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'SPARE': {'root': '{userdir}\\.spare-blockchain\\mainnet'.format(userdir=os_path.expanduser("~")),
                           'denominator': 1000000000000,
                           'friendly_name': 'spare',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '0e7dbcaa707b4a75ef62edad42116c2d09e5d66fdcb3a09c2d0262bc50b8fee1'},
                 'STAI': {'root': '{userdir}\\.stai\\mainnet'.format(userdir=os_path.expanduser("~")),
                          'denominator': 1000000000,
                          'friendly_name': 'staicoin',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'e6cee7cac7e6f0c93297804882fc64c326bb68da99d8b2d2690ace371c590b72'},
                 'STOR': {'root': '{userdir}\\.stor\\mainnet'.format(userdir=os_path.expanduser("~")),
                          'denominator': 1000000000000,
                          'friendly_name': 'stor',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '9bc2787915702f8c60cd7456dfb2b62237e92153cbcef895f95bba70116ac950'},
                 'TAD': {'root': '{userdir}\\.tad\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'tad',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'TRZ': {'root': '{userdir}\\.tranzact\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'tranzact',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'WHEAT': {'root': '{userdir}\\.wheat\\mainnet'.format(userdir=os_path.expanduser("~")),
                           'denominator': 1000000000000,
                           'friendly_name': 'wheat',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '2504307e5ea08f9edefb3a002990417c1b8ebec055bbe8cf673e7f56a0601511'},
                 'XBR': {'root': '{userdir}\\.beernetwork\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'Beer',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'e0695b9baaad913fe6fa5622cbe57f40ce125d13ad3f0c705581ae34248ef8f7'},
                 'XBT': {'root': '{userdir}\\.beet\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'Beet',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '9b9ffca948750d8b41ac755da213461e9d2253ec7bfce80695d78f7fe7d55112'},
                 'XBTC': {'root': '{userdir}\\.btcgreen\\mainnet'.format(userdir=os_path.expanduser("~")),
                          'denominator': 1000000000000,
                          'friendly_name': 'btcgreen',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'a41b40c6fbb8941cfa3bd8f1c85ebdeabfd0872c321bb5c1128581d127861585'},
                 'XCA': {'root': '{userdir}\\.xcha\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'xcha',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ed088cce93473427737048f1b1fdab157bd5974ac5accdc70325db541fbf784d'},
                 'XCC': {'root': '{userdir}\\.chives\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 100000000,
                         'friendly_name': 'chives',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '69cfa80789667c51428eaf2f2126e6be944462ee5b59b8128e90b9a650f865c1'},
                 'XCD': {'root': '{userdir}\\.cryptodoge\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000,
                         'friendly_name': 'cryptodoge',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'cb1a2ef31f47e5b59f97c85f07c9132a700d9f4aeaa4e02b5bdc97eda60a0fac'},
                 'XCH': {'root': '{userdir}\\.chia\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'chia',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'XCR': {'root': '{userdir}\\.chiarose\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000,
                         'friendly_name': 'chiarose',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'XDG': {'root': '{userdir}\\.dogechia\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'dogechia',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'c9c3ba2d62e4358c204fc513092f0c020117f0a360c11b11496df75fed2adf4c'},
                 'XETH': {'root': '{userdir}\\.ethgreen\\mainnet'.format(userdir=os_path.expanduser("~")),
                          'denominator': 1000000000,
                          'friendly_name': 'ethgreen',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '03451a58121a612a047a3abfa66f47d56aba93ab555d1c18c8c3ac727b3089b2'},
                 'XFK': {'root': '{userdir}\\.fork\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'fork',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '3800a9169891c0554775b12cbf5d79f6eb50ccb5f95630536a4cecd7a18aa34b'},
                 'XFL': {'root': '{userdir}\\.flora\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'flora',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '3498044cdfa97df3fcb59473bc52d8c70cd8972c6e21e223db3dac6c10595200'},
                 'XFX': {'root': '{userdir}\\.flax\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'flax',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '9b9ffca948750d8b41ac755da213461e9d2253ec7bfce80695d78f7fe7d55112'},
                 'XKA': {'root': '{userdir}\\.kale\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'kale',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '9248f1109f8f5b99d77b39e7e50ed2491848baf30d2837857561c599ef9b74cb'},
                 'XKJ': {'root': '{userdir}\\.kujenga\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'kujenga',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '707cab3aede5efd4258e81e995009c5090cbed67f58770ee0d88e5b322471aa9'},
                 'XKM': {'root': '{userdir}\\.mint\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'mint',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'a8b1ddfcd3d695218800768c4fae609642c12c7ee514a830155a4b90aa5153fc'},
                 'XKW': {'root': '{userdir}\\.kiwi\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'Kiwi',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'b5f3ef35e1b47979d718dfe632d3bf309c6d376fadcb2028dfb42d849caed3e4'},
                 'XMX': {'root': '{userdir}\\.melati\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'melati',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'XMZ': {'root': '{userdir}\\.maize\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'maize',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb'},
                 'XNT': {'root': '{userdir}\\.skynet\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'skynet',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'f0abc049cdffb33880bb7649e8f2dbff68fb8abedb5e8fb3536cc63d545487a8'},
                 'XOL': {'root': '{userdir}\\.olive\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'olive',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '9248f1109f8f5b99d77b39e7e50ed2491848baf30d2837857561c599ef9b74cb'},
                 'XSC': {'root': '{userdir}\\.sector\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'sector',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '8c63fdfef6e0f9a484ecbb19836c01449dfd7694f6acff0c15b5f4654ad74b9b'},
                 'XSHIB': {'root': '{userdir}\\.shibgreen\\mainnet'.format(userdir=os_path.expanduser("~")),
                           'denominator': 1000,
                           'friendly_name': 'shibgreen',
                          'AGG_SIG_ME_ADDITIONAL_DATA': '44fe497ba45f383d4fcf49e508ece6fac56c8d6c0f4f1d5c229cff499df8201d'},
                 'XSLV': {'root': '{userdir}\\.salvia\\mainnet'.format(userdir=os_path.expanduser("~")),
                          'denominator': 1000000000000,
                          'friendly_name': 'salvia',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'cd712de5a54aa420613d90b4c0f7ad28de3ca1f3edef0ef3fe12d2721c067802'},
                 'XTX': {'root': '{userdir}\\.taco\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'taco',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'c37d35863a3cb05730a9905ed93b2370fea5a05726561b0b437cc841ce4b9dc5'},
                 'XVM': {'root': '{userdir}\\.venidium\\mainnet'.format(userdir=os_path.expanduser("~")),
                         'denominator': 1000000000000,
                         'friendly_name': 'venidium',
                          'AGG_SIG_ME_ADDITIONAL_DATA': 'e172a07f4e246178138ed5a27e58c34149134b1d560fe28b640a3a524655063d'}}