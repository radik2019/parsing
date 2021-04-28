#!/bin/python3

from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import multiprocessing
import threading
lock = multiprocessing.Lock()

HOST = "https://www.autoscout24.it"

url = "https://www.autoscout24.it/lst/ford?sort=standard&desc=0&ustate=N%2CU&cy=I&atype=C"

HEADERS = {
    'accept': '*/*',
    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85'
                  'Safari/537.36 '
}
EMISSIONI_CO2 = 'Emissioni di CO2I dati di consumi ed emissioni per le auto usate si intendono riferiti al ciclo NEDC. Per le auto nuove, a partire dal 16.2.2021, iI rivenditore deve indicare i valori relativi al consumo di carburante ed emissione di CO2 misurati con il ciclo WLTP. Il rivenditore deve rendere disponibile nel punto vendita una guida gratuita su risparmio di carburante e emissioni di CO2 dei nuovi modelli di autovetture. Anche stile di guida e altri fattori non tecnici influiscono su consumo di carburante e emissioni di CO2. Il CO2 è il gas a effetto serra principalmente responsabile del riscaldamento terrestre.'
CONSUMO = 'Consumo carburante:I dati di consumi ed emissioni per le auto usate si intendono riferiti al ciclo NEDC. Per le auto nuove, a partire dal 16.2.2021, iI rivenditore deve indicare i valori relativi al consumo di carburante ed emissione di CO2 misurati con il ciclo WLTP. Il rivenditore deve rendere disponibile nel punto vendita una guida gratuita su risparmio di carburante e emissioni di CO2 dei nuovi modelli di autovetture. Anche stile di guida e altri fattori non tecnici influiscono su consumo di carburante e emissioni di CO2. Il CO2 è il gas a effetto serra principalmente responsabile del riscaldamento terrestre.'

CONSUMO_ELETTRICO = 'Consumo di energia elettricaI dati di consumi ed emissioni per le auto usate si intendono riferiti al ciclo NEDC. Per le auto nuove, a partire dal 16.2.2021, iI rivenditore deve indicare i valori relativi al consumo di carburante ed emissione di CO2 misurati con il ciclo WLTP. Il rivenditore deve rendere disponibile nel punto vendita una guida gratuita su risparmio di carburante e emissioni di CO2 dei nuovi modelli di autovetture. Anche stile di guida e altri fattori non tecnici influiscono su consumo di carburante e emissioni di CO2. Il CO2 è il gas a effetto serra principalmente responsabile del riscaldamento terrestre.'

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
    a = a.split()[0].replace('.', '')
    if a == '-':
        return 0
    return int(a)


def get_csv_file(url, number_thread):

    global data
    print(f"runing parsing page {number_thread}")
    html = get_html(url)
    parser = BeautifulSoup(html, 'html.parser')
    items = parser.find_all(
        'div', class_="cl-list-element cl-list-element-gap")

    # lock.acquire()
    for i in items:
        dati_diversi = [item for item in i.find(
            'div', class_="cldt-summary-vehicle-data").get_text().split("\n") if item != '']
        data['price Euro'].append(price_processing(
            i.find(class_="cldt-price sc-font-xl sc-font-bold").get_text().split('\n')[1]))
        data['marchio'].append(
            i.find(class_="cldt-summary-makemodel sc-font-bold sc-ellipsis").get_text())
        data['motore'].append(dati_diversi[6])
        data['kilometri'].append(km_average(dati_diversi[0]))
        data['kw'].append(engine_power(dati_diversi[2])[0])
        data['cv'].append(engine_power(dati_diversi[2])[1])
        data['immatricolazione'].append(dati_diversi[1])
        data['consumo'].append(transform_to_float(dati_diversi[7]))
        # lock.release()
        get_data_from_link("https://www.autoscout24.it" + i.find('a').get("href"))

    
    print(f"finishing parsing page {number_thread}")


def get_data_from_link(link: str) -> dict:
    global data
    html = get_html(link)
    parser = BeautifulSoup(html, 'html.parser')
    items = parser.find_all("div", class_='sc-grid-row')
    
    # lock.acquire()


    for i in items:
        a = i.find('dd')
        if i.find('dd') != None:
            list_data = [d.get_text().strip() for d in i.find_all("dd")]
            list_title = [k.get_text() for k in i.find_all("dt")]
            for i in range(len(list_title)):
                if list_title[i] == EMISSIONI_CO2:
                    list_title[i] = 'Emissioni_CO2'
                elif list_title[i] == CONSUMO:
                    list_title[i] = 'Consumo'
                elif list_title[i] == CONSUMO_ELETTRICO:
                    list_title[i] = 'Consumo elettrico'
            for item in range(len(list_title)):
                try:
                    data[list_title[item]].append(list_data[item])
                except KeyError:
                    data[list_title[item]] = [list_data[item]]

            # lock.release()
            return

def run_proc(car):

    lnk = f"https://www.autoscout24.it/lst/{car}?sort=standard&desc=0&ustate=N%2CU&size=20&page="
    thr = []
    for i in range(1, 10):
        # get_csv_file(lnk + str(i),i)
        t = multiprocessing.Process(target=get_csv_file, args=(lnk + str(i),i))
        thr.append(t)
        t.start()
    for k in range(len(thr)):

        thr[k].join()

    print(len(data))
    df2 = pd.DataFrame.from_dict(data, orient='index')
    df2 = df2.transpose()
    car = '_'.join(car.split("/"))
    df2.to_csv(f"{car}.csv")


def run_thr(car):

    lnk = f"https://www.autoscout24.it/lst/{car}?sort=standard&desc=0&ustate=N%2CU&size=20&page="
    thr = []
    for i in range(1, 10):
        # get_csv_file(lnk + str(i),i)
        t = threading.Thread(target=get_csv_file, args=(lnk + str(i),i))
        thr.append(t)
        t.start()
    for k in range(len(thr)):

        thr[k].join()
    
    print(len(data))
    df2 = pd.DataFrame.from_dict(data, orient='index')
    df2 = df2.transpose()
    car = '_'.join(car.split("/"))
    df2.to_csv(f"{car}.csv")

car = input('macchina:  ')

def run(car):

    lnk = f"https://www.autoscout24.it/lst/{car}?sort=standard&desc=0&ustate=N%2CU&size=20&page="
    thr = []
    for i in range(1, 10):
        get_csv_file(lnk + str(i),i)
    
    print(len(data))
    df2 = pd.DataFrame.from_dict(data, orient='index')
    df2 = df2.transpose()
    car = '_'.join(car.split("/"))
    df2.to_csv(f"{car}.csv")



if __name__ == '__main__':
    import time
    tmp = time.time()
    run_thr(car)
    print('      threading  ',time.time() - tmp, len(data['marchio']))
    tmp = 0

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
    tmp = time.time()
    run_proc(car)
    print('      processing  ',time.time() - tmp, len(data['marchio']))
    tmp = 0

    tmp = time.time()
    run(car)
    print('      normal  ',time.time() - tmp, len(data['marchio']))
    tmp = 0
