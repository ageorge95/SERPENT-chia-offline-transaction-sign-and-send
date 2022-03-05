import sys
from os import path
clvm_rs_root = path.join(sys._MEIPASS, 'clvm_rs_0_1_15/clvm_rs')\
    if '_MEIPASS' in sys.__dict__\
    else path.abspath(path.join(path.dirname(__file__), 'clvm_rs_0_1_15/clvm_rs'))
sys.path.insert(0, clvm_rs_root)
try: sys.path.append(path.join(sys._MEIPASS, 'melon_blockchain'))
except: sys.path.append(path.join(path.dirname(__file__), 'melon_blockchain'))

from json import load
from traceback import format_exc
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
    G2Element,\
    PublicKeyMPL
from melon_blockchain.melon.consensus.cost_calculator import calculate_cost_of_program
from melon_blockchain.melon.consensus.default_constants import DEFAULT_CONSTANTS
from melon_blockchain.melon.full_node.bundle_tools import simple_solution_generator
from melon_blockchain.melon.full_node.mempool_check_conditions import get_name_puzzle_conditions
from melon_blockchain.melon.rpc.full_node_rpc_client import FullNodeRpcClient
from melon_blockchain.melon.types.announcement import Announcement
from melon_blockchain.melon.types.blockchain_format.coin import Coin
from melon_blockchain.melon.types.blockchain_format.program import Program, SerializedProgram
from melon_blockchain.melon.types.coin_record import CoinRecord
from melon_blockchain.melon.types.coin_solution import CoinSolution
from melon_blockchain.melon.types.condition_opcodes import ConditionOpcode
from melon_blockchain.melon.types.blockchain_format.sized_bytes import bytes32
from melon_blockchain.melon.types.spend_bundle import SpendBundle
from melon_blockchain.melon.util.bech32m import encode_puzzle_hash, decode_puzzle_hash
from melon_blockchain.melon.util.condition_tools import parse_sexp_to_conditions
from melon_blockchain.melon.util.config import load_config
from melon_blockchain.melon.util.ints import uint16, uint64
from melon_blockchain.melon.util.hash import std_hash
from melon_blockchain.melon.util.condition_tools import conditions_dict_for_solution, pkm_pairs_for_conditions_dict
from melon_blockchain.melon.util.keychain import mnemonic_to_seed
from melon_blockchain.melon.util.byte_types import hexstr_to_bytes
from melon_blockchain.melon.wallet.wallet import Wallet
from melon_blockchain.melon.wallet.derive_keys import master_sk_to_farmer_sk
from melon_blockchain.melon.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import (
    puzzle_for_pk,
    calculate_synthetic_secret_key,
    DEFAULT_HIDDEN_PUZZLE_HASH,
)

