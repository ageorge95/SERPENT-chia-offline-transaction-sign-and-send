from os import path
from chia.wallet.derive_keys import master_sk_to_farmer_sk
from chia.wallet.wallet import Wallet
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import puzzle_for_pk,\
    calculate_synthetic_secret_key,\
    DEFAULT_HIDDEN_PUZZLE_HASH
from chia.util.keychain import mnemonic_to_seed
from chia.util.bech32m import encode_puzzle_hash,\
    decode_puzzle_hash
from chia.full_node.bundle_tools import simple_solution_generator
from chia.full_node.mempool_check_conditions import get_name_puzzle_conditions
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.types.coin_spend import CoinSpend
from chia.types.announcement import Announcement
from chia.types.spend_bundle import SpendBundle
from chia.types.condition_opcodes import ConditionOpcode
from chia.util.hash import std_hash
from chia.util.byte_types import hexstr_to_bytes
from chia.util.condition_tools import parse_sexp_to_conditions
from chia.util.condition_tools import conditions_dict_for_solution,\
    pkm_pairs_for_conditions_dict
from blspy import AugSchemeMPL,\
    PrivateKey,\
    G1Element,\
    G2Element
from typing import Dict,\
    AnyStr,\
    Optional,\
    List
import requests
requests.packages.urllib3.disable_warnings()
from traceback import format_exc
from yaml import safe_load
from snake.base import handle_SERPENT_config
from logging import getLogger

class FullNodeAPIwrapper():
    def __init__(self,
                 config_root: AnyStr):
        self.config_root = config_root
        with open(path.join(config_root, 'config.yaml'), 'r') as config_yaml_in:
            self.config = safe_load(config_yaml_in)

        self._log = getLogger()

    def query_full_node(self,
                        url_option,
                        json_data):
        try:
            node_response_raw = requests.post(url=f"https://localhost:{self.config['full_node']['rpc_port']}/{url_option}",
                                 verify=False,
                                 cert=(path.join(self.config_root, 'ssl/full_node/private_full_node.crt'),
                                       path.join(self.config_root, 'ssl/full_node/private_full_node.key')),
                                 headers = {'content-type': 'application/json'},
                                 json=json_data,
                                 )
            try:
                node_response = node_response_raw.json()
                return node_response
            except:
                self._log.error(f"Abnormal full node response: {node_response_raw.text}")
                return None
        except:
            self._log.error(f"Error found while querying the full node at {url_option}\n{format_exc(chain=False)}")
            return None

