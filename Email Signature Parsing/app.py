import json
import openai

from flask import Flask, redirect, url_for, request, Response
from flask_mail import Mail, Message 

app = Flask(__name__)

@app.route("/")
def home():
    return 'Kathan Here!'

#Email Credentials
f = open("email_cred.json", "r")

cred = json.load(f)

email_address = cred.get("email_address")
email_password = cred.get("email_password")

print(cred);

#Email Config
app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = email_address
app.config['MAIL_PASSWORD'] = email_password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

#Reading Key
f = open("key.txt", "r")

openai.api_key = f.readline()
openai.api_base = "https://api.pulze.ai/v1"

f.close()

#Defining System Msg
instructiones = '''User will give an email text as message content. Your task is to retrive email signature from that email. You should follow below steps 
1) figure out the name of person sending the mail
2) find the name of the organization or company the person belongs to if mentioned any
3) check if there is an mobile number the person writing email might have given
4) return the response message content in JSON like format as below
    {
        "name": "name that you have figured out"
        "org": "organization/company"
        "number": mobile number found
    }
5) you can keep fields empty by putting 'Null' if you do not find any of them'''

#Pulze API call
def pulze_llm(mail):
    chat_response = openai.ChatCompletion.create(
        model="pulze-v0",
        max_tokens=100,
        messages=[
            {"role": "system", "content": instructiones},
            {"role": "user", "content": mail}
        ],
    )

    print(chat_response)
    return chat_response.choices[0].message.content

#Request Processing
@app.route("/mailpost", methods=["POST"])
def login():
    if request.method == "POST":
        user_address = request.form["address"]
        user_email = request.form["email"]
        access_password = request.form["password"]
        
        if(access_password == "Aethereus@123"):
            msg = Message( 
                'Hello', 
                sender ='kathan.naik@aethereus.com', 
                recipients = [user_address] 
               ) 
            msg.body = 'Hello Flask message sent from Flask-Mail'
            mail.send(msg) 
            
            r = Response(response=pulze_llm(user_email), status=200, mimetype="application/json")
            r.headers["Content-Type"] = "application/json; charset=utf-8"
            return r
        else:
            return "invalid request"
        
        if __name__ == "__main__":
    app.run(host="localhost", port=8080)