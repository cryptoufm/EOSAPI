from flask import Flask, request
import subprocess
app = Flask(__name__)
import os.path





@app.route('/')
def hello_world():
    return 'EOS API'

@app.route('/createAccount')
def createAccount():
    email = str(request.args.get('email'))
    account = request.args.get('account')
    if(email != None and account != None):
        # validate email or account exists in contract and return the keys in case it exists

        #create keys
        create_keys = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80', 'create', 'key', '-f', 'KeysUser.txt'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        f = open(os.path.join("KeysUser.txt"), "r")
        private_key = f.readline()[13:-1]
        public_key = f.readline()[12:-1]
        # create user
        create_user = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80','system','newaccount','--stake-net','5.0000 EOS','--stake-cpu','5.0000 EOS', 
        '--buy-ram-kbytes','4','ricardojmv53',str(account),'EOS6YeWnZDHYgtHDvTuqq5NDW3kiCKSoKZQLv8BhppSMjM3uLuoRR',str(public_key)],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        create_user_out, create_user_err = create_user.communicate()
        f=open("NewAccount.txt", "w+")
        f.write(str(create_user_out))
        if (str(create_user_out).find("Account name already exists") >= 0):
            response = {"error":"account already exist in jungle"}
        elif (str(create_user_out).find("transaction executed") >= 0):
            response = {'account': account,
                        'private_key':private_key,
                        'public_key':public_key
                        }
        else:
            response = {'error':create_user_out}
        return str(response)
    else:
        return 'Missing account or email!'

@app.route('/getScores')
def getScores():
    return 'scores perro'

@app.route('/getBalance')
def getBalance():
    return 'balance returned'

@app.route('/transfer')
def transfer():
    return 'transfer'



if __name__ == '__main__':

    # # init keos after
    # kill_keos = subprocess.Popen(['pkill', 'keosd'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    # kill_keos_out, kill_keos_err = kill_keos.communicate()
    # init_keos = subprocess.Popen(['keosd', '&'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
    # init_keos_out, init_keos_err = init_keos.communicate()
    # print("paso")
    # print("keos init error") if(init_keos_err != None) else print("keos initilized")

    # # unlock default wallet
    # lock_wallet = subprocess.Popen(['cleos', 'wallet', 'lock'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    # unlock_wallet = subprocess.Popen(['cleos', 'wallet', 'unlock','--password','PW5KCH1kz3L1WZDCy98Hrr8kur73T6KfFGHfLzYPb2bAVG4pHR5ns'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    # unlock_out, unlock_err = unlock_wallet.communicate()
    # print("unlocking wallet error") if(unlock_out.decode()[-18:-1] != 'Unlocked: default') else print("wallet unlocked")

    app.run(debug=True, port = 5000, host= '0.0.0.0')
