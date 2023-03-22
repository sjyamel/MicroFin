from flask import *
from main import *
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = 'secret'
db = SQLAlchemy(app)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}} supports_credentials = True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

def init_session():
    try:
        session['user_id']
    except Exception:
        session['user_id'] = None

class Login(Resource):
    @cross_origin()
    def post(self):
        user_id = request.form['user_id']
        psw = request.form['psw']
        if Person.login_is_valid(user_id, psw):
            session['user_id'] = user_id
            return json.dumps({'logged': True}, indent = 4)
        else:
            session['user_id'] = None
            return json.dumps({'logged': False}, indent = 4)

class Signup(Resource):
    def post(self):
        name = request.form['name']
        psw = request.form['psw']
        phone = request.form['phone']
        user_type = 'user'
        data = {'name': name, 'psw': psw, 'phone': phone, 'user_type' : user_type}
        user_id = Person.register(data)
        if user_id != 'phone already Registered!':
            return json.dumps({'user_id' : user_id, 'message' : 'done' })
        else:
            return json.dumps({'message' : user_id, 'user_id' : None})

class AccountInfo(Resource):
    def get(self):
        init_session()
        if session['user_id'] is not None:
            account = Person.get_account_info({'user_id': session['user_id']})
            data = {
                'account_id' : account.account_id,
                'account_number' : account.account_number,
                'account_balance' : account.account_balance
            }
            return json.dumps(data)
        else:
            return json.dumps({'message': 'Login First!'})

class WalletFunding(Resource):
    def post(self):
        init_session()
        if session['user_id'] is not None:
            account_number = request.form['account_number']
            amount = request.form['amount']
            timeline = datetime.datetime.now().strftime('%d-%m-%Y#%H:%M').split('#')
            data = {
                'account_number': account_number,
                'amount': amount,
                'date' : timeline[0],
                'time' : timeline[1]
            }
            user = Person.get_profile_info(session['user_id'])
            Person.FundWallet(user, data)
            return json.dumps({'message': 'done'})
        else:
            return json.dumps({'message': 'Login First!'})

class TransactionsInfo(Resource):
    def get(self):
        init_session()
        if session['user_id'] is not None:
            transactions = Person.get_transactions(session['user_id'])
            data = {"{0}".format(transactions.index(transaction) + 1) : {
                "sender" : transaction.sender,
                'recipient' :transaction.recipient,
                'amount' : transaction.amount,
                "timeline": transaction.timeline,
                "remark" : transaction.remark,
                
                
            }
               for transaction in transactions 
            }
            return json.dumps(data)
        else:
            return json.dumps({'message': 'Login First!'})

class UserName(Resource):
    def get(self):
        init_session()
        if session['user_id'] is not None:
            the_user_id = request.values.get('user_id')
            user = Person.get_profile_info(the_user_id)
            data = {
                'name' : user.name,

            }
            return json.dumps(data)

class Payment(Resource):
    def post(self):
        init_session()
        if session['user_id'] is not None:
            amount = request.form['amount']
            account_number = request.form['account_number']
            pin = request.form['pin']
            current_date = datetime.datetime.now().strftime("%d-%m-%Y")
            current_time = datetime.datetime.now().strftime("%H:%M")
            remark = request.form['remark']
            data = {
                'amount': amount,
                'account_number' : account_number,
                'date': current_date,
                'time': current_time,
                'remark' : remark
            }
            if Person.transaction_is_valid(amount, session['user_id']):
                Person.make_payment(data, session['user_id'], pin)
                return json.dumps({"message": 'done'})
            else:
                return json.dumps({'message' : 'Insufficient Funds'})
        else:
            return json.dumps({"message":"Login First!"})

class WithdrawalRequest(Resource):
    def post(self):
        init_session()
        if session['user_id'] is not None:
            amount = request.form['amount']
            current_date = datetime.datetime.now().strftime("%d-%m-%Y")
            current_time = datetime.datetime.now().strftime("%H:%M")
            data = {
                'amount' : amount,
                'date' : current_date,
                'time' : current_time
            }
            if Person.transaction_is_valid(amount, session['user_id']):
                Person.request_withdrawal(data, session['user_id'])
                return json.dumps({'message' : 'done'})
            else:
                return json.dumps({'message' : 'Insufficient Funds'})
        else:
            return json.dumps({'message' : 'Login First!'})

class ManageTransactionPin(Resource):
    def post(self):
        init_session()
        if session['user_id'] is not None:
            user = Person.get_profile_info(session['user_id'])
            if user.pin is not None:
                current_pin = request.form['current_pin']
                new_pin = request.form['new_pin']
                message = Person.change_pin(session['user_id'], current_pin, new_pin)
                return json.dumps({'message': message})
            else:
                new_pin = request.form['new_pin']
                Person.setup_new_pin(session['user_id'], new_pin)
                return json.dumps({"message" : 'done'})

class Deposits(Resource):
    def get(self):
        init_session['user_id']
        if session['user_id'] is not None:
            deposits = Person.get_deposits(session['user_id'])
            data = {
                '{}'.format(deposits.index(deposit) +1) : {
                'amount' : deposit.amount,
                'timeline' : deposit.timeline
            }
            for deposit in deposits
            }
            return json.dumps(data)

api.add_resource(Login, '/login')
api.add_resource(Signup, '/signup')
api.add_resource(AccountInfo, '/accountinfo')
api.add_resource(WalletFunding, '/fundwallet')  
api.add_resource(TransactionsInfo, '/transactions')
api.add_resource(UserName, '/getuser')
api.add_resource(Payment, '/makepayment')
api.add_resource(WithdrawalRequest, '/requestwithdrawal')
api.add_resource(ManageTransactionPin, '/pinsetup')
api.add_resource(Deposits, '/deposits')

if __name__ == '__main__':
    app.run(debug = True)
