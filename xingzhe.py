from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import time
import requests
import datetime

options = Options()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
driver = webdriver.Chrome(options=options)
driver.get("https://imxingzhe.com/user/login")

username = '13730916126'
password = 'Zc19990816'

username_input = driver.find_element("name", "account")
username_input.send_keys(username)

password_input = driver.find_element("name", "password")
password_input.send_keys(password)

checkbox = driver.find_element("id", "agree")
actions = ActionChains(driver)
actions.move_to_element(checkbox).click().perform()

# WebDriverWait(driver, 10).until(lambda x: x.find_element("id", "submit"))

# button = driver.find_element_by_xpath("//button[@type='submit']")
# button.click()
login_button = driver.find_element("xpath", "//button[@type='submit']")
login_button.click()
time.sleep(3)

cookies = driver.get_cookies()
cookies = {cookie['name']: cookie['value'] for cookie in cookies}
response = requests.get('https://www.imxingzhe.com/api/v4/account/get_user_info/', cookies=cookies)
resp_json = response.json()
user_id = resp_json['userid']



def download_file(url, cookies, save_path):
    response = requests.get(url, cookies=cookies)
    response.raise_for_status()
    with open(save_path, 'wb') as file:
        file.write(response.content)

def get_previous_month(month, year):
    if month == 1:
        previous_month = 12
        previous_year = year - 1
    else:
        previous_month = month - 1
        previous_year = year

    return previous_month, previous_year


def get_latest_record(user_id, cookies):
    now = datetime.datetime.now()
    year, month = now.year, now.month
    while True:
        url = f'https://www.imxingzhe.com/api/v4/user_month_info/?user_id={user_id}&year={year}&month={month}'
        response = requests.get(url, cookies=cookies)
        resp_json = response.json()
        if len(resp_json['data']['wo_info']) == 0:
            month, year = get_previous_month(month, year)
            print(f'empty: year {year}, month {month}')
            continue
        return resp_json['data']['wo_info'][0]

last_record = get_latest_record(user_id, cookies)
title = last_record['title']
record_id = last_record['id']

url = f'https://www.imxingzhe.com/xing/{record_id}/gpx/'
save_path = f'gpx/xingzhe_{record_id}.gpx'
print(f'download {title} to {save_path}')
download_file(url, cookies, save_path)