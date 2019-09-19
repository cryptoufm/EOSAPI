# EOSAPI

EOSAPI is an API developed in Python to serve as the comunicator between a web application and the command line interface from eos. The purpose of EOSAPI is to provide the EOS Jungle Test Net services to a web application capable of making http requests.

## Installation

This Installation process is assuming you have already installed the cleos tool for run the commands to the Jungle Test Net. If you have not installed it please visit https://developers.eos.io/eosio-home/docs

##### Python3 Installation

```
sudo apt get install python3
```

##### Pip3 Installation
```
sudo apt get install pip3-python
```

##### Flask
```
pip3 install flask
```

##### RSTR
```
pip3 install rstr
```
## Setup
##### Run the key manager tool from eos developers.
```
keosd &
```
##### Create a wallet 

The following command will create a JSON file containing your wallet configuration and the wallet password.
```
cleos wallet create -n NAME --to-file
```
##### Unlock Your previously created wallet
```
cleos wallet unlock --password WALLET_PASSWORD
```

##### Add the private key of your Jungle Test Net account
This account should be the  privileged account by the contracts that will be called from the Test Net.
```
cleos wallet import --key PRIVATE_KEY
```
## Run
Run the eosapi.py file
```
python3 eosapi.py
```

## Functions

#### createAccount/

HOST:PORT/createAccount?uid=8khblsffwn343224&username=myaccount123

##### Description

The previous endpoint creates a user referring to account parameter and the email address.

##### Response

If the user does not exist in the players table of the contract, the API should return the generated keys with the new account.

If the user exists in the players table of the contract and the email provided is related to an existing account the API should return the corresponding keys of the existing account

The response of the API should look like the following JSON structure:

{"username": "Isabel",
"private_key": "5K7sHYshU68Vs4gBANWwRGESESNa5RrEjMUdsNPKGKkaqnZjVQ2", 
"public_key": "EOS7Xa1oLuYvuUMtwzgj5GKEUbMmLf9473tbvZJbfmyn5c3DUsfoT"}

#### getScores/

HOST:PORT/getScores

 ##### Description
This endpoint should return a json structure containing the players info.

The response of the API should look like the following JSON structure:

  

[{"name":"Luis Araneda",
"balance":"178.0000"},
{"name":"Nicole Stackmann",
"balance":"143.0000"},
{"name":"Juan Pablo Safie",
"balance":"99.0000"
}]

  
#### getBalance/

  
HOST:PORT/getBalance?uid=12312312312

##### Description
Returns the balance of tokens for the provided uid.

##### Response

{“balance”:19.0000} or {“balance”:0.0000}

  
  

#### getReward/
HOST:PORT/getReward?uid=12344565&amount=23.0000


##### Description
If the transaction is executed successfully, a json structures will return indicating it, but if not the json will contain the error.
##### Response

  

{"action": "transaction executed successfully"}

  

#### getHint/
HOST:PORT/getReward?uid=12344565&amount=23.000

  

##### Description

If the transaction is executed successfully, a json structures will return indicating it, but if not the json will contain the error.

  

##### Response

  

{"action": "transaction executed successfully"}

  

#### createMatch/
HOST:PORT/getReward?uid=12344565password=123&symbol=MI&maximum=100000.0000

  

##### Description

This endpoint will create a new token based on the symbol and maximum parameter provided, it also will initialize its players table.

  

##### Response

 
{"action":"match created successfully"}





