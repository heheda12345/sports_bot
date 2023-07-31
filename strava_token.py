from requests_oauthlib import OAuth2Session
import os
import configparser
from flask import Flask, request
import json

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")
client_id = config['strava']['client_id']
client_secret = config['strava']['client_secret']
server_ip = config['server']['server_ip']
server_port = config['server']['server_port']
redirect_url = config['strava']['redirect_url'] + "/strava_oauth"
ssl_context = (config['ssl']['certfile'], config['ssl']['keyfile'])
session = OAuth2Session(client_id=client_id, redirect_uri=redirect_url)

def save_token(token):
    with open('token.json', 'w') as f:
        json.dump(token, f)



@app.route("/strava_oauth", methods=["GET"])
def strava_oauth():
    print(request.args)
    print(request.method)

    redirect_url = request.url
    print("redirect_url", redirect_url)
    token_url = "https://www.strava.com/api/v3/oauth/token"
    global session
    session.fetch_token(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        authorization_response=redirect_url,
        include_client_id=True
    )
    save_token(session.token)
    response = session.get("https://www.strava.com/api/v3/athlete")
    # Print response
    print("\n\n\n")
    print(f"Response Status: {response.status_code}")
    print(f"Response Reason: {response.reason}")
    print(f"Time Elaspsed: {response.elapsed}")
    print(f"Response Text: \n{'-'*15}\n{response.text}")
    return "Success!"


def get_auth_link(scope):
    auth_base_url = "https://www.strava.com/oauth/authorize"
    global session
    session.scope = scope
    auth_link = session.authorization_url(auth_base_url)
    
    print(f"Click Here: {auth_link[0]}")
    return auth_link[0]

@app.route("/strava", methods=["GET"])
def strava():
    scope = "activity:read_all,activity:write"
    link = get_auth_link(scope)
    html = f'<a href="{link}">{scope}</a>'
    return html


if __name__ == '__main__':
    app.run(host=server_ip, port=server_port, debug=True, ssl_context=ssl_context)