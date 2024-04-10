from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask('Bank Deposit')

connc_URI = 'mongodb+srv://alisu1772018:1234@cluster0.efqhnd3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

client = MongoClient(connc_URI)
db = client['transactionmanagement'] 
user_collection = db['users']
transaction_collection = db['transactions']

#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = user_collection.find_one({'username': username})
        if(user == None):
            return redirect (url_for('signup'))
        if user['username'] == username and user['password'] == password:
            return redirect(url_for('index'))
        elif user == None:
            return redirect(url_for('signup'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')

#signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        mobile_number = request.form['mobile_number']

        #logic for adding that user and validating
        user = user_collection.find_one({'username': request.form['username']})
        if user:
            return redirect(url_for('login'))
        else:
            if password == confirm_password and len(mobile_number) == 10:
                user_collection.insert_one({'username': username, 'password': password, 'email': email, 'mobile_number': mobile_number})
                return redirect(url_for('login'))
            else:
                error = {'errType': '','msg': ''}
                
                if(password != confirm_password):
                    error = {
                        'errType': 'password',
                        'msg': 'Passwords do not match'
                    }
                else:
                    error = {
                        'errType': 'mobile',
                        'msg': 'Please enter correct mobile number'
                    }
                    
                return render_template('signup.html', error=error)

#home
@app.route('/')
def index():
    return render_template('index.html')

#transactions for posting
@app.route('/transaction', methods=['POST', 'GET'])
def transaction():
    if request.method == 'GET':
        return redirect(url_for('login'))
    else:
        transaction_type = request.form['transaction_type']
        amount = int(request.form['amount'])
        newTransaction = {
            'transactionType': transaction_type,
            'amount': amount
        }

        if(transaction_type == 'withdraw'):
            total_deposit = transaction_collection.aggregate([
                {"$match": {"transactionType": "deposit"}},
                {"$group": {"_id": None, "total_deposit": {"$sum": "$amount"}}}
            ])

            total_withdrawl = transaction_collection.aggregate([
                {"$match": {"transactionType": "withdraw"}},
                {"$group": {"_id": None, "total_withdraw": {"$sum": "$amount"}}}
            ])

            total_deposit = list(total_deposit)
            total_withdrawl = list(total_withdrawl)

            available_balance = total_deposit[0]['total_deposit'] - total_withdrawl[0]['total_withdraw']

            if available_balance >= amount:
                transaction_collection.insert_one(newTransaction)
                return redirect(url_for('index'))
            else:
                print('Not enough balance')
                return redirect(url_for('index'))
        else:
            transaction_collection.insert_one(newTransaction)
            return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)