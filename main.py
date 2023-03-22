from database import *
import hashlib
import datetime
import string
import random

class Person(object):

    @staticmethod
    def genid():
        letters = string.ascii_letters
        return ''.join([random.choice(letters) for r in range(2)]) + ''.join([random.choice('1234567890') for r in range(4)]) 

    @staticmethod
    def login_is_valid(user_id, psw):
        psw = hashlib.md5(psw.encode('utf-8')).hexdigest()
        with app.app_context():
            user = Database.find_one_from_table(
                table = Users,
                keys = dict(
                    user_id = user_id,
                    psw = psw
                )
            )
        return user is not None

    @staticmethod
    def exists(user_id, phone):
        with app.app_context():
            user_with_id = Database.find_one_from_table(
                table = Users,
                keys = dict(
                    user_id = user_id
                )
            )
            user_with_phone = Database.find_one_from_table(
                table = Users,
                keys = dict(
                    phone = phone
                )
            )
            
        return user_with_id is not None, user_with_phone is not None

    @staticmethod
    def register(data):
        new_id = Person.genid()
        data['psw'] = hashlib.md5(data['psw'].encode('utf-8')).hexdigest()
        account_data = {
            'account_balance' : '0.0',
            'account_id' : ''.join(reversed(new_id)),
            'account_number' : data['phone'][1:],
            'user_id' : new_id,
            'account_name' : data['name']
        }
        id_exists, phone_exists = Person.exists(new_id, data['phone'])
        if not id_exists:
            data['user_id'] = new_id
        else:
            Person.register(data)
        if not phone_exists:
            with app.app_context():
                Database.insert_into_table(Users, data)
                if data['user_type'].upper() != 'ADMIN':
                    Database.insert_into_table(Accounts, account_data)
            return new_id
        else:
            return 'phone already Registered!'

    @staticmethod
    def get_profile_info(user_id):
        with app.app_context():
            user = Database.find_one_from_table(
                table = Users,
                keys = dict(
                    user_id = user_id
                )
            )
        return user

    @staticmethod
    def get_account_info(keys):
        with app.app_context():
            account = Database.find_one_from_table(
                table = Accounts,
                keys = keys
            )
        return account

    @staticmethod
    def get_all_users(user):
        if user.user_type.upper() == 'ADMIN':
            with app.app_context():
                users = Database.find_many_from_table(
                    table = Users,
                    keys = {}
                )
            return users
        else:
            return []

    @staticmethod
    def make_payment(data, user_id, pin):
        pin = hashlib.md5(pin.encode('utf-8')).hexdigest()
        with app.app_context():
            recipient_account = Database.find_one_from_table(
                Accounts,
                keys = {
                    'account_number' : data['account_number']
                }
            )
            user = Database.find_one_from_table(
                table = Users,
                keys = dict(
                    user_id = user_id,
                    pin = pin
                )
            )
            user_account = Database.find_one_from_table(
                table = Accounts,
                keys = dict(
                    user_id = user.user_id
                )
            )
            Database.update_table(
                table = Accounts,
                keys = dict(
                    user_id = user.user_id
                ),
                updates = dict(
                    account_balance = float(user_account.account_balance - float(data['amount']))
                )
            )
            Database.update_table(
                table = Accounts,
                keys = dict(
                    user_id = recipient_account.user_id
                ),
                updates = dict(
                    account_balance = float(recipient_account.account_balance) + float(data['amount'])
                )
            )
            Database.insert_into_table(
                table = Transactions,
                data = dict(
                    sender = user.user_id,
                    recipient = recipient_account.user_id,
                    amount = data['amount'],
                    timeline = data['date'] + '#' + data['time'],
                    remark = data['remark']
                )
            )

    @staticmethod
    def FundWallet(user, data):
        if user.user_type.upper() == 'ADMIN':
            with app.app_context():
                recipient_account = Database.find_one_from_table(
                    table = Accounts,
                    keys = dict(
                        account_number = data['account_number']
                    )
                )
                Database.update_table(
                    table = Accounts,
                    keys = dict(
                        account_number = data['account_number']
                    ),
                    updates = dict(
                        account_balance = float(recipient_account.account_balance) + float(data['amount'])
                    )
                )
                Database.insert_into_table(
                    table = Depositions,
                    data = dict(
                        user_id = recipient_account.user_id,
                        amount = data['amount'],
                        account_id = recipient_account.account_id,
                        timeline = data['date'] + '#' + data['time']
                    )
                )
        else:
            pass

    @staticmethod
    def request_withdrawal(data, user_id):
        user = Person.get_profile_info(user_id)
        with app.app_context():
            user_account = Database.find_one_from_table(
                table = Accounts,
                keys = dict(
                    user_id = user.user_id
                )
            )
            Database.insert_into_table(
                table = Withdrawals,
                data = dict(
                    user_id = user_id,
                    amount = data['amount'],
                    account_id = user.account_id,
                    timeline = data['date'] + '#' + data['time']
                )
            )
            Database.update_table(
                table = Accounts,
                keys = dict(
                    user_id = user.user_id
                ),
                updates = dict(
                    account_balance = float(user_account.account_balance - float(data['amount']))
                )
            )

    @staticmethod
    def approve_withdrawal(_id):
        with app.app_context():
            withdrawal = Database.find_one_from_table(
                table = Withdrawals,
                keys = dict(
                    id = _id
                )
            )
            Database.update_table(
                table = Withdrawals,
                keys = dict(
                    id = _id
                ),
                updates = dict(
                    amount = '~' + withdrawal.amount
                )
            )

    @staticmethod
    def decline_withdrawal(_id):
        with app.app_context():
            withdrawal = Database.find_one_from_table(
                table = Withdrawals,
                keys = dict(
                    id = _id
                )
            )
            user_account = Database.find_one_from_table(
                table = Accounts,
                keys = dict(
                    user_id = withdrawal.user_id
                )
            )
            Database.update_table(
                table = Accounts,
                keys = dict(
                    user_id = withdrawal.user_id
                ),
                updates = dict(
                    account_balance = float(user_account.account_balance) + float(withdrawal.amount)
                )
            )
            Database.remove_from_table(
                table = Withdrawals,
                keys = dict(
                    id = _id
                )
            )
    
    @staticmethod
    def transaction_is_valid(amount, user_id):
        with app.app_context():
            user_account = Database.find_one_from_table(
                table = Accounts,
                keys = dict(
                    user_id = user_id
                )
            )
        
        return float(amount) <= float(user_account.account_balance)

    @staticmethod
    def get_transactions(user_id):
        user = Person.get_profile_info(user_id)
        with app.app_context():
            transactions = Database.find_many_from_table(
                table = Transactions,
                keys = {}
                )
            if user.user_type.upper() != 'ADMIN':                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
                transactions = [
                    transaction for transaction in transactions\
                    if transaction.sender == user_id or\
                    transaction.recipient == user_id
                ]
        return transactions

    @staticmethod
    def get_all_transactions(user):
        if user.user_type.upper() == 'ADMIN':
            with app.app_context():
                transactions = Database.find_many_from_table(
                    table = Transactions,
                    keys = {}
                )
            return transactions
        else:
            pass

    @staticmethod
    def change_pin(user_id, current_pin, new_pin):
        user = Person.get_profile_info(user_id)
        current_pin = hashlib.md5(current_pin.encode('utf-8')).hexdigest()
        new_pin = hashlib.md5(new_pin.encode('utf-8')).hexdigest()
        if user.pin == current_pin:
            with app.app_context():
                Database.update_table(
                    table = Users,
                    keys = dict(
                        user_id = user_id,
                        pin = current_pin
                    ),
                    updates = dict(
                        pin = new_pin
                    )
                )
            return 'done'
        else:
            return 'Incorrect Pin'

    @staticmethod
    def setup_new_pin(user_id, new_pin):
        new_pin = hashlib.md5(new_pin.encode('utf-8')).hexdigest()
        with app.app_context():
            Database.update_table(
                table = Users,
                keys = dict(
                    user_id = user_id
                ),
                updates = dict(
                    pin = new_pin
                )
            )

    @staticmethod
    def get_deposits(user_id):
        user = Person.get_profile_info(user_with_id)
        if user.user_type.upper() != 'ADMIN':
            with app.app_context():
                deposits = Database.find_many_from_table(
                    table = Depositions,
                    key = dict(
                        user_id = user_id
                    )
                )
        else:
            with app.app_context():
                deposits = Database.find_many_from_table(
                    table = Depositions,
                    key = {}
                )
        return deposits