class SERPENT_back_end():

    def __init__(self):

        config_path = 'config_SERPENT.json' if '_MEIPASS' in sys.__dict__ \
                                            else path.join(path.dirname(__file__), 'config_SERPENT.json')
        with open(config_path, 'r') as json_in_handle:
            self.config_SERPENT = load(json_in_handle)

        self.return_print_payload = [['info',
                                      'SERPENT backend init completed.']]

    def check_mnemonic_integrity(
            self,
            mnemonic: str
    ) -> bool:
        if mnemonic == '':
            self.return_print_payload.append(['warning',
                                              'Please input a non-empty mnemonic !'])
            return False
        if mnemonic.count(' ') != 23:
            self.return_print_payload.append(['warning',
                                              'Your mnemonic appears to NOT have the exact number of words !'])
            return False

        return True

    def _compute_sks(
            self,
            mnemonic: str
    ) -> None:

        try:
            seed: bytes = mnemonic_to_seed(mnemonic, passphrase="")
            master_sk: PrivateKey = AugSchemeMPL.key_gen(seed)
            self.farmer_sk: PrivateKey = master_sk_to_farmer_sk(master_sk)
            self.farmer_pk: PublicKeyMPL = self.farmer_sk.get_g1()
            self.intermediate_sk: PrivateKey = AugSchemeMPL.derive_child_sk(master_sk, 12381)
            self.intermediate_sk: PrivateKey = AugSchemeMPL.derive_child_sk(self.intermediate_sk, 8444)
            self.intermediate_sk: PrivateKey = AugSchemeMPL.derive_child_sk(self.intermediate_sk, 2)

            self.return_print_payload.append(['info',
                                              'sks computed.'])
        except:
            self.return_print_payload.append(['error',
                                              'Oh snap, an error occurred while computing the parent public key !\n{}'.format(format_exc(chain=False))])
            raise Exception

    def generate_address_from_pk(
            self,
            pk: G1Element,
            prefix: str
    ) -> str:

        puzzle = puzzle_for_pk(pk)
        puzzle_hash = puzzle.get_tree_hash()

        return encode_puzzle_hash(puzzle_hash, prefix)

    def _create_hardened_child_pks(
            self,
            prefix,
            use_farmer_sk: bool,
            number: int = 50,
    ) -> None:
        """
        Creates child public keys, derived from the master private key, using hardened derivation. This method is more
        secure than public key derivation since it's following the EIP-2333 spec for quantum security.
        """

        try:
            if use_farmer_sk:
                self.hardened_child_pks = [hexstr_to_bytes(str(self.farmer_pk))]
            else:
                self.hardened_child_pks = [bytes(AugSchemeMPL.derive_child_sk(self.intermediate_sk, i).get_g1()) for i in range(number)]
                self.return_print_payload.append(['info',
                                                  '{} hardened child public keys have been generated successfully !'
                                                  ' Here are the first 5 addresses:\n{}'.format(number,
                                                                            '\n'.join([self.generate_address_from_pk(x, prefix) for x in self.hardened_child_pks][:5]))])
        except:
            self.return_print_payload.append(['error',
                                              'Oh snap, an error occurred while creating the hardened child public keys !\n{}'.format(format_exc(chain=False))])
            raise Exception

    async def check_cost(
            self,
            bundle: SpendBundle
    ) -> None:
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
            self.return_print_payload.append(['info',
                                              f"Transaction cost: {cost}"])
            assert cost < (0.5 * DEFAULT_CONSTANTS.MAX_BLOCK_COST_CLVM)
        except:
            self.return_print_payload.append(['error',
                                              'Oh snap, an error occurred while checking the cost !\n{}'.format(format_exc(chain=False))])
            raise Exception

    def print_conditions(
            self,
            spend_bundle: SpendBundle
    ) -> None:

        try:
            conditions_info = []
            for coin_solution in spend_bundle.coin_solutions:
                result = Program.from_bytes(bytes(coin_solution.puzzle_reveal)).run(
                    Program.from_bytes(bytes(coin_solution.solution))
                )
                error, result_human = parse_sexp_to_conditions(result)
                assert error is None
                for cvp in result_human:
                    conditions_info.append((f"\t{ConditionOpcode(cvp.opcode).name}: {[var.hex() for var in cvp.vars]}"))
            self.return_print_payload.append(['info',
                                              "Conditions:\n{}".format('\n'.join(conditions_info))])
        except:
            self.return_print_payload.append(['error',
                                              'Oh snap, an error occurred while printing conditions !\n{}'.format(format_exc(chain=False))])
            raise Exception

    async def create_transaction(
            self,
            asset: str,
            outputs: List[Tuple[str, uint64]],
            fee: uint64,
            prefix: str,
            pks: Optional[List[G1Element]] = None
    ):
        """
        This searches for all coins controlled by the master public key, by deriving child pks in batches of 1000,
        and then searching the blockchain for coins. This requires the full node to be running and synced. Please keep
        the master public key SECRET, since if someone controls the master public key, and one of the child private keys,
        they can derive any other child private key.

        This method creates a spend bundle (transaction) with the given outputs and fees, in MOJO (chia trillionths),
        or the equivalent for chia forks.
        It is an unsigned transaction so it must be passed to a signer to sign, in JSON.
        """

        try:
            root_path = Path(self.config_SERPENT[asset]['root'])
            config = load_config(root_path, "config.yaml")
            client: FullNodeRpcClient = await FullNodeRpcClient.create("127.0.0.1",
                                                                       uint16(config['full_node']['rpc_port']),
                                                                       root_path,
                                                                       config)
            try:
                state: Dict = await client.get_blockchain_state()

                if not state["sync"]["synced"]:
                    raise Exception(f"Not synced. Please wait for the node to sync and try again.")

                puzzle_hashes: List[bytes32] = []
                puzzle_hash_to_pk: Dict[bytes32, G1Element] = {}

                start = time()
                for pk in pks:
                    puzzle = puzzle_for_pk(pk)
                    puzzle_hash = puzzle.get_tree_hash()
                    puzzle_hashes.append(puzzle_hash)
                    puzzle_hash_to_pk[puzzle_hash] = pk
                records: List[CoinRecord] = await client.get_coin_records_by_puzzle_hashes(puzzle_hashes, False)

                self.return_print_payload.append(['info',
                                                  f"Total number of records: {len(records)}"])
                self.return_print_payload.append(['info',
                                                  f"Time taken: {time() - start}"])

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
                self.return_print_payload.append(['info',
                                                  "Created transaction with fees: {} and outputs:\n{}".format(spend_bundle.fees(),
                                                                                           '\n'.join(transaction_outputs))])

                self.spend_bundle_unsigned = spend_bundle.to_json_dict()

            finally:
                client.close()
        except:
            self.return_print_payload.append(['error',
                                              'Oh snap, an error occurred while creating the transaction !\n{}'.format(format_exc(chain=False))])
            raise Exception

    async def create_unsigned_transaction_hardened(
            self,
            send_to_address: str,
            amount_to_send: float,
            fees_to_attach: float,
            asset: str
    ) -> None:
        try:
            await self.create_transaction(
                asset=asset,
                outputs=[(send_to_address,
                          uint64(amount_to_send * self.config_SERPENT[asset]['denominator']))],
                fee=uint64(fees_to_attach * self.config_SERPENT[asset]['denominator']),
                pks=self.hardened_child_pks,
                prefix=asset.lower()
            )

            self.return_print_payload.append(['info',
                                              'Unsigned transaction created successfully:\n{}'.format(pformat(self.spend_bundle_unsigned, indent=2))])
        except:
            self.return_print_payload.append(['error',
                                              'Oh snap, an error occurred while creating the unsigned transaction !\n{}'.format(format_exc(chain=False))])
            raise Exception

    def sign_tx(
            self,
            asset: str,
            use_farmer_sk: bool,
            number: int = 50
    ) -> None:
        """
        Uses an unsigned transaction (called a spend bundle in chia), and a 24 word mnemonic (master sk)
        and generates the aggregate BLS signature for the transaction.
        """

        try:

            spend_bundle: SpendBundle = SpendBundle.from_json_dict(self.spend_bundle_unsigned)

            # This field is the ADDITIONAL_DATA found in the constants
            additional_data: bytes = bytes.fromhex(self.config_SERPENT[asset]['AGG_SIG_ME_ADDITIONAL_DATA'])
            puzzle_hash_to_sk: Dict[bytes32, PrivateKey] = {}

            if not use_farmer_sk:
                for i in range(number):
                    child_sk: PrivateKey = AugSchemeMPL.derive_child_sk(self.intermediate_sk, i)
                    child_pk: G1Element = child_sk.get_g1()
                    puzzle = puzzle_for_pk(child_pk)
                    puzzle_hash = puzzle.get_tree_hash()
                    puzzle_hash_to_sk[puzzle_hash] = child_sk
            else:
                for entry in self.hardened_child_pks:
                    puzzle_hash_to_sk[puzzle_for_pk(entry).get_tree_hash()] = self.farmer_sk

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

            self.return_print_payload.append(['info',
                                              'The transaction has been successfully signed:\n{}'.format(pformat(self.signed_spend_bundle.to_json_dict(),
                                                                                              indent=2))])

        except:
            self.return_print_payload.append(['error',
                                              'Oh snap, an error occurred while signing the transaction !\n{}'.format(format_exc(chain=False))])
            raise Exception

    def push_tx_transaction(
            self,
            asset: str
    ) -> None:
        try:
            root_path = Path(self.config_SERPENT[asset]['root'])
            config = load_config(root_path, "config.yaml")
            r = post(url='https://localhost:{}/push_tx'.format(uint16(config['full_node']['rpc_port'])),
                     verify=False,
                     cert=(r'{}/config/ssl/full_node/private_full_node.crt'.format(root_path),
                           r'{}/config/ssl/full_node/private_full_node.key'.format(root_path)),
                     headers = {'content-type': 'application/json'},
                     json={"spend_bundle": self.signed_spend_bundle.to_json_dict()},
                     )
            response = r.json()
            self.return_print_payload.append(['info',
                                              'The full node responded:{},'.format(pformat(response,
                                                                         indent=2))])
            self.return_print_payload.append(['info',
                                              'TX push status: {}, success status: {}'.format(response['status'],
                                                                           response['success'])])
            if response['success']:
                self.return_print_payload.append(['info',
                                                  'The transaction should be settled on the blockchain in a couple of minutes ... You can use WILLOW to quickly check the balance.'])
            else:
                self.return_print_payload.append(['info',
                                                  'Something went wrong ! The transaction was not accepted ! Review the input and try again.'])

            return response
        except:
            self.return_print_payload.append(['info',
                                              'Oh snap, an error occurred while pushing the transaction !\n{}'.format(format_exc(chain=False))])
            raise Exception

    async def initiate_transfer_final(
            self,
            asset: str,
            mnemonic: str,
            send_to_address: str,
            amount_to_send: float,
            fees_to_attach: float,
            use_farmer_sk: bool
    ):
        if self.check_mnemonic_integrity(mnemonic=mnemonic):
            self.return_print_payload.append(['info',
                                              'Initiating transfer ...'])
            try:
                self._compute_sks(mnemonic=mnemonic)
                self._create_hardened_child_pks(prefix=asset.lower(),
                                                use_farmer_sk=use_farmer_sk)
                await self.create_unsigned_transaction_hardened(send_to_address=send_to_address,
                                                                amount_to_send=amount_to_send,
                                                                fees_to_attach=fees_to_attach,
                                                                asset=asset)
                self.sign_tx(asset=asset.split('__')[0],
                             use_farmer_sk=use_farmer_sk)
                self.push_tx_transaction(asset=asset.split('__')[0])
            except:
                self.return_print_payload.append(['error',
                                                  format_exc(chain=False)])
                self.return_print_payload.append(['info',
                                                  'Dang it. Could not finish the transfer :('])

        return self.return_print_payload