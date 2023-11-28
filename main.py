from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import requests

import multiprocessing
from multiprocessing import Pool
from itertools import product

from csvHandler import __save_csv
from models import Items
import re


def get_pages_number(url: str):
    driver = get_page(url + "?page=25")

    # получаем ссылку на первый попавшийся товар
    result = (driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div/div[2]/div/div[6]/div/a[8]").get_attribute("href"))
    regex = "(?<=page=).+"
    pages_num = re.search(regex, result)[0]
    driver.close()
    return pages_num


def get_page(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        print("Инета нет")
        exit()

    chrome_options = ChromeOptions()
    # chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.get(url)
    return driver


def get_item_links(url: str) -> list:
    driver = get_page(url)
    last_len = 0
    while True:
        result = driver.find_elements(By.CLASS_NAME, "product-card__link")
        ActionChains(driver).move_to_element(result[-1]).perform()
        if len(result) == last_len:
            break
        last_len = len(result)
    item_links = [item.get_attribute("href") for item in result]
    return item_links


def get_basket_num(item_id, vol, part):
    i = 1
    while True:
        basket_num = f'0{i}' if i // 10 == 0 else str(i)
        response = requests.get(
            f'https://basket-' + basket_num + '.wb.ru/vol' + vol + '/part' + part + '/' + item_id + '/info/ru/card.json')
        if response.status_code == 200:
            return basket_num
        i += 1


def get_chars_dict(link: str):
    item_id = get_item_id(link)
    vol = item_id[:len(item_id) - 5]
    part = item_id[:len(item_id) - 3]

    basket_num = get_basket_num(item_id, vol, part)
    response = requests.get(
        f'https://basket-' + basket_num + '.wb.ru/vol' + vol + '/part' + part + '/' + item_id + '/info/ru/card.json')

    chars_dict = response.json()["options"]

    full_chars_dict = {}
    for item in chars_dict:
        full_chars_dict[item["name"]] = item["value"]
    return full_chars_dict


def get_filter_info(url: str) -> list:
    driver = get_page(url)

    # получаем ссылку на первый попавшийся товар
    first_item_link = driver.find_element(By.CLASS_NAME, "product-card__link").get_attribute("href")
    driver.close()
    filter_list = list(get_chars_dict(first_item_link).keys())
    return filter_list


def get_item_id(link: str):
    regex = "(?<=catalog\/).+(?=\/)"
    item_id = re.search(regex, link)[0]
    return item_id


def parse_item_chars(link: str, filter_list: list):
    filtered_chars_list = []
    item_id = get_item_id(link)
    response = requests.get(f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=123585774&spp=25&nm={item_id}")
    item_main_info = Items.model_validate(response.json()["data"])
    for item_info in item_main_info.products:
        filtered_chars_list.append(item_info.id)
        filtered_chars_list.append(item_info.name)
        filtered_chars_list.append(item_info.salePriceU)
        filtered_chars_list.append(item_info.brand)
        filtered_chars_list.append(item_info.sale)
        filtered_chars_list.append(item_info.rating)
        filtered_chars_list.append(item_info.volume)

    full_chars_dict = get_chars_dict(link)
    for item in filter_list:
        try:
            filtered_chars_list.append(full_chars_dict[item].replace(',', ';'))
        except:
            filtered_chars_list.append("NaN")
    __save_csv(filtered_chars_list)


def main_parse(url: str, filter_list: list):
    links = get_item_links(url)
    with Pool(multiprocessing.cpu_count()) as p:
        p.starmap(parse_item_chars, product(links, [filter_list]))
