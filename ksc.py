import json
import requests
import time
import datetime
import os
import threading
import pickle
import tldextract
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from fake_useragent import UserAgent
from colorama import Fore, Back, Style
from numpy import random
from discord_webhook import DiscordWebhook

# Setting options for req/selenium
ua = UserAgent()
options = Options()
options.headless = True

# Class to store product objects


class product:
    def __init__(self, url, searchKey, name):
        self.url = url
        self.searchKey = searchKey
        self.name = name
        self.reqAccess = None
        self.domainName = tldextract.extract(url).domain
        self.domain = '{uri.scheme}://{uri.netloc}/'.format(
            uri=urlparse(url))
        self.alerted = False

# Function to search for a file in the current directory


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

# Function to save objects to file


def save_object(obj, filename):
    with open(filename, 'wb') as outputFile:
        pickle.dump(obj, outputFile, pickle.HIGHEST_PROTOCOL)


def getInput():
    while input() != "stop":
        pass
    print(Fore.RED + "STOPPING STOCK CHECKER..." + Fore.RESET)


def firstLetter(product):
    return product.name[0]


def fullName(product):
    return product.name


def productSort(products):
    random.shuffle(products)
    products.sort(key=firstLetter)

# Function to check whether a product is in stock (search the html soup for the provided key) - request version


def reqStock(product, alertKeys, discordURL):
    response = requests.get(product.url, headers={
        'User-Agent': str(ua.firefox), 'Referer': 'https://www.google.com/'})
    soup = BeautifulSoup(response.content, 'html.parser')
    inStock = bool(soup.body.find_all(
        text=lambda t: product.searchKey.lower() in t.lower()))
    currentTimeFormat = datetime.datetime.now().strftime("%H:%M:%S")
    alertStock(product, inStock, currentTimeFormat, alertKeys, discordURL)

# Function to check whether a product is in stock (search the html soup for the provided key) - selenium version


def selStock(product, alertKeys, discordURL):
    browser = webdriver.Firefox(options=options)
    browser.get(product.url)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    inStock = bool(soup.body.find_all(
        text=lambda t: product.searchKey.lower() in t.lower()))
    currentTimeFormat = datetime.datetime.now().strftime("%H:%M:%S")
    browser.close()
    alertStock(product, inStock, currentTimeFormat, alertKeys, discordURL)

# Function to print stock status to terminal/alert discord


def alertStock(product, inStock, currentTimeFormat, alertKeys, discordURL):
    if not inStock:
        print(Fore.WHITE + currentTimeFormat, Fore.MAGENTA +
              "[" + product.domainName + "]", Fore.WHITE + product.name, Fore.RED + "OUT OF STOCK" + Fore.RESET)
        product.alerted = False

    else:
        print(Fore.WHITE + currentTimeFormat, Fore.MAGENTA +
              "[" + product.domainName + "]", Fore.WHITE + product.name, Fore.GREEN + "IN STOCK" + Fore.RESET)
        # Sends alert to specified discord webhook if the alert keys are present within the product name
        if alertKeys and discordURL is not None and product.alerted == False:
            alertBool = all(alertKey in product.name.lower()
                            for alertKey in alertKeys)
            if alertBool:
                webhook = DiscordWebhook(
                    url=discordURL, content=product.name + " " + product.url + " IN STOCK")
                webhook.execute()
                # Sets boolean to notify the system that this product has had a discord alert in this session (stops notification spam)
                product.alerted = True

# Function to iteratively search product list


def stockChecker(products, alertKeys, discordURL, stopChecker):
    # Shuffles list on each iteration (stops system from sending consistent and predictable traffic)
    productSort(products)
    for product in products:
        if not stopChecker.is_alive():
            return
        else:
            # Sets the type of access if not defined (product just added)
            if product.reqAccess is None:
                response = requests.get(product.domain, headers={
                                        'User-Agent': str(ua.firefox), 'Referer': 'https://www.google.com/'})
                # Use request module if the request gets a 200, selenium if not
                if response.status_code == 200:
                    # Check if the request module is being led to a NOFOLLOW
                    soup = BeautifulSoup(response.content, 'html.parser')
                    meta = soup.find_all("meta")
                    for tags in meta:
                        if("NOFOLLOW".lower() in tags['content'].lower()):
                            product.reqAccess = False
                            break
                        else:
                            product.reqAccess = True
                    save_object(products, 'products.pkl')
                else:
                    product.reqAccess = False
                    save_object(products, 'products.pkl')
            if product.reqAccess:
                reqStock(product, alertKeys, discordURL)
            else:
                selStock(product, alertKeys, discordURL)
            time.sleep(random.uniform(2, 4))


