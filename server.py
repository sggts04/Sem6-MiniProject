import json
from flask import Flask, jsonify, abort, make_response, request, url_for,session
from flask import render_template, redirect
from web3 import Web3
import requests

rpc = "http://127.0.0.1:7545/"
aadhar_addr = "http://localhost:3002/"

web3 = Web3(Web3.HTTPProvider(rpc))
abi = """[
	{
		"constant": false,
		"inputs": [
			{
				"name": "_candidateId",
				"type": "uint256"
			}
		],
		"name": "vote",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "candidatesCount",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"name": "candidates",
		"outputs": [
			{
				"name": "id",
				"type": "uint256"
			},
			{
				"name": "name",
				"type": "string"
			},
			{
				"name": "voteCount",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "end",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"name": "_candidateId",
				"type": "uint256"
			}
		],
		"name": "votedEvent",
		"type": "event"
	}
]"""
contract_addr = "0x89C145Bb2F26a70849B305Fd36e673c50D184F6d"


app = Flask(__name__)
app.secret_key = 'Xsa/#f394hf*k;dj5n'

adminAccount = '0xa7EA8cc3dEfdF1ab4f341488156fDd176Bb70D17'
adminPrivateKey = '7a75502f25450ad73f367d4318716d4b9eb80ab3af02da56e3b256de1dafdd7e'

vote_tx = []
voted = []
ended = 0

@app.route("/start", methods=['GET'])
def start():
    freshAdminAccount = web3.eth.account.create()
    adminAccount = freshAdminAccount.address
    adminPrivateKey = freshAdminAccount.privateKey
    print(adminAccount, adminPrivateKey)
    return "ok", 200

@app.route("/", methods=['POST'])
def home():
    if(not ended):
        try:
            data = json.loads(request.data) # {"aadhaarID":int(),"candidateID":int()}
            print(data)
            aid = data["aadhaarID"]
            if(aid in voted):
                return "Already voted", 400
            cid = int(data["candidateID"])
            print(cid)
            contract = web3.eth.contract(address=contract_addr, abi=abi)
            print(contract)
            transaction = contract.functions.vote(cid).buildTransaction({
                "gasPrice": web3.eth.gas_price,
                "from": adminAccount, 
                "nonce": web3.eth.getTransactionCount(adminAccount), 
            })
            print('tx', transaction)
            signed_tx = web3.eth.account.signTransaction(transaction, adminPrivateKey)
            print('signed tx', signed_tx)
            tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print('tx hash', tx_hash)
            vote_tx.append(tx_hash)
            voted.append(aid)
            return "Vote successfully casted", 200
        except Exception as e:
            print(e)
            return "Error processing", 500
    else:
        return "Election period ended", 400

@app.route("/results" , methods=['GET'])
def count():
    if(ended):
        res = []
        election = web3.eth.contract(address=contract_addr, abi=abi)
        for i in range(election.caller().candidatesCount()):    
            res.append(election.caller().candidates(i+1))
        return json.dumps(res),200
    else:
        return "Election still on going",400

@app.route("/end" , methods=['GET'])
def end_election():
    global ended
    ended += 1
    contract = web3.eth.contract(address=contract_addr, abi=abi)
    transaction  = contract.functions.end().buildTransaction({
        "gasPrice": web3.eth.gas_price,
        "from": adminAccount, 
        "nonce": web3.eth.getTransactionCount(adminAccount), 
    })

    signed_tx = web3.eth.account.signTransaction(transaction, adminPrivateKey)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return "Election successfully ended\nTx Hash : %s"%(str(tx_hash)),200

@app.route("/verify_aadhar", methods=['POST'])
def verify_aadhar(): 
    # TODO: create a mock aadhar api
    try:
        data = json.loads(request.data)
        print(data)
        resp = requests.post(aadhar_addr + 'verify', {'aadhar': data['aadhaarID']})
        if resp.status_code == 200:
            resu = json.loads(resp.text)
            resu['verified'] = True
            return json.dumps(resu), 200
        else:
            return json.dumps({'verified': False}), 200
    except:
        return "Error processing", 500

@app.route("/isended", methods=['GET'])
def isended(): 
    return str(ended>0), 200

@app.route("/candidates_list", methods=['GET'])
def candidates_list():
    try:
        res = []
        election = web3.eth.contract(address=contract_addr, abi=abi)
        for i in range(election.caller().candidatesCount()):    
            res.append(election.caller().candidates(i+1)[1]) #name
        return json.dumps(res), 200
    except:
        return "Error processing", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3001, debug = True)