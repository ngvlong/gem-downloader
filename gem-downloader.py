import requests
from bs4 import BeautifulSoup
import sys
import urllib3
import re

urllib3.disable_warnings()

Proxies = {
    'http': 'http://192.168.5.8:3128',
    'https': 'http://192.168.5.8:3128'

}
URL_MAIN = 'https://rubygems.org'
URL_GEM = 'https://rubygems.org/gems/{0}'
URL_GEM_VERSION = 'https://rubygems.org/gems/{0}/versions/{1}'
VERIFY_CERT = False


def get_link_with_version(url, version):
    r = requests.get(url + '/versions/' + version, proxies=Proxies, verify=VERIFY_CERT)
    if r.status_code == 200:
        return url
    r = requests.get(url + '/versions', proxies=Proxies, verify=VERIFY_CERT)

    if r.status_code != 200:
        return None
    html = BeautifulSoup(r.content, "html.parser")
    ds = html.find_all('a', {'class': 't-list__item'})
    for d in ds:
        reg = re.search('^{0}(\.\d+)?$'.format(version), d.text)
        if reg:
            return URL_MAIN + d['href']
    
    return None



def get_link(url):
    r = requests.get(url, proxies=Proxies, verify=VERIFY_CERT)
    if r.status_code != 200:
        return None

    html = BeautifulSoup(r.content, "html.parser")
    download = html.find("a", {"id": "download"})
    if not download:
        return None

    download_link = URL_MAIN + download['href']
    if download_link:
        print(download_link)

    dependencies = html.find("div", {"id": "runtime_dependencies"})
    if dependencies:
        ds = dependencies.find_all("a", {"class": "t-list__item"})
        links = []
        for d in ds:
            if '~>' in d.text:
                reg = re.search('\d+\.\d+(\.\d)?', d.text)
                if reg:
                    ver = reg.group(0)
                    link = get_link_with_version(URL_MAIN + d['href'], ver)  
                else: 
                    link = URL_MAIN + d['href']
            else: 
                    link = URL_MAIN + d['href']
            if link:
                links.append(link)
            
        for l in links:
            get_link(l)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python gem-downloader.py url")
    get_link(sys.argv[1])
    
            
    