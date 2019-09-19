from flask import Flask, request, send_file
import subprocess
import os.path
import pandas as pd
import numpy as np
import rstr

app = Flask(__name__)

def unlockwallet():
    unlock_wallet = subprocess.Popen(['cleos', 'wallet', 'unlock','--password','PW5KCH1kz3L1WZDCy98Hrr8kur73T6KfFGHfLzYPb2bAVG4pHR5ns'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    unlock_out, unlock_err = unlock_wallet.communicate()
    return 1
    # print("unlocking wallet error") if(unlock_out.decode()[-18:-1] != 'Unlocked: default') else print("wallet unlocked")

def transfer(account, amount):
    global accounts_df
    unlockwallet()
    transfer = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80', 'push', 'action', 'smurfalexp24', 'transfer', 
    '[ smurfalexp24, '+str(account)+', "'+ str(amount)+'  UFM", reward]', '-p', 'smurfalexp24@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    transfer_out, transfer_err = transfer.communicate()
    if (str(transfer_out).find("transaction executed") >= 0):
        return 1
    else:
        return 0

def balance(account):
    global accounts_df
    unlockwallet()
    get_balance = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80', 'get', 'currency', 'balance',
    'smurfalexp24', str(account) ,'UFM'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    get_balance_out, get_balance_err = get_balance.communicate()
    if(str(get_balance_out.decode()).find("UFM") >= 0):
        return str(get_balance_out)[2:-7]
    else:
        return "0.0000"


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
                create_user = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80','system','newaccount','--stake-net','2.0000 EOS','--stake-cpu','2.0000 EOS', 
                '--buy-ram-kbytes','2','ricardojmv53',str(account),'EOS6YeWnZDHYgtHDvTuqq5NDW3kiCKSoKZQLv8BhppSMjM3uLuoRR',str(public_key)],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                create_user_out, create_user_err = create_user.communicate()
                f=open("NewAccount.txt", "w+")
                f.write(str(create_user_out))
                if (str(create_user_out).find("transaction executed") >= 0):
                    response = {'username': str(username),
                                'private_key':str(private_key),
                                'public_key':str(public_key)
                                }
                    created = True
                    #insert into account df
                    accounts_df = accounts_df.append({'uid':uid,'username':username,'account':account,'privatekey':private_key,'publickey':public_key}, ignore_index=True)
                    accounts_df.to_csv("accounts.csv", index= False)
                elif (str(create_user_out).find("Account name already exists") >= 0):
                    created = False
                elif (str(create_user_out).find("Account using more than allotted RAM") >= 0):
                    created = True
                    response = {"error": "insuficiente RAM to create accounts"}
                else:
                    created = True
                    reponse = {"error":"bad account generation"}
            #enviar dinero
            initial = transfer(account, "200.0000")
            #importar a wallet
            import_key = subprocess.Popen(['cleos', 'wallet', 'import', '--private-key', str(private_key)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return str(response).replace("\'","\"")
    else:
        return 'Missing uid!'

@app.route('/getScores')
def getScores():
    global accounts_df
    temp_df = accounts_df[['username','account']]
    unlockwallet()
    response = [{"name":temp_df['username'].loc[index], "balance":balance(temp_df['account'].loc[index])} for index in range(temp_df.shape[0])]
    response = str(response).replace("\'","\"")
    return response

@app.route('/getBalance')
def getBalance():
    global accounts_df
    uid = str(request.args.get('uid'))
    unlockwallet()
    if (uid != None):
        index = list(accounts_df['uid']).index(uid)
        account = str(accounts_df['account'].iloc[index])
        get_balance = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80', 'get', 'currency', 'balance',
        'smurfalexp24', str(account) ,'UFM'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        get_balance_out, get_balance_err = get_balance.communicate()
        if(str(get_balance_out.decode()).find("UFM") >= 0):
            response = {"balance":str(get_balance_out)[2:-3]}
        else:
            response = {"balance":"0.0000"}
    else:
        response = {"error":"uid missing"}
    response = str(response).replace("\'","\"")
    return response

@app.route('/getReward')
def getReward():
    global accounts_df
    uid = str(request.args.get('uid'))
    amount = str(request.args.get('amount'))
    unlockwallet()
    if (uid != None and amount!= None):
        index = list(accounts_df['uid']).index(uid)
        account = str(accounts_df['account'].iloc[index])
        transfer = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80', 'push', 'action', 'smurfalexp24', 'transfer', 
        '[ smurfalexp24, '+str(account)+', "'+ str(amount)+'  UFM", reward]', '-p', 'smurfalexp24@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        transfer_out, transfer_err = transfer.communicate()
        if (str(transfer_out).find("transaction executed") >= 0):
            response = {"action":"transaction executed successfully"}
        else:
            response = {"error": transfer_out}
    else:
        response = {"error":"uid or amount missing"}

    response = str(response).replace("\'","\"")
    return response

@app.route('/getHint')
def getHint():
    global accounts_df
    uid = str(request.args.get('uid'))
    amount = str(request.args.get('amount'))
    unlockwallet()
    if (uid != None and amount!= None):
        index = list(accounts_df['uid']).index(uid)
        account = str(accounts_df['account'].iloc[index])
        transfer = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80', 'push', 'action', 'smurfalexp24', 'transfer', 
        '[ '+str(account)+', smurfalexp24,  "'+ str(amount)+'  UFM", hint]', '-p', str(account)+'@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        transfer_out, transfer_err = transfer.communicate()
        if (str(transfer_out).find("transaction executed") >= 0):
            response = {"action":"transaction executed successfully"}
        else:
            response = {"error": transfer_out}
    else:
        response = {"error":"uid or amount missing"}

    response = str(response).replace("\'","\"")
    return response

@app.route('/createMatch')
def createMatch():
    global accounts_df
    password = str(request.args.get('password'))
    symbol = str(request.args.get('symbol'))
    maximum = str(request.args.get('maximum'))
    
    if(password == "Queteimporta123" and symbol != None and maximum != None):
        unlockwallet()
        new_token = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80', 'push','action', 'smurfalexp24','create',
        '[ smurfalexp24, "'+str(maximum)+' '+str(symbol)+'"]','-p','smurfalexp24@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        new_token_out, new_token_err = new_token.communicate()
        if (str(new_token_out).find("transaction executed") >= 0):
            issue = subprocess.Popen(['cleos','-u','http://jungle2.cryptolions.io:80','push','action','smurfalexp24','issue',
            '[ smurfalexp24, "'+str(maximum)+' '+str(symbol)+'", "issue tokens"]','-p','smurfalexp24@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            issue_out, issue_err = issue.communicate()
            if (str(issue_out).find("transaction executed") >= 0):
                accounts_df = accounts_df.iloc[0:0]
                accounts_df.to_csv("accounts.csv", index=False)
                response = {"action":"match created successfully"}
            else:
                response = {"error":"error issuing tokens"}
        else:
            response = {"error": new_token_out}
        
    response = str(response).replace("\'","\"")
    return response
    
@app.route('/getMatch')
def getMatch():
    global accounts_df
    # try:
    return send_file(os.path.join("~/accounts.csv"))
    # except:
        # return "Unable to send match file."

if __name__ == '__main__':
    
    # # init keos after
    # kill_keos = subprocess.Popen(['pkill', 'keosd'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    # kill_keos_out, kill_keos_err = kill_keos.communicate()
    # init_keos = subprocess.Popen(['keosd', '&'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
    # init_keos_out, init_keos_err = init_keos.communicate()
    # print("paso")
    # print("keos init error") if(init_keos_err != None) else print("keos initilized")

    app.run(debug=True, port = 5000, host= '0.0.0.0')
