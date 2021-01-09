#!/usr/bin/python3

import asyncio
import os
import time

import aiohttp
import json
import requests
from flask import Flask, request, redirect, Response, render_template, jsonify, abort
from flask import send_from_directory
from datetime import datetime

from functions.database import insertToken, getRefreshToken, updateToken, lookupDestinyID
from static.config import BUNGIE_TOKEN, B64_SECRET, NEWTONS_WEBHOOK

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from nacl.encoding import HexEncoder
from static.config import BOT_ACCOUNT_PUBLIC_KEY

verify_key = VerifyKey(bytes.fromhex(BOT_ACCOUNT_PUBLIC_KEY))

async def refresh_token(discordID):
    url = 'https://www.bungie.net/platform/app/oauth/token/'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'authorization': 'Basic ' + str(B64_SECRET)
    }
    refresh_token = getRefreshToken(discordID)
    destinyID = lookupDestinyID(discordID)
    if not refresh_token:
        return None

    data = {"grant_type":"refresh_token", "refresh_token": str(refresh_token)}

    async with aiohttp.ClientSession() as session:
        for i in range(5):
            t = int(time.time())
            async with session.post(url, data=data, headers=headers, allow_redirects=False) as r:
                if r.status == 200:
                    data = await r.json()
                    access_token = data['access_token']
                    refresh_token = data['refresh_token']
                    token_expiry = t + data['expires_in']
                    refresh_token_expiry = t + data['refresh_expires_in']
                    updateToken(destinyID, discordID, access_token, refresh_token, token_expiry, refresh_token_expiry)
                    return access_token
                else:
                    print(f"Refreshing Token failed with code {r.status} . Waiting 1s and trying again")
                    print(await r.read(), '\n')
                    await asyncio.sleep(1)

    print(f"Refreshing Token failed with code {r.status}. Failed 5 times, aborting")
    return None


########################################## FLASK STUFF ##################################################
app = Flask(__name__)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/test')
def test():
    print('testing')
    return "hi"

@app.route('/level1')
@app.route('/level1/<highscore>')
def level1():
    highscore = request.cookies.get('userHighscore')
    return render_template('level1.html', highscore=highscore)

@app.route('/')
def root():
    response = request.args
    if not (code := response.get('code', None)): #for user auth
        return '''
<img src="https://vignette.wikia.nocookie.net/meme/images/a/a8/Portal-cake.jpg/revision/latest/top-crop/width/360/height/450?cb=20110913215856"/><br/>
<a href="https://elevatorbot.ch/vendorbounties">Vendorbounties</a><br/>
<a href="https://elevatorbot.ch/fireteamstalker">Fireteamstalker</a><br/>
<a href="https://elevatorbot.ch/descendadmintool">Descend Members</a><br/>
'''
    (discordID,serverID) = response['state'].split(':') #mine

    url = 'https://www.bungie.net/platform/app/oauth/token/'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'authorization': 'Basic '+ str(B64_SECRET) #unqiue to this app
    }

    data = f'grant_type=authorization_code&code={code}'

    t = int(time.time())
    r = requests.post(url, data=data, headers=headers)
    authresponse = r.json()
    access_token = authresponse['access_token']
    refresh_token = authresponse['refresh_token']
    token_expiry = t + authresponse['expires_in']
    refresh_token_expiry = t + authresponse['refresh_expires_in']

    reqParams = {
        'Authorization': 'Bearer ' + str(access_token),
        'X-API-Key': BUNGIE_TOKEN
    }
    
    r = requests.get(url='https://www.bungie.net/platform/User/GetMembershipsForCurrentUser/', headers=reqParams)
    response = r.json()['Response']
    membershiplist = response['destinyMemberships']

    primarymembership = None
    display_name = '_missing_'
    for membership in membershiplist:
        if int(membership["membershipType"]) == 3:
            display_name = membership["displayName"]
            steam_name = membership["LastSeenDisplayName"]
        if "crossSaveOverride" in membership.keys() and membership["crossSaveOverride"] and membership["membershipType"] != membership["crossSaveOverride"]:
            #the primary membership has been identified
            continue
        primarymembership = membership
    
    if not primarymembership:
        print(f'no primary membership found for {display_name} aka {discordID} in server {serverID}')

    destinyID = int(primarymembership['membershipId'])
    systemID = int(primarymembership['membershipType'])

    insertToken(int(discordID), destinyID, systemID, int(serverID), access_token, refresh_token, token_expiry, refresh_token_expiry)
    print(f"Inserted token. <@{discordID}> has destinyID `{destinyID}`, Bungie-Name `{display_name}`, Steam-Name `{steam_name}`")
    webhookURL = NEWTONS_WEBHOOK
    requestdata = {
        'content': f"<@{discordID}> has destinyID `{destinyID}`, Bungie-Name `{display_name}`, Steam-Name `{steam_name}`, System `{systemID}`",
        'username': 'EscalatorBot',
        "allowed_mentions": {
            "parse": ["users"],
            "users": []
        },
    }
    rp = requests.post(url=webhookURL, data=json.dumps(requestdata), headers={"Content-Type": "application/json"})
    return '''
        Thank you for signing up with <h1> Elevator Bot </h1>\n <p style="bottom: 20" >There will be cake</p>
        <script>
            setTimeout("location.href = 'https://www.elevatorbot.ch';",1500);
        </script>
    '''



@app.route('/.well-known/acme-challenge/<challenge>')
def letsencrypt_check(challenge):
    challenge_response = {
        "<some_challenge_token>":"<challenge_response>",
        "<other_challenge_token>":"<challenge_response>"
    }
    return Response(challenge_response[challenge], mimetype='text/plain')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/elevatorgateway/', methods=['POST'])
def elevatorgateway():
    signature = request.headers["X-Signature-Ed25519"]
    timestamp = request.headers["X-Signature-Timestamp"]
    body = request.data
    
    try:
        verify_key.verify(timestamp.encode() + body, bytes.fromhex(signature))
    except BadSignatureError:
        abort(401, 'invalid request signature') #https://i.imgflip.com/48ybrs.jpg
        return


    if request.json["type"] == 1: #responding to discords pings
        return jsonify({
            "type": 1 
        })
    
    else: #https://discord.com/developers/docs/interactions/slash-commands -> responding to an interaction
        print(request.json['data'])
        data = request.json['data']
        if data['name'] == 'lenny': #check name of command
            if 'options' in request.json['data'].keys() and request.json['data']['options'][0]['value'] > 0:
                return jsonify({
                    "type": 4,
                    "data": {
                        "tts": False,
                        "content": "( ͡° ͜ʖ ͡°)" * request.json['data']['options'][0]['value'],
                        "embeds": [],
                        "allowed_mentions": []
                    }
                })
            else:
                return jsonify({
                    "type": 4,
                    "data": {
                        "tts": False,
                        "content": "( ͡° ͜ʖ ͡°)",
                        "embeds": [],
                        "allowed_mentions": []
                    }
                })
        elif data['name'] == 'newCommand':
            pass
        else:
            return jsonify({
                    "type": 4,
                    "data": {
                        "tts": False,
                        "content": "Command not implemented",
                        "embeds": [],
                        "allowed_mentions": []
                    }
                })

@app.before_request
def before_request():
    if request.url.startswith('http://'):
        return redirect(request.url.replace('http://', 'https://'), code=301)
    pass


@app.errorhandler(404)
def not_found(e):
    """Page not found."""
    return "page not founderino"

if __name__ == '__main__':
    print('server running')
    app.run(host= '0.0.0.0')