def main():
    try:
        # Creates product and setup files if they dont exist within path, otherwise read the existing files
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if find("products.pkl", dir_path) is None:
            products = []
            save_object(products, 'products.pkl')
        else:
            with open('products.pkl', 'rb') as inputFile:
                products = pickle.load(inputFile)
        if find("setup.pkl", dir_path) is None:
            setup = [None] * 2
            save_object(setup, 'setup.pkl')
        else:
            with open('setup.pkl', 'rb') as inputFile:
                setup = pickle.load(inputFile)

        # KSC interface
        while True:
            print(Fore.LIGHTRED_EX + "WELCOME TO KSC HOME. CONTINUE TO (setup) FOR ALERTS AND DISCORD, (products) TO VIEW, ADD OR REMOVE PRODUCTS, (start) TO START CHECKING STOCK, (exit) TO QUIT KSC" + Fore.RESET)
            alertKeys = setup[0]
            discordURL = setup[1]
            flow = input()
            if flow == "setup":
                while True:
                    print(Fore.LIGHTMAGENTA_EX + "WELCOME TO KSC SETUP. (info) TO CHECK CURRENT ALERT DETAILS, (alert keyword1 keyword2 keywordn) TO SET THE KEYWORD(S) FOR ALERTS, (clear alert) TO CLEAR AN ALERT, (discord link_to_discord_webhook) TO SET UP DISCORD NOTIFICATIONS, (back) TO RETURN HOME" + Fore.RESET)
                    setupInput = input()
                    if setupInput == "info":
                        keywords = setup[0]
                        webhook = setup[1]
                        if keywords is not None:
                            print(Fore.YELLOW + "KEYWORDS:" + Fore.RESET)
                            for keyword in keywords:
                                print(Fore.WHITE + keyword + Fore.RESET)
                        else:
                            print(Fore.RED + "NO KEYWORD(S) SET" + Fore.RESET)
                        if webhook is not None:
                            print(Fore.YELLOW + "DISCORD: " +
                                  Fore.WHITE + webhook + Fore.RESET)
                        else:
                            print(Fore.RED + "DISCORD NOT LINKED" + Fore.RESET)
                    elif setupInput == "alert":
                        print(Fore.YELLOW +
                              "alert keyword1 keyword2 keywordn" + Fore.RESET)
                    elif setupInput.startswith("alert "):
                        keywords = setupInput[6:len(
                            setupInput)].lower().split()
                        setup[0] = keywords
                        save_object(setup, 'setup.pkl')
                        for keyword in keywords:
                            print(Fore.WHITE + keyword + Fore.RESET)
                        print(Fore.GREEN + "KEYWORD(S) SET" + Fore.RESET)
                    elif setupInput == "clear alert":
                        keywords = None
                        setup[0] = keywords
                        save_object(setup, 'setup.pkl')
                        print(Fore.GREEN + "ALERT CLEARED" + Fore.RESET)
                    elif setupInput == "discord":
                        print(Fore.YELLOW +
                              "discord link_to_discord_webhook" + Fore.RESET)
                    elif setupInput.startswith("discord "):
                        webhook = setupInput[8:len(setupInput)]
                        if webhook.startswith("https://discord.com/api/webhooks/"):
                            setup[1] = webhook
                            save_object(setup, 'setup.pkl')
                            print(Fore.GREEN +
                                  "DISCORD", Fore.WHITE + webhook + Fore.GREEN, "LINKED" + Fore.RESET)
                        else:
                            print(Fore.WHITE + webhook, Fore.RED +
                                  "IS NOT A VALID DISCORD WEBHOOK" + Fore.RESET)
                    elif setupInput == "back":
                        break
                    else:
                        print(Fore.RED + "UNKNOWN COMMAND",
                              Fore.WHITE + "(" + setupInput + ")" + Fore.RESET)
            elif flow == "products":
                while True:
                    print(Fore.CYAN + "WELCOME TO KSC PRODUCTS. (list) TO VIEW PRODUCTS, (add url, search_key, name) TO ADD A PRODUCT, (remove productnumber1, productnumber2, productnumbern)/remove all) TO REMOVE THE PRODUCT(S), (back) TO RETURN HOME" + Fore.RESET)
                    productsInput = input()
                    if productsInput == "list":
                        products.sort(key=fullName)
                        index = 1
                        if not products:
                            print(Fore.RED + "NO PRODUCTS FOUND" + Fore.RESET)
                        else:
                            for eachProduct in products:
                                print(str(index) + ". " + Fore.MAGENTA +
                                      "[" + eachProduct.domainName + "] " + Fore.WHITE + eachProduct.name + " " + Fore.YELLOW + "{" + eachProduct.searchKey + "}" + Fore.RESET, sep="\n")
                                index += 1
                    elif productsInput == "remove":
                        print(
                            Fore.YELLOW + "remove productnumber1, productnumber2, productnumbern)/remove all" + Fore.RESET)
                    elif productsInput.startswith("remove "):
                        removeId = productsInput[7:len(productsInput)]
                        if removeId == "all":
                            products.clear()
                            save_object(products, 'products.pkl')
                            print(Fore.GREEN + "ALL PRODUCTS REMOVED" + Fore.RESET)
                        else:
                            removeIds = removeId.split(', ')
                            for removeId in removeIds:
                                if removeId.isdigit():
                                    removeId = int(removeId)
                                    if removeId <= len(products):
                                        removeId -= 1
                                        name = products[removeId].name
                                        del products[removeId]
                                        save_object(products, 'products.pkl')
                                        print(Fore.WHITE + name + Fore.GREEN +
                                              " REMOVED!" + Fore.RESET)
                                    else:
                                        print(Fore.RED + "NO PRODUCT LISTED AT POSITION",
                                              Fore.WHITE + str(removeId) + Fore.RESET)
                                else:
                                    print(Fore.WHITE + str(removeId), Fore.RED +
                                          "IS NOT A VALID NUMBER" + Fore.RESET)
                    elif productsInput == "add":
                        print(Fore.YELLOW + "add url, search_key, name" + Fore.RESET)
                    elif productsInput.startswith("add "):
                        productString = productsInput[4:len(productsInput)]
                        if productString.count(", ") == 2:
                            url, searchKey, name = productString.split(", ")
                            products.append(product(url, searchKey, name))
                            save_object(products, 'products.pkl')
                            print(Fore.WHITE + name, Fore.GREEN +
                                  "ADDED" + Fore.RESET)
                        else:
                            print(
                                Fore.WHITE + productString, Fore.RED + "IS IN THE INCORRECT FORMAT. PLEASE USE THE PROVIDED FORMAT (add url, search_key, name)" + Fore.RESET)
                    elif productsInput == "back":
                        break
                    else:
                        print(Fore.RED + "UNKNOWN COMMAND",
                              Fore.WHITE + "(" + productsInput + ")" + Fore.RESET)
            elif flow == "start":
                if not products:
                    print(Fore.RED + "NO PRODUCTS FOUND" + Fore.RESET)
                else:
                    if alertKeys is None:
                        print(Fore.YELLOW + "WARNING:", Fore.WHITE +
                              "NO KEYWORD(S) SET FOR ALERTS" + Fore.RESET)
                    if discordURL is None:
                        print(Fore.YELLOW + "WARNING:", Fore.WHITE +
                              "NO DISCORD IS LINKED" + Fore.RESET)
                    if alertKeys and discordURL is not None:
                        print(Fore.MAGENTA + "LOOKING FOR" + Fore.RESET, end=" ")
                        for keyword in alertKeys:
                            print(Fore.WHITE + keyword + Fore.RESET, end=", ")
                        print(Fore.MAGENTA + "TO NOTIFY",
                              Fore.WHITE + discordURL + Fore.RESET)
                    print(
                        Fore.GREEN + "STARTING STOCK CHECKER... (stop) TO STOP CHECKING STOCK" + Fore.RESET)
                    stopChecker = threading.Thread(target=getInput)
                    stopChecker.daemon = True
                    stopChecker.start()
                    # Checks if 'stop' has been input to the terminal, continue running the stock checker if not
                    while stopChecker.is_alive():
                        stockChecker(products, alertKeys,
                                     discordURL, stopChecker)
                    # Resets alerted status of products for previous session
                    for eachProduct in products:
                        eachProduct.alerted = False
                    save_object(products, 'products.pkl')
                    print(Fore.RED + "STOPPED STOCK CHECKER" + Fore.RESET)
            elif flow == "exit":
                quit()
            else:
                print(Fore.RED + "UNKNOWN COMMAND",
                      Fore.WHITE + "(" + flow + ")" + Fore.RESET)
    except KeyboardInterrupt:
        # Resets alerted status of products for previous session
        for eachProduct in products:
            eachProduct.alerted = False
        save_object(products, 'products.pkl')


if __name__ == '__main__':
    main()
