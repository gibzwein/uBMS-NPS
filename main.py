import network
import urequests as requests
import machine
import ntptime
import json
import time
import time_utils
import config
import gc
from machine import Pin, SoftI2C
import uBMS_WiFi
import uBMS_Web

# LED Config
led_pin = 6
led = machine.Pin(led_pin, machine.Pin.OUT)

# Relays config
r1_pin = 4
relay1 = machine.Pin(r1_pin, machine.Pin.OUT)

# Define the pin for the button
button_pin = 9  # For example, GPIO0 for ESP8266
button = machine.Pin(button_pin, machine.Pin.IN, machine.Pin.PULL_UP)

def button_handler(pin):
    print("Button pressed")
    uBMS_Web.AP_start()

button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_handler)

# Golbal variables
rce_prices = None
rce_prices_stats = None
lowest_entries = None
last_time = (0,0,0,0,0,0,0,0)
current_price = None

uBMS_WiFi.wifi_connect()

def get_data():
    max_retries = 3
    retry_count = 0
    led.value(1)
    
    while retry_count < max_retries:
        try:
            date_string = time_utils.get_api_date()

            url = f"https://api.raporty.pse.pl/api/rce-pln?$filter=doba eq '{date_string}'&$select=rce_pln,udtczas"
            print("Requesting URL:", url)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout = 10)
            if response.status_code == 200:
                print('Data fetched')
                gc.collect()
                try:
                    return json.loads(response.text)
                except ValueError:
                    print("Error decoding JSON response")
                    return None
            else:
                print(f"Error while retrieving data. Response code: {response.status_code}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying to fetch data in {5 * retry_count} seconds...")
                    time.sleep(5 * retry_count)
                else:
                    print("Exceeded maximum number of data retrieval attempts.")
            led.value(0)
            return None
        except Exception as e:
            print(f"An error occurred while retrieving data: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying to fetch data in {5 * retry_count} seconds...")
                time.sleep(5 * retry_count)
            else:
                print("Exceeded maximum number of data retrieval attempts.")
                return None

def parse_data(json_data):
    parsed_data = []
    for row in json_data['value']:
        date_str = row['udtczas']
        unix_timestamp_to = time_utils.get_timestamp_from_datestring(row['udtczas'])
        unix_timestamp_from = unix_timestamp_to - 15*60 # Move start 15 minutes before
        
        # Append to list
        parsed_data.append({
            'datetime': date_str,
            'timestamp_from': unix_timestamp_from,
            'timestamp_to': unix_timestamp_to,
            'price': row['rce_pln']
        })
    print('Data parsed')
    print(len(parsed_data))
    gc.collect()
    return parsed_data

def calculate_average(data):
    total = sum(entry['price'] for entry in data)
    min_price = min(entry['price'] for entry in data)
    max_price = max(entry['price'] for entry in data)
    print('Calculated averages')
    gc.collect()
    return {'average': total / len(data), 'min': min_price, 'max': max_price}

def display_data(price_data, price):
    if not isinstance(price_data, dict):
        print("Invalid price_data format")
        return
    print(f"Current price: {price}")
    print(config.MINIMUM_SALE_PRICE)
    if price < config.MINIMUM_SALE_PRICE:
        print(f"Price lower than: {config.MINIMUM_SALE_PRICE}")
        relay1.value(1)
        print("Relay ON")
    else:
        relay1.value(0)
        print("relay OFF")
    gc.collect()

def get_rce_prices():
    global rce_prices
    global rce_prices_stats
    global lowest_entries
    rce_prices = None
    rce_prices_stats = None
    lowest_entries = None
    data = get_data()
    rce_prices = parse_data(data)
    rce_prices_stats = calculate_average(rce_prices)

def get_current_price(now_timestamp):
    if rce_prices is None:
        return None

    if not isinstance(rce_prices, list):
        print("Error: rce_prices is not a list.")
        return None

    for row in rce_prices:
        if not isinstance(row, dict):
            print("Error: row is not a dictionary.")
            return None

        if now_timestamp >= row['timestamp_from'] and now_timestamp < row['timestamp_to']:
            print(row['price'], now_timestamp, row)
            led.value(not led.value())
            return row['price']

    gc.collect()
    return None

while True:
    if not uBMS_WiFi.sta.isconnected():
        uBMS_WiFi.wifi_connect()

    if rce_prices == None:
        rce_prices = get_rce_prices()

    now = time_utils.get_current_time()
    now_time = time.localtime(now)

    if last_time is None or last_time[4] != now_time[4]:
        print('Day changed, fetching new data')
        get_rce_prices()

        last_time = now_time

    current_price = get_current_price(now)
    if current_price is not None and rce_prices is not None:
        averages = calculate_average(rce_prices)
        display_data(averages, current_price)

    gc.collect()
    print("Free memory: ", gc.mem_free())
    time.sleep(1)