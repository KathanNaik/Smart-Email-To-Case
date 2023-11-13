import json
import openai

from flask import Flask, redirect, url_for, request, Response
from flask_mail import Mail, Message 

app = Flask(__name__)

@app.route("/")
def home():
    return 'Kathan Here!'

f = open("email_cred.json", "r")

cred = json.load(f)

email_address = cred.get("email_address")
email_password = cred.get("email_password")

print(cred);

app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = email_address
app.config['MAIL_PASSWORD'] = email_password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

f = open("key.txt", "r")

openai.api_key = f.readline()
openai.api_base = "https://api.pulze.ai/v1"

f.close()

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
5) you can keep fields empty by putting 'NULL' if you do not find any of them'''

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

def pulze_llm_p(mail, list):
    
    listMsg = (
        '''Given is the list of product name and their description separated by an equal to/= sign'''
            
        + list + 
            
        '''
        1) Your task is to figure out if the user has mentioned any of the products in their message.
        2) Return the name of the product in JSON format as below:
        {
            "product": "the product" 
        }
        4) Strictly include only one product name given in the list as the product.
        3) You can keep fields empty by putting 'NULL' if you do not find any of them.
        '''
    )
    
    chat_response = openai.ChatCompletion.create(
        
        model="pulze-v0",
        max_tokens=100,
        messages=[
            {"role": "system", "content": listMsg},
            {"role": "user", "content": mail}
        ],
    )

    print(chat_response)
    return chat_response.choices[0].message.content

@app.route("/mailpost", methods=["POST"])
def signatureParsing():
    if request.method == "POST":
        user_address = request.form["address"]
        user_email = request.form["email"]
        access_password = request.form["password"]
        
        if(access_password == "Aethereus@123"):
            msg = Message( 
                'Email-Conformation', 
                sender = email_address, 
                recipients = [user_address] 
               ) 
            msg.body = 'A case has been raised based on your email and our team will be contacting you soon. Thank you for reaching out!'
            mail.send(msg) 
            
            r = Response(response=pulze_llm(user_email), status=200, mimetype="application/json")
            r.headers["Content-Type"] = "application/json; charset=utf-8"
            return r
        else:
            return "invalid request"
        
@app.route("/product", methods=["POST"])
def productParsing():
    if request.method == "POST":
        user_email = request.form["email"]
        product_list = request.form["products"]
        access_password = request.form["password"]
        
        if(access_password == "Aethereus@123"):
            
            r = Response(response=pulze_llm_p(user_email, product_list), status=200, mimetype="application/json")
            r.headers["Content-Type"] = "application/json; charset=utf-8"
            return r
        else:
            return "invalid request"
        
if __name__ == "__main__":
    app.run(host="localhost", port=8080)