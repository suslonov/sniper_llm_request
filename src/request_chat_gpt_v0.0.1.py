import os
import json
import requests
import pyparsing
from flask import Flask, request, jsonify
from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()  # take environment variables from .env.
except:
    pass

def get_env_variable(key):
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set.")
    return value

# Constants
GOOD_TOKEN_TEMPLATE = "good_template1.sol"
HEADERS = {'Content-Type': "application/json"}
ETHERSCAN_CONTRACT_CODE_REQUEST = "https://api.etherscan.io/api?module=contract&action=getsourcecode&address={}&apikey={}"
WEIGHTS = {"TEMPLATE_WEIGHT": 70, "TAX_CHANGING_FUNCTION": 10, "TAX": 20}
# with open(os.path.expanduser(PARAMETERS_FILE), "r") as f:
#     parameters = json.load(f)

json_questions = {
             "is this token fraudulent or high risk of fraud": "boolean",
             "is it honey pot token": "boolean",
             "initial buy tax constant in the code, exactly": "numeric",
             "initial sell tax constant in the code, exactly": "numeric",
             "final buy tax constant in the code, exactly": "numeric",
             "final sell tax constant in the code, exactly": "numeric",
             "reduce buy tax at constant in the code, exactly": "numeric",
             "reduce sell tax at constant in the code, exactly": "numeric",
             "prevent swap before constant in the code, exactly": "numeric",
             "tax levels changing function name from contract code, exactly": "string",
             "suspicious functions name list from contract code": "string",
             "can owner change balance": "boolean",
             "is trading restricted by block Number": "boolean",
             "max wallet size if available else minus one": "numeric",
             "is there white list of addresses": "boolean",
             "is there black list of addresses": "boolean",
             "is it bot protected": "boolean",
             "description of token your expert opinion": "text",
             "non standard features your expert opinion": "text",
             "unusual trade restrictions your expert opinion": "text",
             "function with non standard behaviour your expert opinion": "text",
             }


openai_key = get_env_variable('CHAT_GPT_KEY')
etherscan_key = get_env_variable('ETHERSCAN_KEY')

commentFilter = pyparsing.cppStyleComment.suppress()

application = Flask(__name__)
application.secret_key = 'random string'

@application.route('/openai', methods = ['POST'])
def process_with_chat_gpt1():
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
   
    messages0 = [
        {"role": "user", "content": "make analysis of the token reading contract code " + source_code_filtered},
        {"role": "user", "content": "possible fraudulent feature: transfering balances is possible for someone else than account owner"},
        {"role": "user", "content": "possible fraudulent feature: unathorized changing or adjusting balances"},
        {"role": "user", "content": "possible fraudulent feature: act in not transparent or obfuscated way"},
        {"role": "user", "content": "fraudulent token features can be implemented in non-standard contract functions"},
        {"role": "user", "content": "high risk of fraud: hidden obstacles for transferring of balances"},
        {"role": "user", "content": "high risk of fraud: a token has non-standard functions changing or adjusting many balances at once"},
        {"role": "user", "content": "\"tax\" in this context means the fee collected buy a smart contract from token transfers"},
        {"role": "user", "content": "a standard ERC-20 token contract is not fraudulent, focus on non-standard features"},
        {"role": "user", "content": "taxes, a possibility of tax management, and manual function of changing the contract own balance are not fraudulent"},
        {"role": "user", "content": "provide detailed explanation in text fields, " +
              "give all suspicious things"},
        {"role": "user", "content": "respond as json " + json.dumps(json_questions)},
        ]

    all_content = ""
    for m in messages0:
        all_content = all_content + "\n" + m["content"]
    messages = [{"role": "user", "content": all_content}]
    
    return jsonify(request_chat_gpt(openai_key, messages)), 200


