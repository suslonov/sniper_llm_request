import os
import json
import requests
import pyparsing
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

def get_env_variable(key):
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set.")
    return value

# Constants
HEADERS = {'Content-Type': "application/json"}
ETHERSCAN_CONTRACT_CODE_REQUEST = "https://api.etherscan.io/api?module=contract&action=getsourcecode&address={}&apikey={}"

# with open(os.path.expanduser(PARAMETERS_FILE), "r") as f:
#     parameters = json.load(f)

openai_key = get_env_variable('CHAT_GPT_KEY')
etherscan_key = get_env_variable('ETHERSCAN_KEY')

commentFilter = pyparsing.cppStyleComment.suppress()
client = OpenAI(api_key=openai_key)

application = Flask(__name__)
application.secret_key = 'random string'

@application.route('/openai', methods = ['POST'])
def request_chat_gpt():
    request_json = request.get_json()

    if not 'tokenAddress' in request_json:
        return request_json, 400
    request_token = request_json["tokenAddress"]
    
    res = requests.get(ETHERSCAN_CONTRACT_CODE_REQUEST.format(request_token, etherscan_key), headers=HEADERS)
    if not res.status_code == 200:
        return res.text, 400
    try:
        d = res.json()
        source_code = d["result"][0]["SourceCode"]
    except:
        return res.text, 400
    
    source_code_filtered = commentFilter.transformString(source_code)
    source_code_list0 = source_code_filtered.split("\n")
    source_code_list1 = sum([s.split("\\n") for s in source_code_list0 if len(s) > 0], [])
    source_code_filtered = "".join([s.strip() + "\n" for s in source_code_list1 if len(s.strip()) > 0])
   
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        temperature=0,
        # max_tokens=parameters["MAX_TOKENS"],
        messages=[
            {"role": "user", "content": source_code_filtered},
            # {"role": "user", "content": "make a detailed resume of this smart contract according to what you know about Solidity contracts"},
            {"role": "user", "content": "and make me JSON with all the names and values of Solidity variables related to the buying tax and the selling tax from the contract code given"},
            {"role": "user", "content": "add to the JSON the name only of a function changing any of these variables after the contract creation if it exists in the contract code given"},
            {"role": "user", "content": "a malicious token typically tries to transfer my tokens to the contract owner wallet using malicious transfer, transferFrom or approve function"},
            {"role": "user", "content": "also malicious token can set fee to be a lion's share of approved tokens in the approve function. Is this token malicious?"},
            # {"role": "user", "content": '"gradeToken" field evaluates is the token OK to buy as an floating value from 0 to 100'},
            {"role": "user", "content": 'fields for JSON shoud be: "initialBuyTax", "initialSellTax", "finalBuyTax", "finalSellTax", "reduceBuyTaxAt", "reduceSellTaxAt", "preventSwapBefore", "taxChangingFunction", "maliciousToken", "descriptionOfToken"'},
            {"role": "user", "content": 'return all the response as a one JSON statement'},
        ]
    )
    
    try:
        result = json.loads(completion.choices[0].message.content)
    except:
        return "incorrect chatGPT response " + completion.choices[0].message.content, 500
    result["tokenGrade"] = 100
    
    return jsonify(result), 200

if __name__ == "__main__":
    application.run(port=3000)
