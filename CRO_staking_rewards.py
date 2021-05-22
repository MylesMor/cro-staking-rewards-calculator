import requests
import json
from decimal import Decimal


def get_genesis():
    """Retrieves the genesis file to aid in calculating rewards for vesting accounts

    :returns: The genesis JSON file or None if the request failed
    """
    genesis = "https://raw.githubusercontent.com/crypto-org-chain/mainnet/main/crypto-org-chain-mainnet-1/genesis.json"
    return requests.get(genesis).json()

def get_account(address):
    """Retrieves the account details of a CRO address

    :param address: The address of the account to retrieve

    :returns: The account JSON file or None if the request failed
    """
    account = "https://crypto.org/explorer/api/v1/accounts/" + address
    account_request = requests.get(account)
    return account_request.json()


def get_transactions(address):
    """Retrieves the transaction details of a CRO address

    :param address: The address of the account to retrieve

    :returns: The transactions JSON file or None if the request failed
    """
    txs = "https://crypto.org/explorer/api/v1/accounts/" + address + "/transactions?limit=1000"
    txs_request = requests.get(txs)
    return txs_request.json()


def get_approximate_fiat_reward_value(total_rewards, currency):
    """Convert CRO to fiat

    :returns: Fiat value of CRO
    """
    approximate_fiat = round(total_rewards * get_current_price(currency.upper()), 2)
    return approximate_fiat


def translate_basecro_to_cro(basecro):
    """ Converts basecro to CRO

    :returns: The value in CRO
    """
    return Decimal(basecro) / 100000000


def determine_vesting_account(account_json, address, genesis):
    """Determines if a vesting account and retrieves the initial balance

    :param account_json: Account data in JSON format
    :param address: Address of the account
    :param genesis: The genesis file

    :returns: Initial balance of vesting account, or 0 if not a vesting account
    """
    if "vesting" in account_json['result']['type'] and genesis != None:
        for item in genesis['app_state']['auth']['accounts']:
            if "base_vesting_account" in item:
                if item['base_vesting_account']['base_account']['address'] == address:
                    return translate_basecro_to_cro(Decimal(item['base_vesting_account']['original_vesting'][0]['amount']))
    return 0

def tally_transactions(address, txs):
    """Calculate the net value of all deposits, withdrawals and fees

    :param address: Address of the account
    :param txs: Transactions JSON for the address

    :returns: The total net value of all deposits, withdrawals and fees
    """
    send_total = 0
    for item in txs['result']:
        if item['success']:
            # Check for deposits/withdrawals
            if "MsgSend" in item['messageTypes']:
                if item['messages'][0]['content']['toAddress'] != address:
                    # Remove withdrawals
                    send_total -= translate_basecro_to_cro(Decimal(item['messages'][0]['content']['amount'][0]['amount']))
                else:
                    # Add deposits
                    send_total += translate_basecro_to_cro(Decimal(item['messages'][0]['content']['amount'][0]['amount']))
            # Remove fees
            send_total -= translate_basecro_to_cro(Decimal(item['fee'][0]['amount']))
    return send_total


def get_total_rewards(address, genesis=None):
    """Calculates and returns total balance and total rewards for an account

    :param address: The account address to calculate balance/rewards for
    :param genesis: The genesis file (to be used for vesting accounts)

    :returns: A dictionary containg balance and rewards or False if the API calls failed
    """
    try:
        txs_json = get_transactions(address)
        account_json = get_account(address)
    except:
        print("Failed to retrieve account and/or transactions.")
        return False
    if (txs_json['result'] == None or account_json['result'] == None):
        print("Failed to retrieve account and/or transactions.")
        return False
    # Determine initial account balance
    initial_balance = determine_vesting_account(account_json, address, genesis)
    send_total = tally_transactions(address, txs_json)
    if len(account_json['result']['totalBalance']) != 0:
        current_total = translate_basecro_to_cro(Decimal(account_json['result']['totalBalance'][0]['amount']))
    else:
        current_total = Decimal(0.0)
    if len(account_json['result']['totalRewards']) != 0:
        unclaimed = translate_basecro_to_cro(Decimal(account_json['result']['totalRewards'][0]['amount']))
    else:
        unclaimed = Decimal(0.0)
    if len(account_json['result']['bondedBalance']) != 0:
        bonded = translate_basecro_to_cro(Decimal(account_json['result']['bondedBalance'][0]['amount']))
    else:
        bonded = Decimal(0.0)
    if "vesting" in account_json['result']['type']:
        bal = Decimal(0.0)
        if (len(account_json['result']['balance']) != 0):
            bal = translate_basecro_to_cro(Decimal(account_json['result']['balance'][0]['amount']))
        total_rewards = abs(current_total - (bonded + bal))
    else:
        total_rewards = abs(current_total - (send_total + initial_balance))
    return {"balance": current_total, "rewards": total_rewards, "unclaimed": unclaimed, "bonded": bonded}


def get_current_price(currency):
    """Returns the current price of CRO in specified fiat currency

    Compatible currencies:
    GBP | USD | EUR | CAD | AUD | NZD | JPY | RUB | CNY | HKD |
    IDR | ILS | DKK | INR | CHF | MXN | CZK | SGD | THB | MYR | 
    NOK | PHP | PLN | ZAR | BRL | TRY | KRW | HUF | SEK

    :param currency: The currency to convert the price of CRO to (must be one of the
        above compatible currencies)

    :returns: The price of CRO in specified currency or False if incompatible currency
    """
    price = "https://api.coingecko.com/api/v3/coins/crypto-com-chain"
    price_request = requests.get(price)
    USD_price = Decimal(price_request.json()['market_data']['current_price']['usd'])
    if currency.upper() != "USD":
        try:
            converted_price = price_request.json()['market_data']['current_price'][currency.lower()]
        except Exception as e:
            print("Incompatible currency!")
            return False
        return converted_price
    return USD_price
