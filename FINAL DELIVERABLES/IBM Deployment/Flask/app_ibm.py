import numpy as np
from flask import Flask, render_template, request, redirect, jsonify
from markupsafe import escape
import pickle
import inputScript   #inputScript file - to analyze the URL
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

app = Flask(__name__)

# model = pickle.load(open("/home/ana/ana/web-phishing-detection/phishing_website.pkl","rb"))

# user-inputs the URL in this page
@app.route('/')
def predict():
    return render_template("final.html")

#  fetches given URL and passes to inputScript
@app.route('/predict',methods=["POST"])
def y_predict():
    url = request.form['url']
    check_predic = inputScript.main(url)

    payload_scoring = {"input_data": [{"field": 'check_predic', "values": check_predic}]}
    response_scoring = requests.post(os.getenv('DEPLOYMENT_LINK'), json=payload_scoring,headers={'Authorization': 'Bearer ' + mltoken})


    # model = joblib.load('/home/ana/ana/web-phishing-detection/phishing_website.pkl')
    # predic = model.predict(check_predic)

    predic = response_scoring.json()

    result = predic['predictions'][0]['values'][0][0]

    print(result)

    # result = predic[0]
    if(result==-1):
        pred = "You are safe!! This is a Legimate Website :)"
    elif(result==1):
        pred = "You are in a phishing site. Dont Trust :("
    else:
        pred = "You are in a suspecious site. Be Cautious ;("

    return render_template("final.html", pred_text = '{}'.format(pred), url = url)

if __name__ == "__main__":
    app.run(host = '0.0.0.0', debug=True)