class SERPENT():
    def __init__(self,
                 asset: AnyStr,
                 mnemonic: AnyStr,
                 send_to_address: AnyStr,
                 amount_to_transfer: float,
                 fee: float = 0,
                 addresses_to_check: int = 50,
                 use_farmer_sk: bool = False
                 ):
        self.config_SERPENT = handle_SERPENT_config()

        self._log = getLogger()

        self.asset = asset
        self.use_farmer_sk = use_farmer_sk
        self.prefix = asset.lower()
        self.fee = int(fee * self.config_SERPENT[asset]['denominator'])
        self.amount_to_transfer = int(amount_to_transfer * self.config_SERPENT[asset]['denominator'])
        self.send_to_address = send_to_address
        self.seed: bytes = mnemonic_to_seed(mnemonic)
        self.addresses_to_check = addresses_to_check
        self.full_node_API_wrapper = FullNodeAPIwrapper(config_root=self.config_SERPENT[asset]['config_root'])

        self._compute_sk_pk()

    def _compute_sk_pk(self):
        self.master_sk: PrivateKey = AugSchemeMPL.key_gen(self.seed)
        self.farmer_sk: PrivateKey = master_sk_to_farmer_sk(self.master_sk)
        self.farmer_pk: G1Element = self.farmer_sk.get_g1()

        self.puzzle_hash_to_sk: Dict[bytes32, PrivateKey] = {}
        self.puzzle_hash_to_pk: Dict[AnyStr, PrivateKey] = {}
        self.hardened_ph: List[AnyStr] = []
        self.hardened_p: List = []
        self.unhardened_ph: List[AnyStr] = []
        self.unhardened_p: List = []
        self.hardened_addr: List = []
        self.unhardened_addr: List = []

        if self.use_farmer_sk:
            puzzle = puzzle_for_pk(self.farmer_pk)
            puzzle_hash = puzzle.get_tree_hash()
            address = encode_puzzle_hash(puzzle_hash, self.prefix)

            self.hardened_ph.append(puzzle_hash.hex())
            self.hardened_p.append(puzzle)
            self.hardened_addr.append(address)
            self.puzzle_hash_to_sk[puzzle_hash] = self.farmer_sk
            self.puzzle_hash_to_pk[puzzle_hash.hex()] = self.farmer_pk

        else:
            # hardened public keys
            wallet_sk_intermediate: PrivateKey = AugSchemeMPL.derive_child_sk(self.master_sk, 12381)
            wallet_sk_intermediate: PrivateKey = AugSchemeMPL.derive_child_sk(wallet_sk_intermediate, self.config_SERPENT[self.asset]['wallet_sk_derivation_port'])
            wallet_sk_intermediate: PrivateKey = AugSchemeMPL.derive_child_sk(wallet_sk_intermediate, 2)
            for i in range(self.addresses_to_check):
                child_sk: PrivateKey = AugSchemeMPL.derive_child_sk(wallet_sk_intermediate, i)
                child_pk: G1Element = child_sk.get_g1()
                puzzle = puzzle_for_pk(child_pk)
                puzzle_hash = puzzle.get_tree_hash()
                address = encode_puzzle_hash(puzzle_hash, self.prefix)

                self.hardened_ph.append(puzzle_hash.hex())
                self.hardened_p.append(puzzle)
                self.hardened_addr.append(address)
                self.puzzle_hash_to_sk[puzzle_hash] = child_sk
                self.puzzle_hash_to_pk[puzzle_hash.hex()] = child_pk

            # unhardened public keys
            wallet_sk_intermediate: PrivateKey = AugSchemeMPL.derive_child_sk_unhardened(self.master_sk, 12381)
            wallet_sk_intermediate: PrivateKey = AugSchemeMPL.derive_child_sk_unhardened(wallet_sk_intermediate, self.config_SERPENT[self.asset]['wallet_sk_derivation_port'])
            wallet_sk_intermediate: PrivateKey = AugSchemeMPL.derive_child_sk_unhardened(wallet_sk_intermediate, 2)
            for i in range(self.addresses_to_check):
                child_sk: PrivateKey = AugSchemeMPL.derive_child_sk_unhardened(wallet_sk_intermediate, i)
                child_pk: G1Element = child_sk.get_g1()
                puzzle = puzzle_for_pk(child_pk)
                puzzle_hash = puzzle.get_tree_hash()
                address = encode_puzzle_hash(puzzle_hash, self.prefix)

                self.unhardened_ph.append(puzzle_hash.hex())
                self.unhardened_p.append(puzzle)
                self.unhardened_addr.append(address)
                self.puzzle_hash_to_sk[puzzle_hash] = child_sk
                self.puzzle_hash_to_pk[puzzle_hash.hex()] = child_pk

    def check_cost(
            self,
            bundle: SpendBundle
    ) -> None:
        """
        Checks that the cost of the transaction does not exceed blockchain limits. As of version 1.1.2, the mempool limits
        transactions to 50% of the block limit, or 0.5 * 11000000000 = 5.5 billion cost.
        """
        program = simple_solution_generator(bundle)
        npc_result = get_name_puzzle_conditions(generator=program,
                                                max_cost=int(self.config_SERPENT[self.asset]['MAX_BLOCK_COST_CLVM'] * 0.5),
                                                cost_per_byte=self.config_SERPENT[self.asset]['COST_PER_BYTE'],
                                                mempool_mode=True)
        cost = npc_result.cost
        assert cost < (0.5 * self.config_SERPENT[self.asset]['MAX_BLOCK_COST_CLVM'])

    def print_conditions(
            self,
            spend_bundle: SpendBundle
    ) -> None:

        conditions_info = []
        for coin_solution in spend_bundle.coin_solutions:
            result = Program.from_bytes(bytes(coin_solution.puzzle_reveal)).run(
                Program.from_bytes(bytes(coin_solution.solution))
            )
            error, result_human = parse_sexp_to_conditions(result)
            assert error is None
            for cvp in result_human:
                conditions_info.append((f"\t{ConditionOpcode(cvp.opcode).name}: {[var.hex() for var in cvp.vars]}"))
        self._log.info("Conditions:\n{}".format('\n'.join(conditions_info)))

    def create_unsigned_transaction(self):
        # ############################
        # verify if the full node is synced
        blockchain_state = self.full_node_API_wrapper.query_full_node(url_option='get_blockchain_state',
                                                                      json_data={})
        synced = blockchain_state['blockchain_state']['sync']['synced']
        assert synced

        # ############################
        # get a list with all the coins, by their puzzlehashes
        all_unspent_coins = self.full_node_API_wrapper.query_full_node(url_option='get_coin_records_by_puzzle_hashes',
                                                                      json_data={'puzzle_hashes': self.hardened_ph + self.unhardened_ph,
                                                                                 'include_spent_coins': False})
        assert all_unspent_coins
        assert all_unspent_coins['success']

        records: List[Coin] = [Coin(hexstr_to_bytes(coin['coin']['parent_coin_info']),
                                    hexstr_to_bytes(coin['coin']['puzzle_hash']),
                                    coin['coin']['amount']) for coin in all_unspent_coins['coin_records']]
        self._log.info(f"Gathered {len(records)} TOTAL coins.")
        # Use smaller coins first
        records.sort(key=lambda r: r.amount)

        # ############################
        # select the coins needed for the amount_to_transfer
        selected_coins: List[Coin] = []
        total_selected_amount = 0
        for record in records:
            total_selected_amount += record.amount
            selected_coins.append(record)

            if total_selected_amount >= self.amount_to_transfer:
                break

        assert total_selected_amount >= self.amount_to_transfer

        # ############################
        # calculate the change
        change = total_selected_amount - self.amount_to_transfer
        primaries = [{"puzzlehash": decode_puzzle_hash(self.send_to_address),
                      "amount": self.amount_to_transfer}]

        self._log.info(f"Selected {len(selected_coins)} coins for transfer,"
                       f" for a total of {total_selected_amount/self.config_SERPENT[self.asset]['denominator']} {self.asset}"
                       f" and a change of {change/self.config_SERPENT[self.asset]['denominator']} {self.asset}.")

        if change > 0:
            # The change is going to the 0th hardened key
            primaries.append({"puzzlehash": hexstr_to_bytes(self.hardened_ph[0]),
                              "amount": change})

        # ############################
        # compute the announcement and build the spend bundle
        primary_announcement_hash: Optional[bytes32] = None
        spends: List[CoinSpend] = []
        for coin in selected_coins:
            # get PK
            puzzle: Program = puzzle_for_pk(self.puzzle_hash_to_pk[coin.puzzle_hash.hex()])
            if primary_announcement_hash is None:
                message_list: List[bytes32] = [c.name() for c in selected_coins]
                for primary in primaries:
                    message_list.append(Coin(coin.name(),
                                             primary["puzzlehash"],
                                             primary["amount"]).name())
                message: bytes32 = std_hash(b"".join(message_list))
                solution: Program = Wallet().make_solution(primaries=primaries,
                                                           fee=self.fee,
                                                           coin_announcements=[message])
                primary_announcement_hash = Announcement(coin.name(), message).name()
            else:
                solution = Wallet().make_solution(primaries=[],
                                                  coin_announcements_to_assert=[primary_announcement_hash])
            spends.append(CoinSpend(coin,
                                    puzzle,
                                    solution))

        self.spend_bundle: SpendBundle = SpendBundle(spends,
                                                G2Element())

        # ####################
        # check the costs
        self.check_cost(self.spend_bundle)
        assert self.spend_bundle.fees() == self.fee

        # #######################
        # print conditions and outputs
        self.print_conditions(self.spend_bundle)
        transaction_outputs = []
        for addition in self.spend_bundle.additions():
            transaction_outputs.append(f"\t{encode_puzzle_hash(addition.puzzle_hash, self.prefix)} {addition.amount}")
        self._log.info("Created transaction with fees: {} and outputs:\n{}".format(self.spend_bundle.fees(),
              '\n'.join(transaction_outputs)))

    def sign_tx(
            self
    ) -> None:
        """
        Uses an unsigned transaction (called a spend bundle in chia), and a 24 word mnemonic (master sk)
        and generates the aggregate BLS signature for the transaction.
        """

        # This field is the ADDITIONAL_DATA found in the constants
        additional_data: bytes = bytes.fromhex(self.config_SERPENT[self.asset]['AGG_SIG_ME_ADDITIONAL_DATA'])

        aggregate_signature: G2Element = G2Element()
        for coin_solution in self.spend_bundle.coin_solutions:
            if coin_solution.coin.puzzle_hash not in self.puzzle_hash_to_sk:
                raise Exception(f"Puzzle hash {coin_solution.coin.puzzle_hash} not found for this key.")

            sk: PrivateKey = self.puzzle_hash_to_sk[coin_solution.coin.puzzle_hash]
            synthetic_secret_key: PrivateKey = calculate_synthetic_secret_key(sk,
                                                                              DEFAULT_HIDDEN_PUZZLE_HASH)

            err, conditions_dict, cost = conditions_dict_for_solution(
                coin_solution.puzzle_reveal, coin_solution.solution, self.config_SERPENT[self.asset]['MAX_BLOCK_COST_CLVM']
            )

            if err or conditions_dict is None:
                raise Exception(f"Transaction sign failed, con:{conditions_dict}, error: {err}")

            pk_msgs = pkm_pairs_for_conditions_dict(conditions_dict,
                                                    bytes(coin_solution.coin.name()),
                                                    additional_data)
            assert len(pk_msgs) == 1
            _, msg = pk_msgs[0]
            signature = AugSchemeMPL.sign(synthetic_secret_key, msg)
            aggregate_signature = AugSchemeMPL.aggregate([aggregate_signature, signature])

        self.signed_spend_bundle = SpendBundle(self.spend_bundle.coin_solutions,
                                               aggregate_signature)

        self._log.info("Transaction signed successfully !")

    def push_tx(
            self
    ) -> None:
        response = self.full_node_API_wrapper.query_full_node(url_option='push_tx',
                                                   json_data={"spend_bundle": self.signed_spend_bundle.to_json_dict()})
        self._log.info(f"Full node response: $${response}$$")

