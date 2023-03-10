#!/usr/bin/env python3

import socket
import json
import http.client, urllib
import logging
import os

pushover_token = os.environ['PUSHOVER_TOKEN']
pushover_user = os.environ['PUSHOVER_USER']
sim_key = os.environ['SIM_KEY']
listen_port = int(os.environ['LISTEN_PORT'])
listen_ip = os.environ['LISTEN_IP']

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
server_sock.bind((listen_ip,listen_port))
server_sock.listen(5)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s -- %(levelname)s -- %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def process_and_send(data):
    logger.info(f"RX: {data}")

    # Use key for security
    if data['k'] != sim_key:
        return

    data['d'] = json.loads(data['d'])
    pushover_data = {"token":pushover_token,"user":pushover_user,"message":data['d']['m'] + " (sent via cellular)"}
    if data['d']['p'] != "":
        pushover_data['priority'] = int(data['d']['p'])
        if pushover_data['priority'] == 2:
            pushover_data['expire'] = 300
            pushover_data['retry'] = 30
    
    logger.info(f"TX: {pushover_data}")
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode(pushover_data
        ), { "Content-type": "application/x-www-form-urlencoded" })

while True:
    connection_socket, addr = server_sock.accept()
    
    # Read data on socket
    try:
        data = connection_socket.recv(1024).decode()
        connection_socket.close()
    except:
        connection_socket.close()
        continue

    # Convert data to json
    try:
        data = json.loads(data)
    except Exception as e:
        logger.error(f"Exception {e}: [{data}]")
        continue 

    # Process data and send message
    process_and_send(data)
