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
test_webook_host = os.environ['TEST_WEBHOOK_HOST']
test_webhook_path = os.environ['TEST_WEBHOOK_PATH']
send_email = os.environ['SEND_EMAIL']
email_username = os.environ['EMAIL_USERNAME']
email_password = os.environ['EMAIL_PASSWORD']
email_recipient = os.environ['EMAIL_RECIPIENT']

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

def process_and_send(data,addr):
    logger.info(f"RX -- {addr} -- {data}")

    # Use key for security
    if data['k'] != sim_key:
        return

    data['d'] = json.loads(data['d'])
    
    # Handle Modem Test Message:
    if data['d']['m'] == "t":
        logger.info(f"Healcheck Message Received. Sending Healcheck Pingback: {test_webook_host}{test_webhook_path}")
        conn = http.client.HTTPSConnection(f"{test_webook_host}:443")
        conn.request("PUT", test_webhook_path, 'test')
        response = conn.getresponse()
        if response.read().decode() != "":
            logger.info(response.read().decode())
        conn.close()
        return

    # Prepare and send message through pushover
    pushover_data = {"token":pushover_token,"user":pushover_user,"message":data['d']['m'] + " (sent via cellular)"}
    if data['d']['p'] != "":
        pushover_data['priority'] = int(data['d']['p'])
        if pushover_data['priority'] == 2:
            pushover_data['expire'] = 300
            pushover_data['retry'] = 30
    else:
        pushover_data['priority'] = 0
    
    logger.info(f"TX: {pushover_data}")
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json", json.dumps(pushover_data), {'Content-type': 'application/json'})
    response = conn.getresponse()
    if response.read().decode() != b"":
        logger.info(response.read().decode())
    conn.close()

    # Prepare and send message through email 
    if send_email.lower() == "true":
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(data['d']['m'] + " (sent via cellular)")
        msg['From'] = email_username
        msg['To'] = email_recipient
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(email_username, email_password)
            smtp_server.sendmail(email_username, email_recipient, msg.as_string())
            logger.info("Email message sent!")

while True:
    connection_socket, addr = server_sock.accept()
    data = ''
    # Read data on socket
    connection_socket.settimeout(30)
    try:
        data = connection_socket.recv(1024).decode()
        #connection_socket.close()
    except:
        logger.error(f"Exception {e}: [{data}]")
        connection_socket.close()
        continue

    # Convert data to json
    try:
        data = json.loads(data)
    except Exception as e:
        logger.error(f"Exception {e}: [{data}]")
        continue 

    # Process data and send message
    process_and_send(data,addr)
