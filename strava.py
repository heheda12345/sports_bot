import os
import json
import configparser
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
import logging
logging.basicConfig(level=logging.INFO)
import time

config = configparser.ConfigParser()
config.read("config.ini")
client_id = config['strava']['client_id']
client_secret = config['strava']['client_secret']

strava = None

class TokenError(Exception):
    pass

def load_token():
    if os.path.exists('token.json'):
        with open('token.json', 'r') as f:
            return json.load(f)
    return None

def init_session():
    token = load_token()
    if not token:
        raise TokenError("Token not found. Please authorize first.")
    global strava
    strava = OAuth2Session(client_id, token=token)
    try:
        response = strava.get("https://www.strava.com/api/v3/athlete")
    except TokenExpiredError as e:
        logging.info("Token expired. Refreshing...")
        token = strava.refresh_token("https://www.strava.com/api/v3/oauth/token", client_id=client_id, client_secret=client_secret)
        with open('token.json', 'w') as f:
            json.dump(token, f)
        response = strava.get("https://www.strava.com/api/v3/athlete")
    if response.status_code == 200:
        logging.info("Token is valid.")
    else:
        logging.error("Token is invalid.")
        logging.error(f"Response Status: {response.status_code}")
        logging.error(f"Response Reason: {response.reason}")
        logging.error(f"Time Elaspsed: {response.elapsed}")
        logging.error(f"Response Text: \n{'-'*15}\n{response.text}")
        raise TokenError("Token is invalid.")


def wait_for_upload(upload_id, max_second=20):
    for i in range(max_second):
        resp = strava.get("https://www.strava.com/api/v3/uploads/{}".format(upload_id))
        logging.info("Upload check: code={}, reason={}, text={}".format(resp.status_code, resp.reason, resp.text))
        resp_json = json.loads(resp.text)
        if resp_json["error"] != None:
            error_msg = "Upload failed: {}".format(resp_json["error"])
            logging.error(error_msg)
            return error_msg
        if resp_json["activity_id"] != None:
            logging.info("Upload successful!")
            return f"Upload success: {resp_json['activity_id']}"
    return "Upload timeout"

def post_activity(file_path, name, description=None, trainer=None, commute=None, external_id=None):
    init_session()
    data_type = file_path.split(".")[-1]
    if data_type == 'gz':
        data_type = file_path.split(".")[-2] + ".gz"
    if data_type not in ['fit', 'fit.gz', 'tcx', 'tcx.gz', 'gpx', 'gpx.gz']:
        logging.error("Unsupported file type.")
        return
    url = "https://www.strava.com/api/v3/uploads"
    with open(file_path, 'rb') as f:
        data = {'name': name, 'data_type': data_type}
        if description:
            data['description'] = description
        if trainer:
            data['trainer'] = trainer
        if commute:
            data['commute'] = commute
        if external_id:
            data['external_id'] = external_id
        response = strava.post(url, files={'file': f}, data=data)
        logging.info(f"Upload response: code={response.status_code}, reason={response.reason}, text={response.text}")
        text_json = json.loads(response.text)
        upload_id = text_json['id']
        return wait_for_upload(upload_id)

def check_activity(activity_id):
    init_session()
    url = "https://www.strava.com/api/v3/uploads/{}".format(activity_id)
    response = strava.get(url)
    print("\n\n\n")
    print(f"Response Status: {response.status_code}")
    print(f"Response Reason: {response.reason}")
    print(f"Time Elaspsed: {response.elapsed}")
    print(f"Response Text: \n{'-'*15}\n{response.text}")

if __name__ == '__main__':
    # init_session()
    # check_activity(10218463291)
    ret = post_activity("ZeppLife20230531214756.gpx", "test")
    print("final ret", ret)
    # post_activity("new.gpx", "test")