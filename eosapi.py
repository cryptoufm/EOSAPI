from flask import Flask, request
import subprocess
import os.path
import pandas as pd
import numpy as np
import rstr

app = Flask(__name__)

def unlockwallet():
    unlock_wallet = subprocess.Popen(['cleos', 'wallet', 'unlock','--password','PW5JgLRGuzXmZPKT27vq155hFnLWb1vkt5Ahci5idHaqmYKWVC78G'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    unlock_out, unlock_err = unlock_wallet.communicate()
    return 1
    # print("unlocking wallet error") if(unlock_out.decode()[-18:-1] != 'Unlocked: default') else print("wallet unlocked")

accounts_df = pd.read_csv('accounts.csv')

@app.route('/')
def hello_world():
    return 'EOS API'

@app.route('/createAccount')
def createAccount():
    global accounts_df
    unlockwallet()
    uid = str(request.args.get('uid'))
    username = str(request.args.get('username'))
    if(uid != None):

        if (uid in np.array(accounts_df['uid'])):
            index = list(accounts_df['uid']).index(uid)
            response = str({
                "username": str(accounts_df['username'].iloc[index]),
                "privatekey": str(accounts_df['privatekey'].iloc[index]),
                "publickey": str(accounts_df['publickey'].iloc[index])
            })
        else:
            #create keys
            create_keys = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80', 'create', 'key', '-f', 'KeysUser.txt'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            f = open(os.path.join("KeysUser.txt"), "r")
            private_key = f.readline()[13:-1]
            public_key = f.readline()[12:-1]
            # create account name in jungle
            created = False
            response = ""
            while created == False:
                account = rstr.rstr('abcdefghijklmnopqrtsuvwxyz12345',12)
                create_user = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80','system','newaccount','--stake-net','5.0000 EOS','--stake-cpu','5.0000 EOS', 
                '--buy-ram-kbytes','4','ricardojmv53',str(account),'EOS6YeWnZDHYgtHDvTuqq5NDW3kiCKSoKZQLv8BhppSMjM3uLuoRR',str(public_key)],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                create_user_out, create_user_err = create_user.communicate()
                f=open("NewAccount.txt", "w+")
                f.write(str(create_user_out))
                if (str(create_user_out).find("transaction executed") >= 0):
                    response = {'username': str(account),
                                'private_key':str(private_key),
                                'public_key':str(public_key)
                                }
                    created = True
                    #insert into account df
                    accounts_df = accounts_df.append({'uid':uid,'username':username,'account':account,'privatekey':private_key,'publickey':public_key}, ignore_index=True)
                    accounts_df.to_csv("accounts.csv")
                elif (str(create_user_out).find("Account name already exists") >= 0):
                    created = False
                else:
                    created = True
                    reponse = {"error":"bad account generation"}
        return str(response).replace("\'","\"")
    else:
        return 'Missing uid!'

@app.route('/getScores')
def getScores():

    #iterate the accounts['account'] to request the balance



    unlockwallet()
    response = [
	      {  
	         "name":"Luis Araneda",
	         "balance":"178.00"
	      },
	      {  
	         "name":"Nicole Stackmann",
	         "balance":"143.00"
	      },
	      {  
	         "name":"Juan Pablo Safie",
	         "balance":"99.00"	
	      },
	      {  
	         "name":"Astrid Morales",
	         "balance":"66.00"
	      },
	      {  
	         "name":"Alejandro Melgar",
	         "balance":"17.00"
	      }
	]
    response = str(response).replace("\'","\"")
    return response

@app.route('/getBalance')
def getBalance():
    unlockwallet()
    return 'balance returned'

@app.route('/transfer')
def transfer():
    unlockwallet()
    return 'transfer'

@app.route('/createMatch')
def createMatch():
    unlockwallet()
    return 'creating Match :$'
    

if __name__ == '__main__':
    
    # # init keos after
    # kill_keos = subprocess.Popen(['pkill', 'keosd'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    # kill_keos_out, kill_keos_err = kill_keos.communicate()
    # init_keos = subprocess.Popen(['keosd', '&'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
    # init_keos_out, init_keos_err = init_keos.communicate()
    # print("paso")
    # print("keos init error") if(init_keos_err != None) else print("keos initilized")

    app.run(debug=True, port = 5000, host= '0.0.0.0')
