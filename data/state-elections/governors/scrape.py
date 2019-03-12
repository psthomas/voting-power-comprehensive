import os
import time
import traceback

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

## If you want to scrape semi-anonymously, use these steps:
# https://stackoverflow.com/questions/1096379
# Using Tor:
# $ brew update
# $ brew install tor
# $ pip install -U requests requests[socks]
# Run tor:
# $ tor
# Then tell requests to use port 9050:

def get_page(url, tor=False):
    '''Returns a response object, filtered through tor network
    if tor=True'''
    proxies = {
        'http': 'socks5://localhost:9050',
        'https': 'socks5://localhost:9050'
    }
    if tor:
        response = requests.get(url, proxies=proxies)
    else:
        response = requests.get(url)
    return response 

fips_list = ['01','02','04','05','06','08','09','10',
    '11','12','13','15','16','17','18','19','20','21','22',
    '23','24','25','26','27','28','29','30','31','32','33',
    '34','35','36','37','38','39','40','41','42','44','45',
    '46','47','48','49','50','51','53','54','55','56']

def get_gov_pages():
    base_url = 'https://uselectionatlas.org/RESULTS/compare.php?year=2016&fips={0}&f=0&off=5&elect=0&type=state'
    for i in fips_list:
        url = base_url.format(i)
        try:
            pg = get_page(url, tor=True)
            out = os.path.join(os.getcwd(), 'pages', '{0}.html'.format(i))
            with open(out, 'w') as f:
                f.write(pg.text)
            print('Downloaded:', i)
        except Exception:
            print('Error:', i)
            traceback.print_exc()
        time.sleep(1)

def parse_gov_pages():
    for i in fips_list: 
        loc = os.path.join(os.getcwd(), 'pages', '{0}.html'.format(i))
        out = os.path.join(os.getcwd(), 'governors.csv')
        with open(loc, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            tbs = pd.read_html(str(soup))
            tb_df = pd.concat(tbs)
            tb_df = tb_df[['Year', 'Total', 'Dem.1', 'Rep.1', 'Ind.1', 'Other']]
            tb_df.rename(columns={'Year':'year', 'Total': 'total', 'Other': 'other',
                'Dem.1': 'dem', 'Rep.1': 'rep', 'Ind.1': 'ind'}, inplace=True)
            tb_df['fips'] = i

            if i == '01':
                tb_df.to_csv(out, mode='w', header=True, index=False)
            else:
                tb_df.to_csv(out, mode='a', header=False, index=False)


if __name__ == '__main__':
    # Uncomment as needed:
    #get_gov_pages()
    parse_gov_pages()


