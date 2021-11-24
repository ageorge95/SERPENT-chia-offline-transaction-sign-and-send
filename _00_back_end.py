from logging import getLogger
from json import load,\
    dump
from traceback import format_exc
from sys import path
from os import path as os_path
path.append(os_path.join('chia_blockchain'))

from pprint import pformat
from time import time
from requests import post
from pathlib import Path
from typing import Dict,\
    List,\
    Tuple,\
    Optional
from blspy import G1Element,\
    AugSchemeMPL,\
    PrivateKey,\
    G2Element

from chia_blockchain.chia.consensus.cost_calculator import calculate_cost_of_program
from chia_blockchain.chia.consensus.default_constants import DEFAULT_CONSTANTS
from chia_blockchain.chia.full_node.bundle_tools import simple_solution_generator
from chia_blockchain.chia.full_node.mempool_check_conditions import get_name_puzzle_conditions
from chia_blockchain.chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia_blockchain.chia.types.announcement import Announcement
from chia_blockchain.chia.types.blockchain_format.coin import Coin
from chia_blockchain.chia.types.blockchain_format.program import Program, SerializedProgram
from chia_blockchain.chia.types.coin_record import CoinRecord
from chia_blockchain.chia.types.coin_solution import CoinSolution
from chia_blockchain.chia.types.condition_opcodes import ConditionOpcode
from chia_blockchain.chia.types.blockchain_format.sized_bytes import bytes32
from chia_blockchain.chia.types.spend_bundle import SpendBundle
from chia_blockchain.chia.util.bech32m import encode_puzzle_hash, decode_puzzle_hash
from chia_blockchain.chia.util.condition_tools import parse_sexp_to_conditions
from chia_blockchain.chia.util.config import load_config
from chia_blockchain.chia.util.ints import uint16, uint64
from chia_blockchain.chia.util.hash import std_hash
from chia_blockchain.chia.util.condition_tools import conditions_dict_for_solution, pkm_pairs_for_conditions_dict
from chia_blockchain.chia.util.keychain import mnemonic_to_seed
from chia_blockchain.chia.wallet.wallet import Wallet
from chia_blockchain.chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    puzzle_for_pk,
    calculate_synthetic_secret_key,
    DEFAULT_HIDDEN_PUZZLE_HASH,
)

