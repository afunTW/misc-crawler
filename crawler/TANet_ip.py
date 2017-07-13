import re
import csv
import requests
from bs4 import BeautifulSoup
from pprint import pprint


def main():
    resp = requests.get(website)
    soup = BeautifulSoup(resp.text, 'lxml')
    target = soup.find(id='IP.E4.BD.8D.E5.9D.80.E7.AF.84.E5.9C.8D')
    all_data = {}

    with open('TANet_ip.csv', 'w', newline='\n') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'IP'])
        for i, ul in enumerate(target.parent.find_next_siblings('ul')):

            if i >= len(target.parent.find_next_siblings('ul'))-1:
                break

            for li in ul.find_all('li'):
                data = list(filter(None, li.text.split('—')))

                if len(data) < 2:
                    continue

                name = data[0]
                all_ip = []

                # handle ip string
                ips = [x.strip() for x in data[1].split(',')]
                for ip in ips:
                    # 靜宜大學 120.110（主要140.128.1～40）
                    ip = ip.replace('～', '~')
                    ip = re.sub('（.*）|\[.*\]', '', ip)

                    if '~' in ip:
                        ip = [re.findall('\d+', _) for _ in ip.split('~')]
                        ip_from, ip_to = ip
                        for _ in range(int(ip_from[-1]), int(ip_to[0])+1):
                            all_ip.append('{}.{}.{}'.format(ip_from[0], ip_from[1], _))
                    elif '、' in ip:
                        ip_1, ip_2 = ip.split('、')
                        all_ip.append(ip_1)
                        all_ip.append('.'.join(ip_1.split('.')[:-1]) + '.{}'.format(ip_2))
                    else:
                        all_ip.append(ip)

                # padding '*'
                for ip in all_ip:
                    _ = ip.split('.')
                    _.extend('*' * (4-len(_)))
                    writer.writerow([name, '.'.join(_)])

if __name__ == '__main__':
    website = 'https://zh.wikipedia.org/wiki/TANet'
    main()
