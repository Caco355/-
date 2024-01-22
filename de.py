import subprocess
import time
import re
import urllib.parse
import random
import openpyxl
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def extract_fakeid(page_source):
    fakeid_pattern = r'"fakeid":"([^"]+)"'
    match = re.search(fakeid_pattern, page_source)
    if match:
        return match.group(1)
    return None

def wait_for_element_disappear(driver):
    try:
        element = WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'new-creation__menu-item.red-dot'))
        )
        print("指定元素消失.")
        # 元素消失后等待一段时间（例如，等待3秒）
        time.sleep(30)
        driver.minimize_window()
    except TimeoutException:
        print("等待指定元素消失超时.")

def wait_for_login(driver):
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'weui-desktop-person_info')))
        print("登录成功.")
        return True
    except TimeoutException:
        return False

def get_token_from_url(driver):
    url = driver.current_url
    match = re.search(r'token=(\w+)', url)
    if match:
        return match.group(1)
    return None

def get_cookies(driver):
    return driver.get_cookies()

def get_user_agent(driver):
    return driver.execute_script("return navigator.userAgent;")

#def print_cookies(cookies):
    #for cookie in cookies:
        #print(f"Cookie Name: {cookie['name']}, Value: {cookie['value']}")

def main():
    chrome_options = Options()
    # 如果需要其他选项，比如无头模式，可以在这里添加
    # chrome_options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('https://mp.weixin.qq.com/')
    if wait_for_login(driver):
        print("登录成功.")
        token = get_token_from_url(driver)
        if token:
            print("找到Token:")
        else:
            print("未找到Token")

        cookies = get_cookies(driver)
        #print("Cookies:")
        #print_cookies(cookies)

        user_agent = get_user_agent(driver)
        print("User Agent:", user_agent)

        cookies_value = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

        search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'

        excel_file = 'weinames.xlsx'
        wb = openpyxl.load_workbook(excel_file)
        sheet = wb.active

        fakeid_list = []

        for row in sheet.iter_rows(min_row=2, values_only=True):
            for query in row:
                print(f"当前查询值: {query}")

                query_id = {
                    'action': 'search_biz',
                    'token': token,
                    'lang': 'zh_CN',
                    'f': 'json',
                    'ajax': '1',
                    'random': random.random(),
                    'query': query,
                    'begin': '0',
                    'count': '5'
                }

                full_url = search_url + urllib.parse.urlencode(query_id)

                #print("完整的URL:", full_url)

                driver.get(full_url)
                driver.implicitly_wait(10)
                page_source = driver.page_source

                fakeid = extract_fakeid(page_source)
                if fakeid:
                    print(f"找到FakeID for {query}")
                    fakeid_list.append((fakeid, query))
                else:
                    print(f"未找到FakeID for {query}")

        with open('fakeid.txt', 'w') as f:
            for fakeid, query in fakeid_list:
                f.write(f"FakeID: {fakeid}, 查询值: {query}\n")

        for fakeid, query in fakeid_list:
            gzh_name = query
            g_json_command = ["python", "g_json.py", cookies_value, user_agent, fakeid, token, gzh_name]
            try:
                subprocess.run(g_json_command, check=True)
                print(f"已成功运行 g_json.py 文件，使用的 FakeID 为: {fakeid}")
            except subprocess.CalledProcessError as e:
                print(f"运行 g_json.py 文件时出错: {e}")

        pachong_command = ["python", "pachong.py"]
        try:
            subprocess.run(pachong_command, check=True)
            print("已成功运行 pachong.py 文件")
        except subprocess.CalledProcessError as e:
            print(f"运行 pachong.py 文件时出错: {e}")

        matchchar_command = ["python", "matchchar.py"]
        try:
            subprocess.run(matchchar_command, check=True)
            print("已成功运行 matchchar.py 文件")
        except subprocess.CalledProcessError as e:
            print(f"运行 matchchar.py 文件时出错: {e}")

        # Close the browser when the loop is finished
        driver.quit()

if __name__ == "__main__":
    main()
