#!/bin/python3

from bs4 import BeautifulSoup
import requests
import pandas as pd
import re




url = "https://www.autoscout24.it/lst/ford?sort=standard&desc=0&ustate=N%2CU&cy=I&atype=C"

HEADERS = {
    'accept': '*/*',
    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85'
                  'Safari/537.36 '
}


def transform_to_float(a):
    """elabora i dati dei consumi"""
    
    a = a.split()[0].replace(",", ".")
    if a == '-/-':
        return 0
    else:
        return float(a)


def get_html(url, params=''):
    r = requests.get(url, headers=HEADERS, params=params).text
    return r


def engine_power(s):
    
    pattern = r'\d+'
    n = [int(i) for i in re.findall(pattern, s)]
    if len(n) != 2:
        return [0, 0]
    return n


def price_processing(s):
    """Price processing"""
    a = s.split()[1].split(",")[0].replace(".", "")
    return float(a)


def km_average(a):
    a = a.split()[0].replace('.','')
    if a == '-':
        return 0
    return int(a)
    

def get_content2(url):
    html = get_html(url)
    parser = BeautifulSoup(html, 'html.parser')
    items = parser.find_all('div', class_="cl-list-element cl-list-element-gap")
    data = {
        'kw': [],
        'cv': [],
        'marchio': [],
        'price Euro': [],
        'marchio': [],
        'motore': [],
        'kilometri': [],
        'immatricolazione': [],
        'consumo': [],
        'link': []
        }
    for i in items:
        dati_diversi = [item for item in i.find('div', class_="cldt-summary-vehicle-data").get_text().split("\n") if item != '']

        data['price Euro'].append(price_processing(i.find(class_="cldt-price sc-font-xl sc-font-bold").get_text().split('\n')[1]))
        data['marchio'].append(i.find(class_="cldt-summary-makemodel sc-font-bold sc-ellipsis").get_text())
        data['motore'].append(dati_diversi[6])
        data['kilometri'].append(km_average(dati_diversi[0]))
        data['kw'].append(engine_power(dati_diversi[2])[0])
        data['cv'].append(engine_power(dati_diversi[2])[1])
        data['immatricolazione'].append(dati_diversi[1])
        data['consumo'].append(transform_to_float(dati_diversi[7]))
        data['link'].append("https://www.autoscout24.it" +i.find('a').get("href"))
    df = pd.DataFrame(data)
    return df


def get_len(html):
    html = get_html(url)
    parser = BeautifulSoup(html, 'html.parser')
    items = parser.find_all("a", href="?&sort=standard&desc=0&ustate=N%2CU&size=20&cy=I&atype=C&page")
    for i in items:
        print(i)


def run():
    car = input('macchina:  ')

    lnk = f"https://www.autoscout24.it/lst/{car}?sort=standard&desc=0&ustate=N%2CU&size=20&page="
    df = pd.DataFrame({
            'price Euro': [],
            'marchio': [],
            'motore': [],
            'kilometri': [],
            'kw': [],
            'cv': [],
            'immatricolazione': [],
            'consumo': [],
            'link': []
            })
    for i in range(1, 21):
        print(f'parse page {i}')
        # lst2 += get_content2(lnk + str(i))
        df = pd.concat([df, get_content2(lnk + str(i))], ignore_index=True)

    car = '_'.join(car.split("/"))
    df.to_csv(f"{car}.csv")
# print(df)
# dg = get_content2(url)
# print(dg,22)



"""
https://www.autoscout24.it/lst/citroen?&sort=standard&desc=0&ustate=N%2CU&size=20&atype=C&page=2
?&sort=standard&desc=0&ustate=N%2CU&size=20&cy=I&atype=C&page=
"?&amp;sort=standard&amp;desc=0&amp;ustate=N%2CU&amp;size=20&amp;atype=C&amp;page="
https://www.autoscout24.it/lst/citroen/berlingo?sort=standard&desc=0&ustate=N%2CU&size=20&page=1&atype=C&fc=2&qry=&
https://www.autoscout24.it/lst/audi?sort=price&desc=0&superdeal=true&ustate=N%2CU&size=20&page=1&cy=I&atype=C&fc=8&qry=&
https://www.autoscout24.it/lst/bmw?sort=standard&desc=0&ustate=N%2CU&size=20&page=1&atype=C&fc=1&qry=&
"""
