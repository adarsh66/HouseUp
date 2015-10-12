__author__ = 'adarsh'

''' Following code was taken from Open Bank Project Python implementation
    It was then further edited on for the Hack Make The Bank Hackathon
    Date: 2015-10-10
    Project Name: myMortgage (provisional)
'''
# -*- coding: utf-8 -*-
from requests_oauthlib import OAuth1Session
import json
# oauth flow in simple words: http://pyoauth.readthedocs.org/en/latest/guides/oauth1.html

client_key = "c3505leozqekhdgjmncq5dsbftf3jaww2orqztvl"
client_secret = "qx1gcn0dkm5lm0rt2msz1x3pnmi21ocfywfznvzi"

base_url = "https://rbs.openbankproject.com"
request_token_url = base_url + "/oauth/initiate"
authorization_base_url = base_url + "/oauth/authorize"
access_token_url = base_url + "/oauth/token"
openbank = OAuth1Session(client_key, client_secret=client_secret, callback_uri='https://rbs.openbankproject.com')

openbank.fetch_request_token(request_token_url)

authorization_url = openbank.authorization_url(authorization_base_url)
print 'Please go here and authorize, '
print authorization_url

redirect_response = raw_input('Paste the full redirect URL here:')
openbank.parse_authorization_response(redirect_response)

openbank.fetch_access_token(access_token_url)

our_bank = "rbs-rbs-a"

print "Get owner accounts"
r = openbank.get(u"{}/obp/v1.2.1/banks/{}/accounts/private".format(base_url,
    our_bank), headers= {'obp_limit': '25'})
print r.json()
accounts = r.json()['accounts']
for a in accounts:
    if 'id' in a:
        print a['id']

#just picking first account
our_account = accounts[3]['id']

print "Get owner transactions"
r = openbank.get(u"{}/obp/v1.2.1/banks/{}/accounts/{}/owner/transactions".format(base_url,
    our_bank,
    our_account), headers= {'obp_limit': '25'})

if 'transactions' in r.json():
    transactions = r.json()['transactions']
    print "Got {} transactions".format(len(transactions))

print r
print r.json()
myjson = r.json()
for i,tagval in [(0,'Discretionary'), (1,'Basic'), (2,'Rent'), (3,'Salary')]:
    myjson['transactions'][i]['metadata']['tags'] = tagval

with open(our_account + '.json', 'w') as outfile:
    json.dump(myjson, outfile)

'''
print "Transfer some money"
send_to = {"bank": "rbs-rbs-a", "account": "111111"}
payload = '{"account_id": "' + send_to['account'] +'", "bank_id": "' + send_to['bank'] + '", "amount": "700", ' \
                                                                                         '"metadata": {"tags":["Discretionary"] } }'
headers = {'content-type': 'application/json'}
r = openbank.post(u"{}/obp/v1.2.1/banks/{}/accounts/{}/owner/transactions".format(base_url,
    our_bank, our_account), data=payload, headers=headers)
'''

trans_id_to_update = '50a1ed3b-df62-4d11-a84d-91aea13d94d7'
print r
print r.json()
