#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests

URL = "http://localhost:3000/openai"
HEADERS = {'Content-Type': "application/json"}

tokens = {}
def add_token_to_compare_dict(name, address):
    tokens[name] = address

add_token_to_compare_dict("KERMIT", "0x7f13cc695185a06f3db199557024acb2f5a4ef95")
add_token_to_compare_dict("ELONGATE", "0xcC6c4F450f1d4aeC71C46f240a6bD50c4E556B8A")
add_token_to_compare_dict("squid_game", "0x561Cf9121E89926c27FA1cfC78dFcC4C422937a4")
add_token_to_compare_dict("DAI", "0x6B175474E89094C44Da98b954EedeAC495271d0F")
add_token_to_compare_dict("METAMOONMARS", "0x8ed9C7E4D8DfE480584CC7EF45742ac302bA27D7")
add_token_to_compare_dict("CHUGJUG", "0xb9065690dc79ea0e59b8567ba7823608d5739474")
add_token_to_compare_dict("COTI", "0xDDB3422497E61e13543BeA06989C0789117555c5")
add_token_to_compare_dict("cyb3rgam3r420_Gamer", "0xf89674f18309a2e97843c6e9b19c07c22caef6d5")
add_token_to_compare_dict("FAKE_CHAINLINK", "0x849569f2e27c4ff3e8c148cb896cd944f28a6f63")
add_token_to_compare_dict("CHAINLINK", "0x514910771AF9Ca656af840dff83E8264EcF986CA")
add_token_to_compare_dict("MEMEAI", "0x6D2d8D9A13A9F5ab4B2CD7ae982C2A22e029500A")
add_token_to_compare_dict("DRAKE", "0x288334E049fB3C7950E56E41FE4F24cDce72290c")

data = {"tokenAddress": tokens["MEMEAI"]}
res = requests.post(URL, headers=HEADERS, data=json.dumps(data))
print(res.status_code)
try:
    print(res.json())
except:
    print(res.text)
