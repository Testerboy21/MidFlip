'''
A simple machine learning climber for towers that goes off of the previous game's
successful guesses. I had the idea to mirror the guesses to try to ward off bloxflip's
tower rigging (if they do).
'''

import sys, os, scraper, random, json

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException

sys.path.append("..")

from assets import *

config = json.load(open(os.path.abspath("config.json"), "r"))

browser = scraper.get_browser()

scraper.login(browser, config["auth"])

browser.refresh()
browser.fullscreen_window()

highest_clicked = []
button_xpaths = []

recent_clicks = []

in_bet = False
choosing_random = False
mirrored = False

count = 0

scraper.click_button(browser, assets["Towers"]["sidebar button"])
scraper.clear_data(browser, assets["Towers"]["bet amount"])
scraper.send_key(browser, assets["Towers"]["bet amount"], config["towers_bet_amount"])

scraper.click_button(browser, scraper.get_difficulty(browser))

grid = scraper.load_grid(browser)

def change_string(string, index, new_string):
    return string[:index] + new_string + string[index+1:]

def get_button_choice(browser, choice=None):
    global choosing_random
    
    active_row = scraper.get_active_row(browser)
    
    for a in range(len(grid)):
            if active_row == grid[a][0]:
                for b in grid[a]: # Get the active row
                    if type(b) == list: # Get the individual buttons
                        for c in b:
                            if type(c) != str: # Append button clicks for comparing
                                highest_clicked.append(c)

                                if len(highest_clicked) == 3: # Wait until all the buttons are in
                                    for d in grid[a]:
                                        if type(d) == list:
                                            for e in d:
                                                if max(highest_clicked) == e:
                                                    highest_clicked.clear()
                                                    highest_clicked.append(e)

                                                    if all(f == 0 for f in highest_clicked): # Just pick a random button if I have no data
                                                        choosing_random = True
                                                    else:
                                                        choosing_random = False
                            else:
                                button_xpaths.append(c)

                if choosing_random:
                    random_button = random.choice(button_xpaths)
                    choice = random_button

                    button_xpaths.clear()
                else:

                    # Choose the most successfully clicked
                    for g in grid[a]:
                        if type(g) == list:
                            if highest_clicked[0] in g:
                                choice = g[0]

    return choice

def bet():
    global in_bet, count, mirrored
    
    choice = get_button_choice(browser)
    
    lost = scraper.has_lost_in_towers(browser, assets["Towers"]["tower"] + "/div/div/div") # "/div/div/div" to access all the buttons under the entire tower
    tower_length = scraper.get_number_of_elements(browser, assets['Towers']['tower'], "./div")

    if not in_bet:
        scraper.click_button(browser, assets["Towers"]["new game"])
        
        in_bet = True
    
    if in_bet:
        if choice:
            if mirrored:
                button = int(choice[len(choice) - 2])

                if config["difficulty"] != "Normal":
                    if button == 3:
                        button = button - 2
                    else:
                        if button == 1:
                            button = button + 2
                        else:
                            if button == 2: # Middle button stays the same
                                pass
                else:
                    if button == 1:
                        button = button + 1
                    else:
                        if button == 2:
                            button = button - 1
                    
                button = str(button)

                choice = change_string(choice, len(choice) - 2, button)
            else:
                pass
            
            try:
                scraper.click_button(browser, choice)
            except ElementClickInterceptedException:
                print(choice)

            recent_clicks.append(choice) # Get clicks for when I lose

            count += 1
        
        for h in grid:
            for i in h:
                if type(i) == list:
                    if lost:
                        if recent_clicks[len(recent_clicks) - 1] in i:
                            if i[1] > 0: # Decrement the button that made us lose
                                i[1] = i[1] - 1
                    else:
                        i[1] = i[1] + 1 # Increment the button that made us win
        
        if lost or count >= tower_length:
            scraper.click_button(browser, assets["Towers"]["new game"])
            
            count = 0

            if not mirrored:
                mirrored = True
            else:
                mirrored = False

            in_bet = False
            
while True:
    if not scraper.isBrowserAlive(browser):
        os.system(f"taskkill /im geckodriver.exe /f")
        
        break
    else:
        bet()