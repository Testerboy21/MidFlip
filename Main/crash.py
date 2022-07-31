'''
An automatic better for crash that follows a gate-like system where
the percent of players cashed out has to equal a successful crash's 
player count percentage that is logged previously.
'''

import os, sys, scraper, time, json

from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import StaleElementReferenceException

sys.path.append("..")

from assets import *

config = json.load(open(os.path.abspath("config.json"), "r"))

loss_counter = 0
player_counter = 0

on_launch = False
in_bet = False
cleared = False

temp_gate = []
final_gate = []

game_status = []

browser = scraper.get_browser()

scraper.login(browser, config["auth"])

browser.refresh()
browser.fullscreen_window()

# https://stackoverflow.com/a/43623393/15324861
def remove_dup(a):
   i = 0
   while i < len(a):
      j = i + 1
      while j < len(a):
         if a[i] == a[j]:
            del a[j]
         else:
            j += 1
      i += 1

# https://stackoverflow.com/a/6190236/15324861
def get_decimal_place(float_num):
    return round(float_num - int(float_num), 3) * 10

def load_gate(get_recent_crash_type, crashed, current_multiplier, player_list, player_count):
    global temp_gate, final_gate, cleared

    if current_multiplier:
        # Follows the crash multiplier by multiplies of 2
        decimal = get_decimal_place(current_multiplier)
        decimal *= 10

        # Get multiplies of 2
        if (decimal / 10) % 2 == 0 and decimal % 10 == 0 and current_multiplier > 1 or current_multiplier > 1 and decimal == 0 or current_multiplier == 1.1:
            temp_gate.extend([player_count, current_multiplier, round(player_list / player_count, 2)])

            remove_dup(temp_gate)
            
            # Remove extra percentage that gets appended for some reason (bad code lol)
            for x in range(len(temp_gate)):
                if len(temp_gate) > 3:
                    if temp_gate[x] < 1 and temp_gate[x-1] < 1:
                        temp_gate.remove(temp_gate[x])
                    else:
                        pass
    if crashed:
        if get_recent_crash_type:
            
            # Crash types to log
            if "Yellow" in get_recent_crash_type or "Blue" in get_recent_crash_type:
                
                # Clear the gate ONCE each time. (What if there's another crash of the same type?)
                if not cleared:
                    final_gate.clear()

                    cleared = True

                for x in temp_gate:
                    final_gate.append(x)

                    remove_dup(final_gate)

        temp_gate.clear()

    else:
        cleared = False
    
    return final_gate

def bet():
    global on_launch, in_bet, loss_counter, player_counter, CASHOUT_GOAL

    crashed = scraper.game_crashed(browser)
    started = scraper.game_started(browser)

    current_multiplier = scraper.get_multiplier(browser, crashed)

    player_count = scraper.get_player_count(browser, started)
    player_list = scraper.get_player_list(browser, started, crashed, player_counter)

    crash_type = scraper.get_recent_crash_type(browser)

    gate = load_gate(crash_type, crashed, current_multiplier, player_list, player_count)

    if not on_launch:
        scraper.click_button(browser, assets["Crash"]["sidebar button"])
        scraper.clear_data(browser, assets["Crash"]["bet amount"], assets["Crash"]["auto cashout"])

        on_launch = True
    
    if not in_bet:
        if gate and not crashed and not started:
            scraper.send_key(browser, assets["Crash"]["bet amount"], config["crash_bet_amount"])
            scraper.click_button(browser, assets["Crash"]["cashout"])

            in_bet = True
    
    if in_bet:
        if current_multiplier and player_count:
            decimal = get_decimal_place(current_multiplier)
            decimal *= 10

            # Player count check (I had an idea to only hold on crashes if the current player count is less than the gate's, but it didn't work so lol)
            '''for x in range(len(gate)):
                gate[x] = str(gate[x])
                
                if gate[x].find(".") == -1:
                    gate[x] = int(gate[x])

                    if player_count <= gate[x]:
                        pass
                    else:
                        if player_count > gate[x]:
                            if current_multiplier > 1:
                                gate[x] = str(gate[x])

                                scraper.click_button(browser, assets["Crash"]["cashout"])
                                
                                if gate[x].find(".") != -1:
                                    gate[x] = float(gate[x])
                                else:
                                    gate[x] = int(gate[x])

                                in_bet = False
                else:
                    gate[x] = float(gate[x])'''

            # Compare current crash multiplier with the gate's multiplier (multiples of 2)
            if (decimal / 10) % 2 == 0 and decimal % 10 == 0 and current_multiplier > 1 or current_multiplier > 1 and decimal == 0: # or current_multiplier == 1.1
                for x in range(len(gate)):
                    if current_multiplier == gate[x-1]:
                        current_percent = round(player_list / player_count, 2)

                        # For some reason the multiplier percentage goes above 1 (bad code lol) so I just set it 0.01 behind the current percent once it's above 2 lol
                        if current_multiplier > 2 and gate[x] > 1:
                            gate[x] = current_percent - 0.01

                        if current_percent < gate[x] and not current_multiplier >= 2:
                            scraper.click_button(browser, assets["Crash"]["cashout"])
                            
                            in_bet = False
                        else:
                            pass
            
            if current_multiplier >= CASHOUT_GOAL:
                scraper.click_button(browser, assets["Crash"]["cashout"])

                CASHOUT_GOAL = 3 # ik it's not dynamic but it's temporary (it never became dynamic)

                in_bet = False

        if crashed:
            lost = scraper.has_lost_in_crash(browser, started, crashed)

            if lost:
                CASHOUT_GOAL += 1
                loss_counter += 1

                gate.clear()

                if loss_counter >= config["stop_loss"]:
                    time.sleep(config["timeout"])

                    loss_counter = 0
                
            in_bet = False
            
while True:
    if not scraper.isBrowserAlive(browser):
        os.system(f"taskkill /im geckodriver.exe /f")
        
        break
    else:
        try:
            bet()

        except StaleElementReferenceException:
            pass