initial_config = {'AEC': {'root': '{userdir}\\.aedge\\mainnet'.format(userdir=os_path.expanduser("~")),
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
                 'NCH': {'root': '{userdir}\\.chia\\ext9\\db\\blockchain_v1_ext9.sqlite'.format(userdir=os_path.expanduser("~")),
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
                 'STAI': {'root': '{userdir}\\.staicoin\\mainnet'.format(userdir=os_path.expanduser("~")),
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

class SERPENT_back_end():

    _log: getLogger

    def __init__(self):

        if os_path.isfile('config.json'):
            try:
                with open('config.json', 'r') as json_in_handle:
                    self.config = load(json_in_handle)
            except:
                self.config = initial_config
        else:
            self.config = initial_config
            with open('config.json', 'w') as json_out_handle:
                dump(self.config, json_out_handle, indent=2)

        super(SERPENT_back_end, self).__init__()

    def check_mnemonic_integrity(self,
                                 mnemonic: str):
        if mnemonic == '':
            self._log.warning('Please input a non-empty mnemonic !')
            return False
        if mnemonic.count(' ') != 23:
            self._log.warning('Your mnemonic appears to NOT have the exact number of words !')
            return False

        return True

    def compute_parent_public_key(self,
                                  mnemonic: str):

        try:
            seed: bytes = mnemonic_to_seed(mnemonic, passphrase="")
            master_private_key: PrivateKey = AugSchemeMPL.key_gen(seed)
            self.intermediate_sk: PrivateKey = AugSchemeMPL.derive_child_sk(master_private_key, 12381)
            self.intermediate_sk = AugSchemeMPL.derive_child_sk(self.intermediate_sk, 8444)
            self.intermediate_sk = AugSchemeMPL.derive_child_sk(self.intermediate_sk, 2)

            self._log.info('Parent public key computed: {}'.format(self.intermediate_sk.get_g1()))
        except:
            self._log.error('Oh snap, an error occurred while computing the parent public key !\n{}'.format(format_exc(chain=False)))
            raise Exception

    def generate_address_from_child_pk(self,
                                       child_pk: G1Element,
                                       prefix) -> str:
        puzzle = puzzle_for_pk(child_pk)
        puzzle_hash = puzzle.get_tree_hash()
        return encode_puzzle_hash(puzzle_hash, prefix)

    def create_hardened_child_public_keys(self,
                                          coin,
                                          number: int = 50
                                          ):
        """
        Creates child public keys, derived from the master private key, using hardened derivation. This method is more
        secure than public key derivation since it's following the EIP-2333 spec for quantum security.
        """

        try:
            self.hardened_child_public_keys = [bytes(AugSchemeMPL.derive_child_sk(self.intermediate_sk, i).get_g1()) for i in range(number)]
            self._log.info('{} hardened child public keys have been generated successfully !'
                           ' Here are th first 5 addresses:\n{}'.format(number,
                                                                        '\n'.join([self.generate_address_from_child_pk(x, coin) for x in self.hardened_child_public_keys][:5])))
        except:
            self._log.error('Oh snap, an error occurred while creating the hardened child public keys !\n{}'.format(format_exc(chain=False)))
            raise Exception

    async def check_cost(self,
                         bundle: SpendBundle) -> None:
        """
        Checks that the cost of the transaction does not exceed blockchain limits. As of version 1.1.2, the mempool limits
        transactions to 50% of the block limit, or 0.5 * 11000000000 = 5.5 billion cost.
        """
        try:
            program = simple_solution_generator(bundle)
            npc_result = get_name_puzzle_conditions(generator=program,
                                                    max_cost=DEFAULT_CONSTANTS.MAX_BLOCK_COST_CLVM * 0.5,
                                                    cost_per_byte=DEFAULT_CONSTANTS.COST_PER_BYTE,
                                                    safe_mode=True)
            cost = calculate_cost_of_program(SerializedProgram.from_bytes(bytes(program)), npc_result,
                                             DEFAULT_CONSTANTS.COST_PER_BYTE)
            self._log.info(f"Transaction cost: {cost}")
            assert cost < (0.5 * DEFAULT_CONSTANTS.MAX_BLOCK_COST_CLVM)
        except:
            self._log.error('Oh snap, an error occurred while checking the cost !\n{}'.format(format_exc(chain=False)))
            raise Exception

    def print_conditions(self,
                         spend_bundle: SpendBundle):
        try:
            conditions_info = []
            for coin_solution in spend_bundle.coin_solutions:
                result = Program.from_bytes(bytes(coin_solution.puzzle_reveal)).run(
                    Program.from_bytes(bytes(coin_solution.solution)))
                error, result_human = parse_sexp_to_conditions(result)
                assert error is None
                for cvp in result_human:
                    conditions_info.append((f"\t{ConditionOpcode(cvp.opcode).name}: {[var.hex() for var in cvp.vars]}"))
            self._log.info("Conditions:\n{}".format('\n'.join(conditions_info)))
        except:
            self._log.error('Oh snap, an error occurred while printing conditions !\n{}'.format(format_exc(chain=False)))
            raise Exception

    async def create_transaction(self,
        coin,
        outputs: List[Tuple[str, uint64]],
        fee: uint64,
        prefix="xch",
        public_keys: Optional[List[G1Element]] = None,
    ):
        """
        This searches for all coins controlled by the master public key, by deriving child pks in batches of 1000,
        and then searching the blockchain for coins. This requires the full node to be running and synced. Please keep
        the master public key SECRET, since if someone controls the master public key, and one of the child private keys,
        they can derive any other child private key.

        This method creates a spend bundle (transaction) with the given outputs and fees, in MOJO (chia trillionths).
        It is an unsigned transaction so it must be passed to a signer to sign, in JSON.
        """

        try:
            root_path = Path(self.config[coin]['root'])
            config = load_config(root_path, "config.yaml")
            client: FullNodeRpcClient = await FullNodeRpcClient.create("127.0.0.1", uint16(config['full_node']['rpc_port']), root_path, config)
            try:
                state: Dict = await client.get_blockchain_state()

                if not state["sync"]["synced"]:
                    raise Exception(f"Not synced. Please wait for the node to sync and try again.")

                puzzle_hashes: List[bytes32] = []
                puzzle_hash_to_pk: Dict[bytes32, G1Element] = {}
                records: List[CoinRecord] = []

                start = time()
                # Using hardened keys to create transaction
                for pk in public_keys:
                    puzzle = puzzle_for_pk(pk)
                    puzzle_hash = puzzle.get_tree_hash()
                    puzzle_hashes.append(puzzle_hash)
                    puzzle_hash_to_pk[puzzle_hash] = pk
                records = await client.get_coin_records_by_puzzle_hashes(puzzle_hashes, False)

                self._log.info(f"Total number of records: {len(records)}")
                self._log.info(f"Time taken: {time() - start}")

                total_amount: uint64 = uint64(sum([t[1] for t in outputs]) + fee)

                # Use older coins first
                records.sort(key=lambda r: r.timestamp)

                selected_coins: List[Coin] = []
                total_selected_amount = 0
                for record in records:
                    total_selected_amount += record.coin.amount
                    assert record.coin not in selected_coins
                    selected_coins.append(record.coin)

                    if total_selected_amount >= total_amount:
                        break
                if total_selected_amount < total_amount:
                    raise Exception(f"Not enough coins, total value {total_selected_amount}, need {total_amount}")

                change = total_selected_amount - total_amount

                primaries = []
                for address, amount in outputs:
                    primaries.append({"puzzlehash": decode_puzzle_hash(address), "amount": amount})
                if change > 0:
                    # The change is going to the 0th key
                    primaries.append({"puzzlehash": puzzle_hashes[0], "amount": change})

                primary_announcement_hash: Optional[bytes32] = None
                spends: List[CoinSolution] = []
                for coin in selected_coins:
                    # get PK
                    puzzle = puzzle_for_pk(puzzle_hash_to_pk[coin.puzzle_hash])
                    if primary_announcement_hash is None:
                        message_list: List[bytes32] = [c.name() for c in selected_coins]
                        for primary in primaries:
                            message_list.append(Coin(coin.name(), primary["puzzlehash"], primary["amount"]).name())
                        message: bytes32 = std_hash(b"".join(message_list))
                        solution: Program = Wallet().make_solution(primaries=primaries, fee=fee, coin_announcements=[message])
                        primary_announcement_hash = Announcement(coin.name(), message).name()
                    else:
                        solution = Wallet().make_solution(coin_announcements_to_assert=[primary_announcement_hash])
                    spends.append(CoinSolution(coin, puzzle, solution))

                spend_bundle: SpendBundle = SpendBundle(spends, G2Element())

                await self.check_cost(spend_bundle)
                assert spend_bundle.fees() == fee
                self.print_conditions(spend_bundle)

                transaction_outputs = []
                for addition in spend_bundle.additions():
                    transaction_outputs.append(f"\t{encode_puzzle_hash(addition.puzzle_hash, prefix)} {addition.amount}")
                self._log.info("Created transaction with fees: {} and outputs:\n{}".format(spend_bundle.fees(),
                                                                                           '\n'.join(transaction_outputs)))

                self.spend_bundle_unsigned = spend_bundle.to_json_dict()

            finally:
                client.close()
        except:
            self._log.error('Oh snap, an error occurred while creating the transaction !\n{}'.format(format_exc(chain=False)))
            raise Exception

    async def create_unsigned_transaction(self,
                                          address_to_send,
                                          amount_to_send,
                                          fees_to_attach,
                                          coin):
        try:
            await self.create_transaction(
                coin=coin,
                outputs=[
                    (address_to_send, uint64(amount_to_send * self.config[coin]['denominator'])),
                ],
                fee=uint64(fees_to_attach),
                public_keys=self.hardened_child_public_keys,
                prefix=coin.lower()
            )

            self._log.info('Unsigned transaction created successfully:\n{}'.format(pformat(self.spend_bundle_unsigned, indent=2)))
        except:
            self._log.error('Oh snap, an error occurred while creating the unsigned transaction !\n{}'.format(format_exc(chain=False)))
            raise Exception

    def sign_tx(self,
                coin):
        """
        Uses an unsigned transaction (called a spend bundle in chia), and a 24 word mnemonic (master sk)
        and generates the aggregate BLS signature for the transaction.
        """

        try:

            spend_bundle: SpendBundle = SpendBundle.from_json_dict(self.spend_bundle_unsigned)

            # This field is the ADDITIONAL_DATA found in the constants
            additional_data: bytes = bytes.fromhex(self.config[coin]['AGG_SIG_ME_ADDITIONAL_DATA'])
            puzzle_hash_to_sk: Dict[bytes32, PrivateKey] = {}

            # Change this loop to scan more keys if you have more
            for i in range(10):
                child_sk: PrivateKey = AugSchemeMPL.derive_child_sk(self.intermediate_sk, i)
                child_pk: G1Element = child_sk.get_g1()
                puzzle = puzzle_for_pk(child_pk)
                puzzle_hash = puzzle.get_tree_hash()
                puzzle_hash_to_sk[puzzle_hash] = child_sk

            aggregate_signature: G2Element = G2Element()
            for coin_solution in spend_bundle.coin_solutions:
                if coin_solution.coin.puzzle_hash not in puzzle_hash_to_sk:
                    raise Exception(f"Puzzle hash {coin_solution.coin.puzzle_hash} not found for this key.")
                sk: PrivateKey = puzzle_hash_to_sk[coin_solution.coin.puzzle_hash]
                synthetic_secret_key: PrivateKey = calculate_synthetic_secret_key(sk, DEFAULT_HIDDEN_PUZZLE_HASH)

                err, conditions_dict, cost = conditions_dict_for_solution(
                    coin_solution.puzzle_reveal, coin_solution.solution, 11000000000
                )

                if err or conditions_dict is None:
                    raise Exception(f"Sign transaction failed, con:{conditions_dict}, error: {err}")

                pk_msgs = pkm_pairs_for_conditions_dict(conditions_dict, bytes(coin_solution.coin.name()), additional_data)
                assert len(pk_msgs) == 1
                _, msg = pk_msgs[0]
                signature = AugSchemeMPL.sign(synthetic_secret_key, msg)
                aggregate_signature = AugSchemeMPL.aggregate([aggregate_signature, signature])

            # This transaction can be submitted to the blockchain using the RPC: push_tx
            self.signed_spend_bundle = SpendBundle(spend_bundle.coin_solutions, aggregate_signature)

            self._log.info('The transaction has been successfully signed:\n{}'.format(pformat(self.signed_spend_bundle.to_json_dict(),
                                                                                              indent=2)))

        except:
            self._log.error('Oh snap, an error occurred while signing the transaction !\n{}'.format(format_exc(chain=False)))
            raise Exception

    def push_tx_transaction(self,
                            coin):
        try:
            root_path = Path(self.config[coin]['root'])
            config = load_config(root_path, "config.yaml")
            r = post(url='https://localhost:{}/push_tx'.format(uint16(config['full_node']['rpc_port'])),
                     verify=False,
                     cert=(r'{}/config/ssl/full_node/private_full_node.crt'.format(root_path),
                           r'{}/config/ssl/full_node/private_full_node.key'.format(root_path)),
                     headers = {'content-type': 'application/json'},
                     json={"spend_bundle": self.signed_spend_bundle.to_json_dict()},
                     )
            response = r.json()
            self._log.info('The full node responded:\n{}'.format(pformat(response,
                                                                         indent=2)))
            self._log.info('TX push status: {}, success status: {}'.format(response['status'],
                                                                           response['success']))
            if response['success']:
                self._log.info('The transaction should be settled on the blockchain in a couple of minutes ... You can use WILLOW to quickly check the balance.')
            else:
                self._log.info('Something went wrong ! The transaction was not accepted ! Review the input and try again.')
        except:
            self._log.error('Oh snap, an error occurred while pushing the transaction !\n{}'.format(format_exc(chain=False)))
            raise Exception

    async def initiate_transfer(self,
                          coin,
                          mnemonic: str,
                          address_to_send,
                          amount_to_send,
                          fees_to_attach,
                          ):
        if self.check_mnemonic_integrity(mnemonic=mnemonic):
            self._log.info('Initiating transfer ...')
            try:
                self.compute_parent_public_key(mnemonic=mnemonic)
                self.create_hardened_child_public_keys(coin=coin.lower())
                await self.create_unsigned_transaction(address_to_send=address_to_send,
                                                 amount_to_send=amount_to_send,
                                                 fees_to_attach=fees_to_attach,
                                                 coin=coin)
                self.sign_tx(coin=coin.split('__')[0])
                self.push_tx_transaction(coin=coin.split('__')[0])
            except:
                self._log.info('Dang it. Could not finish the transfer :(')
