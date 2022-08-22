#!/usr/bin/python3
import os
import requests
import datetime
import json
from argparse import ArgumentParser
from pprint import pprint
from time import sleep
import logging
from dotenv import load_dotenv, find_dotenv

# instantiate global variable
oauth2_base_url = "https://www.googleapis.com/oauth2/v4/token?"
nest_url = "https://smartdevicemanagement.googleapis.com/v1/enterprises/"
oauth2_token = None
device_id = None
load_dotenv()

# create class to hold oauth2 token information
class Oauth2_Token:
    def __init__(self, access_token):
        self.access_token = access_token
        self.expires_at = datetime.datetime.today() + datetime.timedelta(hours = 1)

# function to refresh the oauth2 token
def refresh_auth_key():
    global oauth2_token
    try:
        response = requests.post(oauth2_base_url + "client_id=" + OAUTH2_CLIENT_ID + 
                    "&client_secret=" + OAUTH2_CLIENT_SECRET + 
                    "&refresh_token=" + OAUTH2_REFRESH_TOKEN + 
                    "&grant_type=refresh_token" )
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if oauth2_token == None:
        oauth2_token = Oauth2_Token(response.json()['access_token'])
    else:
        oauth2_token.access_token = response.json()['access_token']
        oauth2_token.expires_at = datetime.datetime.today() + datetime.timedelta(hours = 1)

# function to change the mode of the nest ex. OFF, COOL, HEAT
def set_nest_mode(mode):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + oauth2_token.access_token}
    data = json.loads('{"command": "sdm.devices.commands.ThermostatMode.SetMode", "params": {"mode" : "' + mode + '"}}')
    try:
        response = requests.post(nest_url + PROJECT_ID + "/devices/" + device_id + ":executeCommand", headers=headers, data=json.dumps(data))
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return response

# function to get list containing device informaiton
def get_nest_device():
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + oauth2_token.access_token}
    try:
        response = requests.get(nest_url + PROJECT_ID + "/devices", headers=headers)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return response.json()["devices"][0]

# main function
def main(manual):
    # Load environment variables from .env file
    global PROJECT_ID
    global OAUTH2_CLIENT_ID
    global OAUTH2_CLIENT_SECRET
    global OAUTH2_REFRESH_TOKEN
    PROJECT_ID = os.environ.get("PROJECT_ID")
    OAUTH2_CLIENT_ID = os.environ.get("OAUTH2_CLIENT_ID")
    OAUTH2_CLIENT_SECRET = os.environ.get("OAUTH2_CLIENT_SECRET")
    OAUTH2_REFRESH_TOKEN = os.environ.get("OAUTH2_REFRESH_TOKEN")
    now = datetime.datetime.now()
    # setup logging
    logging.basicConfig(filename='/var/tmp/ac_cycler.log', level=logging.INFO)

    global device_id
    logging.info("Getting auth key\n")
    
    # run the refresh_auth_key function before first api connect attempt
    refresh_auth_key()
    logging.info("Getting Device ID\n")

    # get device id, the device_id is just the last portion of the name variable
    device_id = get_nest_device()['name'].split('/')[-1]

    # print starting loop to log as long as the manual argument has not been provided
    if manual == None:
        logging.info("Starting Loop...\n")

    # start loop as long as manual argument is not provided
    while(manual == None):
        # create timestamp for log on current loop
        now = datetime.datetime.now()
        # check that the oauth2 token is still valid from, refreshes token if not
        if oauth2_token == None or oauth2_token.expires_at < datetime.datetime.today():
            logging.info("Refreshing auth key\n")
            refresh_auth_key()
        logging.info("Get device info...\n")
        device = get_nest_device()
        logging.info("Current status: " + device["traits"]["sdm.devices.traits.ThermostatHvac"]["status"] + "\n" + now.strftime("%m/%d/%Y, %H:%M:%S"))
        # if the ac is currently running, turn off the AC for 5 minutes before tunring it back on and waiting 1 hour before restarting loop 
        if device["traits"]["sdm.devices.traits.ThermostatHvac"]["status"] == "COOLING":
            logging.info("Setting mode to OFF\n" + now.strftime("%m/%d/%Y, %H:%M:%S"))
            set_nest_mode("OFF")
            logging.info("Sleeping for 5 minutes...\n")
            sleep(300)
            logging.info("Setting mode to COOL\n" + now.strftime("%m/%d/%Y, %H:%M:%S"))
            set_nest_mode("COOL")
        logging.info("Sleeping for 60 minutes" + now.strftime("%m/%d/%Y, %H:%M:%S"))
        sleep(3600)


    # enables or disables system based on manual argument
    if manual == '0':
        set_nest_mode('OFF')
        logging.info("off " + now.strftime("%m/%d/%Y, %H:%M:%S"))
    elif manual == '1':
        set_nest_mode('COOL')
        logging.info("cooling " + now.strftime("%m/%d/%Y, %H:%M:%S"))
    elif manual == '2':
        set_nest_mode('HEAT')
        logging.info("heating " + now.strftime("%m/%d/%Y, %H:%M:%S"))

# __name__ function to run main if file is run directly
if __name__ == '__main__':
    parser = ArgumentParser("Nest AC State Cycler")
    # argument parsing to run in command line
    parser.add_argument('-m',
                        '--manual',
                        help='Single run to manually enable or disable nest, enter 1 for Cooling, 2 for Heat, and 0 for Off')

    args = parser.parse_args()

    main(args.manual)