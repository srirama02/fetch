from flask import Flask, jsonify, request
from datetime import datetime
from collections import defaultdict

app = Flask("fetch")

accounts = dict() # maintains each transaction
total = 0
sorted_date_strings = [] # maintains the sorted order of date-time strings
payers = defaultdict(int)  # maintains the total points for each payer

# Function to insert a new date-time string while maintaining the sorted order
def insert_sorted(date_string):
    date = datetime.fromisoformat(date_string)
    for i, existing_date in enumerate(sorted_date_strings):
        if date < datetime.fromisoformat(existing_date):
            sorted_date_strings.insert(i, date_string)
            return
    sorted_date_strings.append(date_string)

# Define a route for creating a new item
@app.route('/add', methods=['POST'])
def add():
    new_item = request.get_json()
    date_string = new_item["timestamp"].replace('Z', '')   
    accounts[date_string] = [new_item["points"], new_item["payer"]]

    insert_sorted(date_string)

    payers[new_item["payer"]] += new_item["points"]
    global total
    total += new_item["points"]

    return "", 200

@app.route('/spend', methods=['POST'])
def spend():
    print(accounts)
    new_item = request.get_json()
    points = new_item["points"]
    global total
    if total < points:
        return jsonify({"message": "Not enough points"}), 400
    total -= points
    idx = 0
    output = list()
    while points:
        if accounts[sorted_date_strings[idx]][0] > points:
            accounts[sorted_date_strings[idx]][0] -= points
            payers[accounts[sorted_date_strings[idx]][1]] -= points
            output.append({"payer" : accounts[sorted_date_strings[idx]][1], "points" : -points})
            points = 0
        else:
            points -= accounts[sorted_date_strings[idx]][0]
            output.append({"payer" : accounts[sorted_date_strings[idx]][1], "points": -accounts[sorted_date_strings[idx]][0]})
            payers[accounts[sorted_date_strings[idx]][1]] -= accounts[sorted_date_strings[idx]][0]
            accounts[sorted_date_strings[idx]][0] = 0
        idx += 1
    return jsonify(output), 200

@app.route('/balance', methods=['GET'])
def get_balance():
    return payers, 200

if __name__ == '__main__':
    app.run(debug=True)
