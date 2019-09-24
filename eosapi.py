from flask import Flask, request, send_file
import subprocess
import os.path
import pandas as pd
import numpy as np
import rstr
import yaml

app = Flask(__name__)
 
config = yaml.load(open("configuration.yml", "r"), Loader=yaml.FullLoader)
accounts_df = pd.read_csv('accounts.csv')
def openMatch(number):
    df = pd.read_csv(number+'.csv')
    return df

def unlockwallet():
    unlock_wallet = subprocess.Popen(['cleos', 'wallet', 'unlock','--password',str(config['WALLETPASSWORD'])], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    unlock_out, unlock_err = unlock_wallet.communicate()
    return 1

def transfer(account, amount, message=None):
    global accounts_df, config
    unlockwallet()
    transfer = subprocess.Popen(['cleos', '-u', str(config['JUNGLEENDPOINT']), 'push', 'action', str(config['CONTRACTOWNER']), 'transfer', 
    '[ '+str(config['CONTRACTOWNER'])+', '+str(account)+', "'+ str(amount)+'  '+str(config['TOKEN'])+'", '+str(message)+']', '-p', str(config['CONTRACTOWNER'])+'@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    transfer_out, transfer_err = transfer.communicate()
    if (str(transfer_out).find("transaction executed") >= 0):
        return 1
    else:
        return 0

def balance(account):
    global accounts_df
    unlockwallet()
    get_balance = subprocess.Popen(['cleos', '-u', str(config['JUNGLEENDPOINT']), 'get', 'currency', 'balance',
    str(config['CONTRACTOWNER']), str(account) ,str(config['TOKEN'])], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    get_balance_out, get_balance_err = get_balance.communicate()
    if(str(get_balance_out.decode()).find(str(config['TOKEN'])) >= 0):
        return str(get_balance_out)[2:-7]
    else:
        return "0.0000"

@app.route('/')
def hello_world():
    return 'EOS API'

@app.route('/createAccount')
def createAccount():
    global config
    accounts_df = openMatch('accounts')
    unlockwallet()
    uid = str(request.args.get('uid'))
    username = str(request.args.get('username'))
    amount = str(request.args.get('amount'))
    if(uid != None):

        if (int(uid) in np.array(accounts_df['uid'])):
            index = list(accounts_df['uid']).index(int(uid))
            response = str({
                "username": str(accounts_df['username'].iloc[index]),
                "account": str(accounts_df['account'].iloc[index]),
                "privatekey": str(accounts_df['privatekey'].iloc[index]),
                "publickey": str(accounts_df['publickey'].iloc[index])
            })
            
        else:
            #create keys
            create_keys = subprocess.Popen(['cleos', '-u', str(config['JUNGLEENDPOINT']), 'create', 'key', '-f', 'KeysUser.txt'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            f = open(os.path.join("KeysUser.txt"), "r")
            private_key = f.readline()[13:-1]
            public_key = f.readline()[12:-1]
            # create account name in jungle
            created = False
            response = ""
            while created == False:
                account = username[:6]+str(rstr.rstr('abcdefghijklmnopqrtsuvwxyz12345',6))
                create_user = subprocess.Popen(['cleos', '-u', str(config['JUNGLEENDPOINT']),'system','newaccount','--stake-net','2.0000 EOS','--stake-cpu','2.0000 EOS', 
                '--buy-ram-kbytes','2',str(config['ACCOUNTSGENERATOR']),str(account),str(config['ACCOUNTSGENERATORPASSWORD']),str(public_key)],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                create_user_out, create_user_err = create_user.communicate()
                f=open("NewAccount.txt", "w+")
                f.write(str(create_user_out))
                if (str(create_user_out).find("transaction executed") >= 0):
                    response = {'username': str(username),
                                'account': str(account),
                                'private_key':str(private_key),
                                'public_key':str(public_key)
                                }
                    created = True
                    transfer(account, amount, 'initial')
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
            #importar a wallet
            import_key = subprocess.Popen(['cleos', 'wallet', 'import', '--private-key', str(private_key)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return str(response).replace("\'","\"")
    else:
        return 'Missing uid!'

@app.route('/getScores')
def getScores():
    match = str(request.args.get('match'))
    files = os.listdir(os.getcwd())
    if str(match+'.csv') in files:
        accounts_df = openMatch(match)
        temp_df = accounts_df
        unlockwallet()
        response = [{"name":temp_df['account'].loc[index], "balance":float(balance(temp_df['account'].loc[index]))} for index in range(temp_df.shape[0])]
        response = sorted(response, key = lambda i: i["balance"],reverse=True) 
    else:
        response = {"error":"match not found"}
    return str(response).replace("\'","\"")
        

@app.route('/getBalance')
def getBalance():
    global config
    uid = str(request.args.get('uid'))
    match = str(request.args.get('match'))
    accounts_df = openMatch(match)
    unlockwallet()
    if (uid != None):
        index = list(accounts_df['uid']).index(int(uid))
        account = str(accounts_df['account'].iloc[index])
        get_balance = subprocess.Popen(['cleos', '-u', str(config['JUNGLEENDPOINT']), 'get', 'currency', 'balance',
        str(config['CONTRACTOWNER']), str(account) , str(config['TOKEN'])], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        get_balance_out, get_balance_err = get_balance.communicate()
        if(str(get_balance_out.decode()).find(str(config['TOKEN'])) >= 0):
            response = {"balance":str(get_balance_out)[2:-3]}
        else:
            response = {"balance":"0.0000"}
    else:
        response = {"error":"uid missing"}
    response = str(response).replace("\'","\"")
    return response

@app.route('/getReward')
def getReward():
    global config
    match = str(request.args.get('match'))
    uid = str(request.args.get('uid'))
    amount = str(request.args.get('amount'))
    accounts_df = openMatch(match)
    unlockwallet()
    if (uid != None and amount!= None):
        index = list(accounts_df['uid']).index(int(uid))
        account = str(accounts_df['account'].iloc[index])
        transfer = subprocess.Popen(['cleos', '-u', str(config['JUNGLEENDPOINT']), 'push', 'action', str(config['CONTRACTOWNER']), 'transfer', 
        '[ '+str(config['CONTRACTOWNER'])+', '+str(account)+', "'+ str(amount)+'  '+str(config['TOKEN'])+'", reward]', '-p', str(config['CONTRACTOWNER'])+'@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
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
    global config
    match = str(request.args.get('match'))
    uid = str(request.args.get('uid'))
    amount = str(request.args.get('amount'))
    accounts_df = openMatch(match)
    unlockwallet()
    if (uid != None and amount!= None and match != None):
        index = list(accounts_df['uid']).index(int(uid))
        account = str(accounts_df['account'].iloc[index])
        transfer = subprocess.Popen(['cleos', '-u', str(config['JUNGLEENDPOINT']), 'push', 'action', str(config['CONTRACTOWNER']), 'transfer', 
        '[ '+str(account)+', '+str(config['CONTRACTOWNER'])+',  "'+ str(amount)+'  '+str(config['TOKEN'])+'", hint]', '-p', str(account)+'@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        transfer_out, transfer_err = transfer.communicate()
        if (str(transfer_out).find("transaction executed") >= 0):
            response = {"action":"transaction executed successfully"}
        else:
            response = {"error": transfer_out}
    else:
        response = {"error":"uid, amount or match missing"}

    response = str(response).replace("\'","\"")
    return response

@app.route('/createMatch')
def createMatch():
    global accounts_df, config
    password = str(request.args.get('password'))
    symbol = str(rstr.rstr('ABCDEFGHIJKLMNOPQRSTUVWXYZ',3))
    maximum = str(request.args.get('maximum'))
    
    pass
    if(password == "Queteimporta123" and symbol != None and maximum != None):
        unlockwallet()

        new_token = subprocess.Popen(['cleos', '-u', str(config['JUNGLEENDPOINT']), 'push','action', str(config['CONTRACTOWNER']),'create',
        '[ '+str(config['CONTRACTOWNER'])+', "'+str(maximum)+' '+str(symbol)+'"]','-p', str(config['CONTRACTOWNER'])+'@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        new_token_out, new_token_err = new_token.communicate()
        if (str(new_token_out).find("transaction executed") >= 0):
            issue = subprocess.Popen(['cleos','-u',str(config['JUNGLEENDPOINT']),'push','action',str(config['CONTRACTOWNER']),'issue',
            '[ '+str(config['CONTRACTOWNER'])+', "'+str(maximum)+' '+str(symbol)+'", "issue tokens"]','-p', str(config['CONTRACTOWNER'])+'@active'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            issue_out, issue_err = issue.communicate()
            if (str(issue_out).find("transaction executed") >= 0):
                match = str(rstr.rstr('0123456789',10))
                new_match = pd.DataFrame({'uid':[],'account':[],'start_time':[],'balance':[]})
                new_match.to_csv(match+'.csv', index= False)
                config['TOKEN']=symbol
                with open('configuration.yml', 'w') as f:
                    yaml.dump(config, f)
                response = {"match": match}
            else:
                response = {"error":"error issuing tokens"}
        else:
            response = {"error": new_token_out}

    response = str(response).replace("\'","\"")
    return response
    
@app.route('/getMatch')
def getMatch():
    global accounts_df
    match = str(request.args.get('match'))
    files = os.listdir(os.getcwd())
    if str(match+'.csv') in files:
        return send_file(os.path.join(match+'.csv'))
    else:
        return {"error":"match not"}


@app.route('/getProfile')
def getProfile():
    global config
    accounts_df = openMatch('accounts')
    uid = str(request.args.get('uid'))
    if (int(uid) in np.array(accounts_df['uid'])):
        index = list(accounts_df['uid']).index(int(uid))
        response = {"account": accounts_df['account'].loc[index],
                    "privatekey": accounts_df['privatekey'].loc[index],
                    "balance": balance(accounts_df['account'].loc[index])}
    else:
        response = {"error": "uid not in recognized"}
    return str(response).replace("\'","\"")

@app.route('/joinMatch')
def joinMatch():
    global config
    uid = str(request.args.get('uid'))
    match = str(request.args.get('match'))
    time = str(request.args.get('time'))
    files = os.listdir(os.getcwd())
    accounts_df = openMatch('accounts')
    if str(match+'.csv') in files:
        df = openMatch(match)
        if(int(uid) in np.array(accounts_df['uid'])):
            if len(df.index)==0:
                index = list(accounts_df['uid']).index(int(uid))
                df = df.append({'uid':uid,'account':accounts_df['account'].loc[index],'start_time':time,'balance':balance(uid)}, ignore_index=True)
                response = {"action": "user added to match"}
                df.to_csv(match+'.csv', index= False)
                response = {"action":"user inserted in match"}
            else:
                if(int(uid) in np.array(df['uid'])):
                    al = list(df['uid']).index(int(uid))
                    response = {"action": "player already in match"}
                else:
                    index = list(accounts_df['uid']).index(int(uid))
                    df = df.append({'uid':uid,'account':accounts_df['account'].loc[index],'start_time':time,'balance':balance(uid)}, ignore_index=True)
                    response = {"action": "user added to match"}
                    df.to_csv(match+'.csv', index= False)
        else:
            response = {"error":"uid not in accounts"}
    else:
        response = {"error": "match not found"}
    return str(response).replace("\'","\"")


if __name__ == '__main__':
    
    app.run(debug=True, port = 5000, host= '0.0.0.0')
