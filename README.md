# CRO Staking Rewards Calculator
A tool for calculating your total DeFi staking rewards in real-time for the Crypto.org Coin (CRO). 

View the app in action at: https://cro.pythonanywhere.com

## API
You can access the API used for this website using this format:

### Request

`https://cro.pythonanywhere.com/rewards?address=ADDRESS&currency=CURRENCY`

- `ADDRESS` should be placed by the address you'd like to retrieve the total rewards for.

- `CURRENCY` should be the fiat currency you'd like the rewards displayed in. Currency must be one of:
  * `GBP | USD | EUR | CAD | AUD | NZD | JPY | RUB | CNY | HKD | IDR | ILS | DKK | INR | CHF | MXN | CZK | SGD | THB | HRK | MYR | NOK | BGN | PHP | PLN | ZAR | ISK | BRL | RON | TRY | KRW | HUF | SEK)`

### Response
You will recieve a JSON response, examples of which can be seen in the [Examples](#examples) section.

### Rate limits
You are limited to 2 requests per second, due to a limited amount of web workers and priority given to the website.

### Examples

#### Valid example
`https://cro.pythonanywhere.com/rewards?address=VALID_ADDRESS&currency=GBP`

```
{
  "data": {
    "fiat_rewards": 30,
    "price_per_cro": 0.149583924766234,
    "rewards": 200.53214778341157,
    "total_balance": 16097.327215743411,
    "total_balance_fiat": 2407.9
    },
  "success": true
}
```

#### Address not found
`https://cro.pythonanywhere.com/rewards?address=cro1359f79e32gfd7rv4mtv67dkvtc9kq9uzqlrsqh&currency=GBP`

```
{
  "data": {
    "price_per_cro": 0.1491602624892415
  },
  "error": 404,
  "message": "Address not found",
  "success": false
}
```

#### Invalid address format
`https://cro.pythonanywhere.com/rewards?address=test&currency=GBP`

```
{
  "data": {
    "price_per_cro": 0.1491602624892415
  },
  "error": 400,
  "message": "Invalid address format",
  "success": false
}
```

#### Rate-limited

```
{
  "error": 429
  "message": "Ratelimit exceeded 2 per 1 second",
  "success": false
}
```
