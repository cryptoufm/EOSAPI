from flask import Flask, request
import subprocess
app = Flask(__name__)



@app.route('/')
def hello_world():
    return 'EOS API'

@app.route('/createAccount')
def createAccount():
    email = str(request.args.get('email'))
    account = request.args.get('account')
    if(email != None and account != None):
        #create keys
        create_keys = subprocess.Popen(['cleos', '-u', 'http://jungle2.cryptolions.io:80', 'create', 'key', '-f', 'KeysUser.txt'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        f = open("KeysUser.txt", "r")
        private_key = f.readline()[13:-1]
        public_key = f.readline()[12:-1]
        # create user
        # create_user = subprocess.Popen(['cleos','-u','http://jungle2.cryptolions.io:80','system',str(account),'--stake-net','"5.0000 EOS"','--stake-cpu','"5.0000 EOS"', 
        # '--buy-ram-kbytes','4','ricardojmv53',str(account),'EOS6YeWnZDHYgtHDvTuqq5NDW3kiCKSoKZQLv8BhppSMjM3uLuoRR'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        response = {'account': account,
                    'private_key':private_key,
                    'public_key':public_key
                    }
        return str(response)
    else:
        return 'Missing account or email!'

if __name__ == '__main__':
    print("API INIT")

    # init keos after
    kill_keos = subprocess.Popen(['pkill', 'keosd'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    kill_keos_out, kill_keos_err = kill_keos.communicate()
    init_keos = subprocess.Popen(['keosd', '&'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
    init_keos_out, init_keos_err = init_keos.communicate()
    print("keos init error") if(init_keos_err != None) else print("keos initilized")

    # unlock default wallet
    lock_wallet = subprocess.Popen(['cleos', 'wallet', 'lock'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    unlock_wallet = subprocess.Popen(['cleos', 'wallet', 'unlock','--password',''], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    unlock_out, unlock_err = unlock_wallet.communicate()
    print("unlocking wallet error") if(unlock_out.decode()[-18:-1] != 'Unlocked: default') else print("wallet unlocked")

    #
    app.run(debug=True, port = 5000)
