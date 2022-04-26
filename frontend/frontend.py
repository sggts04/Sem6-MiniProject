from flask import Flask, render_template, flash, request, session, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import requests
import json

backend_addr = "http://localhost:3001/"

app = Flask(__name__)
app.secret_key = '1IskOP2%1n^p)oY' 

@app.route("/", methods=['GET', 'POST'])
def home():
    return redirect(url_for('verify'))

@app.route("/results", methods=['GET'])
def results():
    try:
        resp = requests.get(backend_addr+'results')
        if(resp.status_code!=200):
            return render_template('confirmation.html',message=resp.text),resp.status_code
        result = json.loads(resp.text)
        print(result)
        result.sort(reverse=True,key=lambda x: x[2])
        return render_template('results.html',result=result)
    except:
        return render_template('confirmation.html',message="Error processing"),500
    
@app.route("/verify", methods=['GET', 'POST'])
def verify():
    try:
        resp = requests.get(backend_addr+'isended')
        if(not eval(resp.text)):
            if request.method == 'POST':
                aid = request.form['aid']
                bio = request.form['biometric']
                resp = requests.post(backend_addr + 'verify_aadhar', json.dumps({'aadhaarID': aid}))
                resu = json.loads(resp.text)
                if(bio == 'yes' and resu['verified']):
                    session['verified'] = True
                    session['aid'] = aid
                    session['name'] = resu['name']
                    return redirect(url_for('vote'))
            return render_template('verification.html')
        else:
            return render_template('confirmation.html', message="Election ended", code=400), 400
    except Exception as e:
        print(e)
        return render_template('confirmation.html', message="Error processing"), 500

@app.route("/vote", methods=['GET', 'POST'])
def vote():
    resp = requests.get(backend_addr + 'isended')
    if(not eval(resp.text)):
        if('verified' in session):
            resp = requests.get(backend_addr + 'candidates_list')
            candidates = eval(resp.text)
            print(candidates)
            candidates1 = candidates[:int(len(candidates)/2)]
            candidates2 = candidates[int(len(candidates)/2):]
            if request.method == 'POST':
                aid = session['aid']
                session.pop('verified')
                session.pop('aid')
                session.pop('name')
                candidate = request.form['candidate']
                cid = candidates.index(candidate)+1
                print(cid)
                resp = requests.post(backend_addr, json.dumps({'aadhaarID':aid, 'candidateID':cid}))
                print(resp)
                return render_template('confirmation.html', message = resp.text, code = resp.status_code), resp.status_code
            return render_template('vote.html', candidates1 = candidates1, candidates2 = candidates2, name = session['name']), 200
        else:
            return redirect(url_for('verify'))
    else:
        return render_template('confirmation.html', message="Election ended", code = 400),400
    
if __name__ == '__main__':
	app.run(host="0.0.0.0", port=3000, debug = True)