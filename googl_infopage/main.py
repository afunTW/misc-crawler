import argparse
import inspect
import os
import random
import time
from urllib.parse import urljoin

from selenium import webdriver

import pandas as pd

__FILE__ = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
SAVE_PATH = os.path.abspath(os.path.join(__FILE__, '../data'))

def argparser():
    parser = argparse.ArgumentParser(description='interactive graph cut for moth image')
    parser.add_argument('--csv', help='given a csv file to process',
        nargs=1, default=None)
    parser.add_argument('--url', help='given bunch of url to process',
        nargs='+', default=None)
    parser.add_argument('--outdir', help='given the ouput directory', nargs=1, default=None)
    return parser

def get_urls(args):
    urls = []

    if args.csv:
        filepath = os.path.abspath(args.csv[0])
        df = pd.read_csv(filepath, header=None)
        df.columns = ['url']
        urls += list(df.url)

    if args.url:
        urls += [u.strip(' ') for u in args.url]

    return urls

def main(args):
    global SAVE_PATH
    save_path = args.outdir[0] or SAVE_PATH

    try:
        urls = get_urls(args)
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        for i, url in enumerate(urls):
            # check
            hash_id = url.split('/')[-1]
            url = urljoin(url, '/info') + '/{}'.format(hash_id)
            save_file = os.path.join(save_path, '{}.html'.format(hash_id))
            if os.path.exists(save_file):
                continue

            # process
            driver.get(url)

            # save
            with open(save_file, 'w+') as f:
                print('{} - #{} Save {}'.format(time.ctime(), i, save_file))
                f.write(driver.page_source)
                time.sleep(random.randint(1,3))

    except Exception as e:
        print(e)

if __name__ == '__main__':
    parser = argparser()
    main(parser.parse_args())
