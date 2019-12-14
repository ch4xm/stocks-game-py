from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import atexit
import configparser


#https://stackoverflow.com/questions/19078170/python-how-would-you-save-a-simple-settings-config-file
def stock_name(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
    result = requests.get(url).json()
    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']
def stock_price(stock_choice):
    options = Options()
    options.headless = True
    #browser = webdriver.Firefox(options=options)
    #browser.implicitly_wait(10)
    #browser.get("https://finance.yahoo.com/quote/" + stock_choice)
    html = requests.get("https://finance.yahoo.com/quote/"+stock_choice)
    soup = BeautifulSoup(html.text, features="lxml")
    find = soup.find_all("span", {"class":"Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)"})
    price = float((str(find[0]).replace('<span class="Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)" data-reactid="14">', '').replace('</span>', '').replace(",", "")))
    return price
def reset_config():
    reset = open("StockProfile.ini", "w")
    lines = ["cash=10000"]
    reset.writelines(lines)
    reset.close()
def exit_handler():
    append = open("StockProfile.ini", "w")
    for key in user_stocks.items():

        append.write(key[0] + ":" + key[1] + "\n")
    append.write("cash=" + str(cash))
def write_current_dict():
    append = open("StockProfile.ini", "w")
    for key in user_stocks.items():
        append.write(key[0] + ":" + key[1] + "\n")
    append.write("cash=" + str(cash))
atexit.register(exit_handler)
'''Put the stock symbols you want updated in the "stock_symbols.txt" file. Outputs to stock_prices.txt. '''
# <editor-fold desc="Reading and writing to files">
f = open("StockProfile.ini", "r")                      #Read the file with stock symbols to update prices
settings = f.readlines()
f.close()

# </editor-fold>
user_stocks = {}
for line in settings:
    try:
        cash = float(line.split("=")[1])
    except:
        pass
try:
    cash
except:
    print("Config corrupt!")
    reset_config()
    cash = 10000
with open("StockProfile.ini") as f:
    for line in f:
       try:
           stock = line.split(":")[0].strip().rstrip()
           units = line.split(":")[1].strip().rstrip()
           user_stocks[stock] = units
       except:
           pass

'''
config = configparser.ConfigParser()
config.read("StockProfile.ini")

config.add_section("money")
config.add_section("stocks")

config.set("money", "cash", "10000")
config.set("money", "total_assets", "10000")
'''

repeat = "yes"
#stock_price(stock_choice)
while repeat == "yes":
    user_choice = input("Buy stocks, sell stocks, list money/stocks, view assets, check price of stock, or quit? (b/s/l/c/q)? ").lower()
    if user_choice == "b":
        stock_choice = input("Enter a stock symbol: ").upper()
        try:
            price = stock_price(stock_choice)
            print("The stock "+stock_choice+" costs $"+str(price)+".")
        except Exception as e:
            print(e)
            user_choice = ("Error: Invalid stock symbol! Try again? (yes/no) ")
            if user_choice.lower() == "yes":
                continue
            else:
                break
        amount_of_stock = int(input("How many stocks to purchase? (Max: "+str(cash/price)+") "))
        if amount_of_stock * price > cash:
            user_choice = ("You do not have enough money to buy "+str(amount_of_stock) +" stock(s). Restart? (yes/no) ")
            if user_choice == "yes":
                continue
            else:
                break
        if amount_of_stock * price <= cash:
            confirm = input("Are you sure? (yes/no) ")
            if confirm == "no":
                break
            elif confirm == "yes":
                cash -= float(amount_of_stock) * float(price)
                if stock_choice in user_stocks.keys():
                    user_stocks[stock_choice] = str(int(user_stocks[stock_choice]) + amount_of_stock)
                elif stock_choice not in user_stocks.keys():
                    user_stocks[stock_choice] = str(amount_of_stock)
                print("Bought "+str(amount_of_stock)+" stock(s). Your balance is now "+str(cash)) #
                write_current_dict()
    if user_choice == "s":
        stock_choice = input("Which stock to sell? ").upper()
        if stock_choice in user_stocks.keys():
            price = stock_price(stock_choice)
            amount_of_stock = int(user_stocks[stock_choice])
            if amount_of_stock <= 0:
                print("Error: You have no stocks to sell! Restarting session...")
                continue
            elif amount_of_stock > 0:
                amount_to_sell = int(input("You have "+str(amount_of_stock)+" unit(s) of the stock "+stock_choice.upper()+". How many do you want to sell? "))
                if amount_to_sell > amount_of_stock:
                    print("Error: Not enough stock to sell!")
                    continue
                elif amount_to_sell <= amount_of_stock:
                    confirm = input("You will have "+str(amount_to_sell*price+cash)+" after this transaction. Are you sure? (yes/no) ").lower()
                    if confirm == "yes":
                        amount_of_stock -= amount_to_sell
                        cash += float(amount_to_sell)*float(price)
                        user_stocks[stock_choice] = str(int(user_stocks[stock_choice]) - amount_to_sell)
                        if user_stocks[stock_choice] == "0":
                            del user_stocks[stock_choice]
                        write_current_dict()
                        print("Sold "+str(amount_to_sell)+" unit(s) of the stock "+stock_choice.upper()+". You now have $"+str(cash) +".")
                        continue
                    else:
                        continue
        else:
            print("You do not own that stock!")
    if user_choice == "q":
        break
        break
    if user_choice == "l":
        print("\nYou currently have $"+str(cash)+ " in cash.\n")
        if not user_stocks:
            print("You own no stocks.")
        else:
            for key in user_stocks.items():
                stock_value = list(key)
                print("You have "+str(key[1])+" units of the stock "+str(stock_value[0]).upper()+".")
    if user_choice == "c":
        stock_choice = input("Which stock to check price of? (e.g NVDA) ")
        print("The price of one stock of "+stock_choice+" is "+str(stock_price(stock_choice)))
    # repeat = input("Restart session? (yes/no) ").lower()
    write_current_dict()
    print("\n")

print(user_stocks)
total_stocks = 0
for key in user_stocks.items():
    total_stocks += int(key[1])
write_current_dict()
print("Session ended. You have $"+str(cash)+" in cash, and "+str(total_stocks)+" stock unit(s) in total.")


