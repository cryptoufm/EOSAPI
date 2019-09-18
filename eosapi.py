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
        return email
    else:
        return 'Missing account or email!'

if __name__ == '__main__':
    print("API INIT")

    # init keos after
    kill_keos = subprocess.Popen(['pkill', 'keosd'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
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