@application.route('/openaitemplate', methods = ['POST'])
def process_with_chat_gpt2():
    request_json = request.get_json()

    if not 'tokenAddress' in request_json:
        return request_json, 400
    request_token = request_json["tokenAddress"]
    request_token_name = "NEWTOKEN"

    template_token_name = "GOODTOKEN"
    with open(GOOD_TOKEN_TEMPLATE, 'r') as f:
        source_code_template = f.read()
    
    res = requests.get(ETHERSCAN_CONTRACT_CODE_REQUEST.format(request_token, etherscan_key), headers=HEADERS)
    if not res.status_code == 200:
        return res.text, 400
    try:
        d = res.json()
        source_code = d["result"][0]["SourceCode"]
    except:
        return res.text, 400
    
    if len(source_code) < 20:
        return res.text, 400

    source_code_filtered = commentFilter.transformString(source_code)
    source_code_list0 = source_code_filtered.split("\n")
    source_code_list1 = sum([s.split("\\n") for s in source_code_list0 if len(s) > 0], [])
    source_code_filtered = "".join([s.strip() + "\n" for s in source_code_list1 if len(s.strip()) > 0])
   
    messages0 = [
        {"role": "user", "content": "compare two following token contracts"},
        {"role": "user", "content": template_token_name + " token is " + source_code_template},
        {"role": "user", "content": "make analysis of the token reading contract code " + source_code_filtered},
        {"role": "user", "content": "possible fraudulent feature: transfering balances is possible for someone else than account owner"},
        {"role": "user", "content": "possible fraudulent feature: unathorized changing or adjusting balances"},
        {"role": "user", "content": "possible fraudulent feature: act in not transparent or obfuscated way"},
        {"role": "user", "content": "fraudulent token features can be implemented in non-standard contract functions"},
        {"role": "user", "content": "high risk of fraud: hidden obstacles for transferring of balances"},
        {"role": "user", "content": "high risk of fraud: a token has non-standard functions changing or adjusting many balances at once"},
        {"role": "user", "content": "\"tax\" in this context means the fee collected buy a smart contract from token transfers"},
        {"role": "user", "content": "a standard ERC-20 token contract is not fraudulent, focus on non-standard features"},
        {"role": "user", "content": "taxes, a possibility of tax management, and manual function of changing the contract own balance are not fraudulent"},
        {"role": "user", "content": "provide detailed explanation in text fields, " +
              "give all suspicious things"},
        {"role": "user", "content": "respond as json " + json.dumps(json_questions)},
        ]

    all_content = ""
    for m in messages0:
        all_content = all_content + "\n" + m["content"]
    messages = [{"role": "user", "content": all_content}]

    return jsonify(request_chat_gpt(openai_key, messages)), 200

@application.route('/')

def ping():

    return 'Pong'


def request_chat_gpt(openai_key, messages):

    client = OpenAI(api_key=openai_key)
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo-1106",
      temperature=0,
        response_format={ "type": "json_object" },
      # max_tokens=parameters["MAX_TOKENS"],
      messages=messages)

    try:
        result = json.loads(completion.choices[0].message.content)
        result["isMaliciousToken"] = result.get("is this token fraudulent or high risk of fraud", False)
    except:
        return "incorrect chatGPT response " + completion.choices[0].message.content, 500
    
    # if result["maliciousToken"]:
    #     result["tokenGrade"] = 0
    # else:
    #     grade = 0
    #     grade += result["tokenLikeness"] * WEIGHTS["TEMPLATE_WEIGHT"]
    #     grade += (1 if result["taxChangingFunction"] is None else 0) * WEIGHTS["TAX_CHANGING_FUNCTION"]
    #     grade -= ((0 if result["initialBuyTax"] is None else result["initialBuyTax"]) / WEIGHTS["TAX"]
    #               + (0 if result["initialSellTax"] is None else result["initialSellTax"]) / WEIGHTS["TAX"]) / WEIGHTS["TAX"] * WEIGHTS["TAX"]

    #     result["tokenGrade"] = grade / sum([WEIGHTS[w] for w in WEIGHTS])
    
    return result

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=3000)
