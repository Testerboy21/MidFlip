import os, sys, json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.common.action_chains import ActionChains

sys.path.append("..")

from assets import *

config = json.load(open(os.path.abspath("config.json"), "r"))

# os.environ['GH_TOKEN'] = config["gh_token"]

options = Options()

options.set_preference("browser.privatebrowsing.autostart", True)
options.headless = True

def get_browser():
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options, service_log_path=os.path.devnull)
    browser.get(config["bloxflip_link"])

    return browser

def isBrowserAlive(driver):
   try:
      driver.current_url
      
      return True
   except:
        return False

def load_data(browser, path: str):
    data = browser.find_elements(By.XPATH, path)

    return data

def clear_data(browser, *path: str):
    for p in path:
        data = browser.find_element(By.XPATH, p)

        data.clear()

def click_button(browser, path: str):
    data = WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.XPATH, path)))

    element = browser.find_element(By.XPATH, path)

    actions = ActionChains(browser)
    actions.move_to_element(element).perform()

    return data.click()

def login(browser, authentication):    
    return browser.execute_script(f'''localStorage.setItem("_DO_NOT_SHARE_BLOXFLIP_TOKEN", "{authentication}")''')

def send_key(browser, path: str, input):
    data = WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.XPATH, path)))

    click_button(browser, path)
    
    data.clear()

    element = browser.find_element(By.XPATH, path)

    actions = ActionChains(browser)
    actions.move_to_element(element).perform()

    return data.send_keys(str(input))

'''Crash funcs'''

# https://stackoverflow.com/a/12150013/15324861
def game_started(browser):
    try:
        browser.find_element(By.XPATH, assets["Crash"]["rocket"])
        
    except NoSuchElementException:
        return False
        
    return True
                        
def game_crashed(browser):
    try:        
        data = browser.find_element(By.XPATH, assets["Crash"]["rocket"]).get_attribute("class")

        if "crash_crashGameChartRocket__ugFoI crash_isCrashed" in data:
            return True

    except NoSuchElementException:
        pass

    return False

def get_multiplier(browser, crashed, replaced=None):
    data = load_data(browser, assets["Crash"]["multiplier"])

    for d in data:
        text = d.text

        if not crashed:
            if text == "0.00x" or text == "1.00x":
                pass
            else:
                starting = text.find("+")

                if starting != -1:
                    text = text[:starting]
        
                    replaced = text.replace('x', '')
                else:
                    ending = text.find("Current payout")

                    if ending != -1:
                        text = text[:ending]
                        
                        replaced = text.replace('x', '')
        
    if replaced:               
        return float(replaced)

def get_player_count(browser, started, text=None):
    data = load_data(browser, assets["Crash"]["player count"])
    
    if started:
        for d in data:
            text = d.text
            text = ''.join(filter(lambda i: i.isdigit(), text))

    if text:
        return int(text)

def get_player_list(browser, started, crashed, counter, data=None):
    if started:
        data = browser.find_element(By.XPATH, assets["Crash"]["player list"]).get_attribute("textContent")

    if data:
        data = data.split()

        for x in data:
            if "X" and "." in x:
                counter += 1

                if crashed:
                    counter = 0

    return counter

def get_recent_crash_type(browser, type=None):
    data = load_data(browser, assets["Crash"]["history"])

    for d in data:
        type = d.get_attribute("class")
        type = type.replace("gameLatestItem", "")

    return type # Neutral, Yellow, Blue

def has_lost_in_crash(browser, started, crashed):
    data = browser.find_elements(By.XPATH, assets["Crash"]["multiplier"])

    if started and crashed:
        for d in data:
            outline = d.value_of_css_property('outline')
                    
            starting = outline.find("none")
            outline = outline[:starting]

            if outline.find("rgb(5, 211, 221)") == -1:
                return True

        return False

'''Tower funcs'''

# https://stackoverflow.com/a/50915437/15324861
def get_number_of_elements(browser, main_element_xpath, sub_element):
    data = browser.find_element(By.XPATH, main_element_xpath)

    return len(data.find_elements(By.XPATH, sub_element))

def load_grid(browser):
    array = []
    
    tower_length = get_number_of_elements(browser, assets['Towers']['tower'], "./div")

    for x in reversed(range(tower_length)):
        x += 1

        row = assets['Towers']['tower'] + f"/div[{x}]"

        array.append([row])

    for y in range(len(array)):
        buttons = get_number_of_elements(browser, array[y][0], "./div")

        for z in range(buttons):
            z += 1

            array[y].append([array[y][0] + f"/div[{z}]", 0])
    
    return array

def get_active_row(browser, active_row=None):
    tower_length = get_number_of_elements(browser, assets['Towers']['tower'], "./div")

    for x in range(tower_length):
        x += 1

        row = assets['Towers']['tower'] + f"/div[{x}]"
        data = load_data(browser, row)

        for d in data:
            class_name = d.get_attribute('class')

            if "Active" in class_name:
                active_row = row
    
    return active_row

def has_lost_in_towers(browser, row, type=None):
    data = load_data(browser, row + "/div/div")

    for d in data:
        type = d.get_attribute("class")
        
        if "Cross" in type and not "Star" in type:
            return True

    return False

def get_difficulty(browser, difficulty=None):
    difficulty_length = get_number_of_elements(browser, assets["Towers"]["difficulty bar"], "./button")
    
    for e in range(difficulty_length):
        e += 1

        difficulty_button = f"/html/body/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/div[3]/div/button[{e}]"

        difficulty_text = browser.find_element(By.XPATH, difficulty_button).get_attribute("textContent")

        if difficulty_text.lower() == config["difficulty"].lower():
            difficulty = difficulty_button
    
    return difficulty