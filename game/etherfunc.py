from web3 import Web3
from dotenv import load_dotenv
import os
import json
from web3.middleware import geth_poa_middleware

load_dotenv('../.env', verbose=True)

w3 = Web3(Web3.HTTPProvider(os.environ.get('ETHER_BINGO_HTTP_PROVIDER')))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract_abi = json.loads(os.environ.get('ETHER_BINGO_CONTRACT_ABI'))
contract_address = os.environ.get('ETHER_BINGO_CONTRACT_ADDRESS')
owner_address = os.environ.get('ETHER_BINGO_OWNER_ADDRESS')
private_key = os.environ.get('ETHER_BINGO_OWNER_PRIVATE_KEY')
chain_id = os.environ.get('ETHER_BINGO_CHAIN_ID')


def get_user_balance(user_id):
    ether_bingo_contract = w3.eth.contract(
        address=contract_address, abi=contract_abi)
    user_balance = ether_bingo_contract.functions.viewUserBalance(
        user_id).call({'from': owner_address})
    print(f'user_balance: {user_balance}')


def get_user_total_coin(user_id):
    ether_bingo_contract = w3.eth.contract(
        address=contract_address, abi=contract_abi)
    user_total_coin = ether_bingo_contract.functions.viewUserTotalCoins(
        user_id).call()
    print(f'user_total_coin: {user_total_coin}')


def get_nonce(address):
    nonce = w3.eth.getTransactionCount(address)
    return nonce


# def value_based_gas_price_strategy(web3, transaction_params):
#     if transaction_params['value'] > Web3.toWei(1, 'ether'):
#         return Web3.toWei(20, 'gwei')
#     else:
#         return Web3.toWei(5, 'gwei')

# w3.eth.set_gas_price_strategy(value_based_gas_price_strategy)

def send_user_balance(user_id, amount):
    ether_bingo_contract = w3.eth.contract(
        address=contract_address, abi=contract_abi)
    nonce = get_nonce(owner_address)  #
    transaction = ether_bingo_contract.functions.sendUserEther(user_id, w3.toWei(amount, 'ether')).buildTransaction(
        {"from": owner_address, "nonce": nonce, "chainId": int(chain_id), "gas": 200000, 'gasPrice': w3.toWei('5', 'gwei')})
    signed_txn = w3.eth.account.sign_transaction(
        transaction, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=180)
    # print(ether_bingo_contract.functions.viewUserBalance(
    #     user_id).call({'from': owner_address}))


def check_room_ownership(user_id, room_id, from_time, to_time):
    ether_bingo_contract = w3.eth.contract(
        address=contract_address, abi=contract_abi)
    res = ether_bingo_contract.functions.checkRoomOwnership(
        user_id, room_id, from_time, to_time).call({'from': owner_address})
    return res


def deposit_money(user_id, amount):
    ether_bingo_contract = w3.eth.contract(
        address=contract_address, abi=contract_abi)
    nonce = get_nonce(owner_address)  #
    print(f'nonce:{nonce}')
    transaction = ether_bingo_contract.functions.depositFullMoney(user_id).buildTransaction(
        {"from": owner_address, "nonce": nonce, "value": w3.toWei(amount, 'ether'), "chainId": int(chain_id), "gas": 2000000, 'gasPrice': w3.toWei('50', 'gwei')})
    signed_txn = w3.eth.account.sign_transaction(
        transaction, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=180)
    print(ether_bingo_contract.functions.getBalance().call(
        {'from': owner_address}))


if __name__ == '__main__':
    get_user_balance(46)
    # send_user_balance(46, 0.01)
    # deposit_money(46, 0.1)
