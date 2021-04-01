# KSC - Key Stock Checker
Simple, quick to set up and easy to use stock notification program to monitor the stock of a list of products.

## Requirements
- [Firefox](https://www.mozilla.org/en-US/firefox/download/thanks/)
 ```
sudo apt install firefox
```
- [Python 3](https://www.python.org/downloads/)
```
sudo apt install python3
```
- [geckodriver](https://github.com/mozilla/geckodriver/releases) (make sure it’s in your PATH, e.g., place it in /usr/bin or /usr/local/bin)


## Discord Notifications
This program uses discord notifications to alert the user of new stock. You will need to provide a discord webhook of the server where you wish to receive alerts.
- Discord Notifications using Webhooks: [Discord Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

## Setup
1. Download ksc.py and packages.txt
2. Complete all requirements
3. Install the necessary packages 
   -  `pip3 install -r packages.txt`

## Run
```
python3 ksc.py
```

## Navigate KSC
- WELCOME TO KSC HOME. CONTINUE TO (setup) FOR ALERTS AND DISCORD, (products) TO VIEW, ADD OR REMOVE PRODUCTS, (start) TO START CHECKING STOCK, (exit) TO QUIT KSC
- WELCOME TO KSC SETUP. (info) TO CHECK CURRENT ALERT DETAILS, (alert keyword1 keyword2 keywordn) TO SET THE KEYWORD(S) FOR ALERTS, (clear alert) TO CLEAR AN ALERT, (discord link_to_discord_webhook) TO SET UP DISCORD NOTIFICATIONS, (back) TO RETURN HOME
- WELCOME TO KSC PRODUCTS. (list) TO VIEW PRODUCTS, (add url, search_key, name) TO ADD A PRODUCT, (remove productnumber1, productnumber2, productnumbern)/remove all) TO REMOVE THE PRODUCT(S), (back) TO RETURN HOME
