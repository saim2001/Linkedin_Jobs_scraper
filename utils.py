import dateparser
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import warnings
import mysql.connector
from dotenv import load_dotenv
import os
warnings.filterwarnings("ignore", category=DeprecationWarning) 

load_dotenv()
#  utils - functions

# create connection
def create_db_connection():
    cnx = mysql.connector.connect(
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        host=os.getenv('HOST'),
        database=os.getenv('DATABASE')
    )
    return cnx

def create_db_cursor(cnx):
    cursor = cnx.cursor()
    return cursor

def keep_driver_open(driver):
    while True:
        pass
    return None


def waitforelemtobeclickable(by,selector,driver,t=25):
    element_clickable = EC.element_to_be_clickable((by, selector))
    element = WebDriverWait(driver, t).until(element_clickable)

    return element


def waitandclickelem(locator, selector, driver,t=15):
    if locator == "XPATH":
        element_present = EC.presence_of_element_located((By.XPATH, selector))
        element = WebDriverWait(driver, t).until(element_present)
    elif locator == "CSS":
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        element = WebDriverWait(driver, t).until(element_present)
    else:
        element_present = EC.presence_of_element_located((By.ID, selector))
        element = WebDriverWait(driver, t).until(element_present)

    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(2)




def extract_date_from_text(text):

    return dateparser.parse(text).date()




def wait_and_click(element_present, driver):
    # element_present = EC.presence_of_element_located((by, selector))
    # element = WebDriverWait(driver, t).until(element_present)
    
    driver.execute_script("arguments[0].scrollIntoView();", element_present)
    return None

def checkifelemexists(css,driver):
    try:
        # return driver.find_element_by_xpath(xpath)
        return driver.find_element(By.CSS_SELECTOR,css)
    except:
        return None


def wait_for_element_to_load(by, selector, driver,t=25):
    element_present = EC.presence_of_element_located((by, selector))
    element = WebDriverWait(driver, t).until(element_present)

    return element

def wait_for_elements_to_load(by, selector, driver,t=25):
    element_present = EC.presence_of_all_elements_located((by, selector))
    element_lst = WebDriverWait(driver, t).until(element_present)
    return element_lst

def scroll_to_half(driver):
    driver.execute_script(
        "window.scrollTo({top : Math.ceil(document.body.scrollHeight/2), behavior : 'smooth'});"
    )
    time.sleep(4)
    
    # driver.execute_script(
        # "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
    # )

def scroll_to_top(driver):
    driver.execute_script(
        "window.scrollTo({top:-document.body.scrollHeight,behavior:'smooth'});"
    )
    time.sleep(4)
    # driver.execute_script(
    #     "window.scrollTo(0, 0);"
    # )

def scroll_to_bottom(driver):
    driver.execute_script(
        "window.scrollTo({top:document.body.scrollHeight,behavior:'smooth'});"
    )
    time.sleep(5)

    # driver.execute_script(
    #     "window.scrollTo(0, document.body.scrollHeight);"
    # )

def page_not_found(driver):
    """ function to manage 404 page """
    for _ in range(3):
        if "Page not found" in driver.page_source:
            driver.refresh()
            time.sleep(3)
        else:
            break

def teardown(driver):
    # driver.close()
    driver.quit()
    print("Driver successfully closed")

def click_home():
    waitandclickelem("CSS","nav>ul>li:first-child>a")
    time.sleep(4)




def search_by_position(position, location,driver):
    driver.find_element(By.CSS_SELECTOR,"input[placeholder='Search']").click()
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR,"input[placeholder='Search']").send_keys(position)
    time.sleep(4.5)
    driver.find_element(By.CSS_SELECTOR,"input[placeholder='Search']").send_keys(Keys.ENTER)
    time.sleep(6)

    scroll_to_half()
    scroll_to_bottom()
    scroll_to_top()

    time.sleep(5)

    wait_and_click(By.XPATH, "//ul[contains(@class,'filter-list')]/li//button[contains(.,'People')]")    # select people tab
    time.sleep(4)

    wait_and_click(By.XPATH, "//ul[contains(@class,'filter-list')]/li//button[contains(.,'Locations')]")   # select location tab
    time.sleep(3)

    driver.find_element(By.XPATH, "//ul[contains(@class,'filter-list')]/li//input[contains(@placeholder,'location')]").send_keys(location)   # send location name
    time.sleep(4)

    wait_and_click(By.CSS_SELECTOR, "div[role='listbox'] div[role='option']:first-child")    # select 1st suggestion
    time.sleep(3)

    wait_and_click(By.XPATH, "//ul[contains(@class,'filter-list')]/li//div[contains(@id,'locations-filter')]//button[contains(.,'Show results')]")   # select show results 
    time.sleep(5)

    scroll_to_half()
    scroll_to_bottom()
    scroll_to_top()
    time.sleep(5)


def send_connect_msg(selector, name, connect_msg,driver):
    """ function to send connect msg """
    selector.click()
    time.sleep(4)

    try:
        wait_and_click(By.CSS_SELECTOR,"button[aria-label*='Other']")
        time.sleep(1)

        wait_and_click(By.CSS_SELECTOR, "div[id*='modal'] button[aria-label*='Connect']")
        time.sleep(1)
    except:
        pass

    wait_and_click(By.CSS_SELECTOR, "button[aria-label*='note']")    
    time.sleep(2)

    driver.find_element(By.TAG_NAME, "textarea").send_keys(connect_msg.format(first_name=name))   # msg data
    time.sleep(3)

    wait_and_click(By.CSS_SELECTOR, "button[aria-label*='Send']")




