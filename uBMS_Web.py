import socket
import re
import machine
import uBMS_WiFi
import config

def AP_start():
    uBMS_WiFi.sta.active(False)
    print("STA mode disactivated")
    uBMS_WiFi.ap.active(True)
    print("AP mode activated")
   
    uBMS_WebPage()

def web_page():
  
    html = """<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>uBMS Web Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f7f7f7;
            margin: 0;
            padding: 20px 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .form-control {
            margin-bottom: 15px;
        }
        .form-control label {
            display: block;
            margin-bottom: 5px;
            color: #555;
        }
        .form-control input {
            width: calc(100% - 22px);
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .form-control input[type="number"] {
            -moz-appearance: textfield;
        }
        .form-control input::-webkit-outer-spin-button,
        .form-control input::-webkit-inner-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-align: center;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        .button:hover {
            background-color: #45a049;
        }
        .button2 {
            background-color: red;
        }
        .button2:hover {
            background-color: darkred;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>uBMS Web Server</h1>
        <div class="form">
            <form action="/configure" method="POST" autocomplete="off" autocapitalize="none">
                <div class="form-control">
                    <label for="ssid">SSID:</label>
                    <input type="text" id="ssid" name="ssid" value=\"""" + config.ssid + """\">
                </div>
                <div class="form-control">
                    <label for="password">Password:</label>
                    <input type="text" id="password" name="password" value=\"""" + config.password + """\">
                </div>
                <div class="form-control">
                    <label for="MINIMUM_SALE_PRICE">Minimum Sale Price [PLN]:</label>
                    <input type="number" id="MINIMUM_SALE_PRICE" name="MINIMUM_SALE_PRICE" step="0.01" value=\"""" + str(config.MINIMUM_SALE_PRICE) + """\">
                </div>
                <div class="form-control">
                    <button class="button">Save</button>
                </div>
            </form>
        </div>
    </div>
</body>
</html>"""
    return html

import re

def save_variables(ssid, password, minimum_sale_price):
    print(f"Attempting to save config")
    
    config_file = "config.py"
    
    # Read the current contents of the config file
    try:
        with open(config_file, "r") as file:
            lines = file.readlines()
    except OSError:
        lines = []

    # Create a dictionary of new values to update in the config
    new_values = {
        'ssid': f'"{ssid}"',
        'password': f'"{password}"',
        "MINIMUM_SALE_PRICE": minimum_sale_price,
    }
    
    # Update the existing lines or add them if they don't exist
    for key, value in new_values.items():
        pattern = re.compile(f"^{key}\s*=\s*.*$")
        updated = False
        for i, line in enumerate(lines):
            if pattern.match(line):
                lines[i] = f"{key} = {value}\n"
                updated = True
                break
        if not updated:
            lines.append(f"{key} = {value}\n")
    
    # Write the updated contents back to the config file
    try:
        with open(config_file, "w") as file:
            for line in lines:
                file.write(line)
        print("Successfully saved config to config.py")
        machine.reset()
    except OSError as e:
        print(f"Failed to save config: {e}")

def url_decode(encoded_str):
    decoded_str = encoded_str.replace('+', ' ')
    # Dictionary of URL encoded characters and their corresponding decoded values
    replacements = {
        '%20': ' ',
        '%21': '!',
        '%22': '"',
        '%23': '#',
        '%24': '$',
        '%25': '%',
        '%26': '&',
        '%27': "'",
        '%28': '(',
        '%29': ')',
        '%2A': '*',
        '%2B': '+',
        '%2C': ',',
        '%2D': '-',
        '%2E': '.',
        '%2F': '/',
        '%3A': ':',
        '%3B': ';',
        '%3C': '<',
        '%3D': '=',
        '%3E': '>',
        '%3F': '?',
        '%40': '@',
        '%5B': '[',
        '%5C': '\\',
        '%5D': ']',
        '%5E': '^',
        '%5F': '_',
        '%60': '`',
        '%7B': '{',
        '%7C': '|',
        '%7D': '}',
        '%7E': '~'
    }
    
    for key, value in replacements.items():
        decoded_str = decoded_str.replace(key, value)
    
    return decoded_str

def parse_post_data(data):
    params = {}
    for pair in data.split('&'):
        key, value = pair.split('=')
        key = url_decode(key)
        value = url_decode(value)
        params[key] = value
    return params

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

def uBMS_WebPage():
    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(2048)
        print(request)
        request_str = request.decode('utf-8')
        print('Content = %s' % request_str)
  
        if 'POST /configure' in request_str:
            parts = request_str.split('\r\n\r\n')
            print(f"Request parts: {parts}")
            if len(parts) > 1:
                post_data = parts[1]
                print(f"Post data: {post_data}")
                decoded_params = parse_post_data(post_data)
                ssid = decoded_params.get('ssid', '')
                password = decoded_params.get('password', '')
                minimum_sale_price = decoded_params.get('MINIMUM_SALE_PRICE', '')
                print(f"Extracted SSID: {ssid}, Password: {password}, Lower_threshold: {minimum_sale_price}")
                ssid = url_decode(ssid)
                password = url_decode(password)
                print(f"Decoded SSID: {ssid}, Password: {password}, Lower threshold: {minimum_sale_price}")
                save_variables(ssid, password, minimum_sale_price)
  
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n'.encode('utf-8'))
        conn.send('Content-Type: text/html\n'.encode('utf-8'))
        conn.send('Connection: close\n\n'.encode('utf-8'))
        conn.sendall(response.encode('utf-8'))
        conn.close()
