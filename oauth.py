#!/usr/bin/python3

import requests, json
from static.config      import BUNGIE_OAUTH, BUNGIE_TOKEN, BUNGIE_SECRET, B64_SECRET, NEWTONS_WEBHOOK
from flask              import Flask, request, redirect, Response, send_file
from functions.database import insertToken, getRefreshToken

def refresh_token(discordID):
    url = 'https://www.bungie.net/platform/app/oauth/token/'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'authorization': 'Basic ' + str(B64_SECRET)
    }
    refresh_token = getRefreshToken(discordID)

    data = 'grant_type=refresh_token&refresh_token=' +str(refresh_token)

    r = requests.post(url, data=data, headers=headers, allow_redirects=False)
    data = r.json()
    access_token = data['access_token']
    refresh_token = data['refresh_token']

    print('got new token ' + str(access_token)) 

    insertToken(discordID, None, None, access_token, refresh_token)


########################################## FLASK STUFF ##################################################
app = Flask(__name__)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
 
@app.route('/database')
def database():
    print('trying to download the file')
    return send_file('database/userdb.sqlite3', as_attachment=True)

@app.route('/simap/<simID>')
def simap(simID):
    print(request.headers.get('User-Agent'))
    if 'ms-office' in request.headers.get('User-Agent') or '.NET4.0C; .NET4.0E;' in request.headers.get('User-Agent'):
        return 'hi'
    return redirect('https://www.simap.ch/shabforms/servlet/Search?EID=3&projectId='+str(simID)+'&mode=2')


@app.route('/test')
def test():
    print('testing')
    return "hi"

@app.route('/')
def root():
    print('called root')
    #print('got request')
    response = request.args
    code = response['code'] #for user auth
    #print(f'code is {code}')
    (discordID,serverID) = response['state'].split(':') #mine

    url = 'https://www.bungie.net/platform/app/oauth/token/'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'authorization': 'Basic '+ str(B64_SECRET) #unqiue to this app
    }

    data = 'grant_type=authorization_code&code='+str(code)

    r = requests.post(url, data=data, headers=headers)
    #print(r)
    data = r.json()
    access_token = data['access_token']
    refresh_token = data['refresh_token']

    #print(f'bungie responded {r.content} and the token is {access_token}')
    #membershipid = r.json()['membership_id']

    reqParams = {
        'Authorization': 'Bearer ' + str(access_token),
        'X-API-Key': BUNGIE_TOKEN
    }
    
    r = requests.get(url='https://www.bungie.net/platform/User/GetMembershipsForCurrentUser/', headers=reqParams)
    response = r.json()['Response']
    membershiplist = response['destinyMemberships']
    #print(membershiplist)
    for membership in membershiplist:
        if "crossSaveOverride" in membership.keys() and membership["crossSaveOverride"] and membership["membershipType"] != membership["crossSaveOverride"]:
            #print(f'membership {membership["membershipType"]} did not equal override {membership["crossSaveOverride"]}')
            continue
        insertToken(int(discordID), int(membership['membershipId']), int(serverID), access_token, refresh_token)
        print(f"<@{discordID}> registered with ID {membership['membershipId']} and display name {membership['LastSeenDisplayName']}")
        webhookURL = NEWTONS_WEBHOOK
        requestdata = {
            'content': f"<@{discordID}> has ID {membership['membershipId']} and display name {membership['LastSeenDisplayName']}",
            'username': 'EscalatorBot',
            "allowed_mentions": {
                "parse": ["users"],
                "users": []
            },
        }
        rp = requests.post(url=webhookURL, data=json.dumps(requestdata), headers={"Content-Type": "application/json"})
    return 'Thank you for signing up with <h1> Elevator Bot </h1>\n <p style="bottom: 20" >There will be cake</p>' # response to your request.


@app.route('/.well-known/acme-challenge/<challenge>')
def letsencrypt_check(challenge):
    challenge_response = {
        "<some_challenge_token>":"<challenge_response>",
        "<other_challenge_token>":"<challenge_response>"
    }
    return Response(challenge_response[challenge], mimetype='text/plain')

@app.before_request
def before_request():
    if request.url.startswith('http://'):
        return redirect(request.url.replace('http://', 'https://'), code=301)

@app.errorhandler(404)
def not_found():
    """Page not found."""
    return "page not founderino"

if __name__ == '__main__':
    print('server running')
    context = ('/etc/letsencrypt/live/rc19v2108.dnh.net/fullchain.pem', '/etc/letsencrypt/live/rc19v2108.dnh.net/privkey.pem')
    app.run(host= '0.0.0.0', port=443, ssl_context=context)


