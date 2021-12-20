#!/usr/bin/python3

import asyncio
import json
import os
import time

import requests
from base64 import b64encode
from config import BUNGIE_APPLICATION_CLIENT_SECRET, BOT_ACCOUNT_PUBLIC_KEY, BUNGIE_APPLICATION_API_KEY, NEWTONS_WEBHOOK, BUNGIE_APPLICATION_CLIENT_ID
from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)
from nacl.encoding import HexEncoder
from nacl.hash import sha256
from nacl.signing import VerifyKey

from database import (
    create_connection_pool,
    getRefreshToken,
    getToken,
    insertToken,
    lookupDiscordID,
)

verify_key = VerifyKey(bytes.fromhex(BOT_ACCOUNT_PUBLIC_KEY))

########################################## FLASK STUFF ##################################################
app = Flask(__name__)

loop = asyncio.get_event_loop()
loop.run_until_complete(create_connection_pool())


def shutdown_server():
    func = request.environ._get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@app.route("/test")
def test():
    print("testing")
    return "hi"


@app.route("/")
def root():
    print("hi")
    response = request.args
    if not (code := response._get("code", None)):  # for user auth
        return """
<img src="https://vignette.wikia.nocookie.net/meme/images/a/a8/Portal-cake.jpg/revision/latest/top-crop/width/360/height/450?cb=20110913215856"/><br/>
<a href="https://elevatorbot.ch/vendorbounties">Vendorbounties</a><br/>
<a href="https://elevatorbot.ch/fireteamstalker">Fireteamstalker</a><br/>
<a href="https://elevatorbot.ch/descendadmintool">Descend Members</a><br/>
"""
    (discordID, serverID) = response["state"].split(":")  # mine

    url = "https://www.bungie.net/platform/app/oauth/token/"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "authorization": "Basic " + b64encode(f"{BUNGIE_APPLICATION_CLIENT_ID}:{BUNGIE_APPLICATION_CLIENT_SECRET}".encode("ascii")).decode("ascii"),  # unqiue to this app
    }

    data = f"grant_type=authorization_code&code={code}"

    t = int(time.time())
    r = requests.post(url, data=data, headers=headers)
    authresponse = r.json()
    if not "access_token" in authresponse:
        print(f"invalid authresponse: {authresponse}")
        return "Something went wrong. Maybe an invalid token/code in your URL?"
    access_token = authresponse["access_token"]
    refresh_token = authresponse["__refresh_token"]
    token_expiry = t + authresponse["expires_in"]
    refresh_token_expiry = t + authresponse["refresh_expires_in"]

    reqParams = {
        "Authorization": "Bearer " + str(access_token),
        "X-API-Key": BUNGIE_APPLICATION_API_KEY,
    }

    r = requests.get(
        url="https://www.bungie.net/platform/User/GetMembershipsForCurrentUser/",
        headers=reqParams,
    )
    response = r.json()["Response"]
    membershiplist = response["destinyMemberships"]

    primarymembership = None
    display_name = "_missing_"
    for membership in membershiplist:
        if int(membership["membershipType"]) == 3:
            display_name = membership["displayName"]
            steam_name = membership["LastSeenDisplayName"]
        if (
            "crossSaveOverride" in membership.keys()
            and membership["crossSaveOverride"]
            and membership["membershipType"] != membership["crossSaveOverride"]
        ):
            # the primary membership has been identified
            continue
        primarymembership = membership

    if not primarymembership:
        print(f"no primary membership found for {display_name} aka {discordID} in server {serverID}")

    destinyID = int(primarymembership["membershipId"])
    systemID = int(primarymembership["membershipType"])

    success = loop.run_until_complete(
        insertToken(
            int(discordID),
            destinyID,
            systemID,
            int(serverID),
            access_token,
            refresh_token,
            token_expiry,
            refresh_token_expiry,
        )
    )
    if not success:
        return f"""
        You already seem to be signed up
        Please verify that the ID {destinyID} belongs to you and notify one of the developers
        """

    print(
        f"Inserted token. <@{discordID}> has destinyID `{destinyID}`, Bungie-Name `{display_name}`, Steam-Name `{steam_name}`"
    )
    webhookURL = NEWTONS_WEBHOOK
    requestdata = {
        "content": f"<@{discordID}> has destinyID `{destinyID}`, Bungie-Name `{display_name}`, Steam-Name `{steam_name}`, System `{systemID}`",
        "username": "EscalatorBot",
        "allowed_mentions": {"parse": ["users"], "users": []},
    }
    rp = requests.post(
        url=webhookURL,
        data=json.dumps(requestdata),
        headers={"Content-Type": "application/json"},
    )
    return """
        Thank you for signing up with <h1> Elevator Bot </h1>\n <p style="bottom: 20" >There will be cake</p>
        <script>
            setTimeout("location.href = 'https://www.elevatorbot.ch';",1500);
        </script>
    """


@app.route("/neriapi/<destinyid>")
def neriapi(destinyid):
    if (
        not sha256(
            bytes(request.headers._get("x-neriapi-key", "missing"), "utf-8"),
            encoder=HexEncoder,
        )
        == b"e3143238a43d9f1c12f47314a8c858a5589f1b2f5c174d391a0e361f869b1427"
    ):
        return jsonify(status=500, error="Wrong api key")
    discordID = loop.run_until_complete(lookupDiscordID(destinyid))
    if not discordID:
        return jsonify(status=500, error="Unknown destiny id")
    token = loop.run_until_complete(getToken(discordID))
    refresh_token = loop.run_until_complete(getRefreshToken(discordID))
    if not token:
        return jsonify(status=500, error="Token not found")
    return jsonify(status=200, token=token, refresh_token=refresh_token)


@app.route("/.well-known/acme-challenge/<challenge>")
def letsencrypt_check(challenge):
    challenge_response = {
        "<some_challenge_token>": "<challenge_response>",
        "<other_challenge_token>": "<challenge_response>",
    }
    return Response(challenge_response[challenge], mimetype="text/plain")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "../ElevatorBot/static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.before_request
def before_request():
    if request.url.startswith("http://"):
        print("turned http into https")
        return redirect(request.url.replace("http://", "https://"), code=301)
    pass


@app.errorhandler(404)
def not_found(e):
    """Page not found."""
    return "page not founderino"


if __name__ == "__main__":
    print("server running")
    app.run(debug=True, host="0.0.0.0")
