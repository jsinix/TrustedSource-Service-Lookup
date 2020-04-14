import requests, sys, argparse
import os, time
from tqdm import tqdm
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool

def writedata(entry, filename):
    with open(filename, "a") as myfile:
        myfile.write(entry+'\n')

def lookup(url):
    pbar.update(1)
    payload = {'e':(None, token1),
               'c':(None, token2),
               'action':(None,'checksingle'),
               'product':(None,'01-ts'),
               'url':(None, url)}

    try:
        r = requests.post('https://www.trustedsource.org/en/feedback/url', headers=headers, files=payload)
        bs = BeautifulSoup(r.content, "html.parser")
        form = bs.find("form", { "class" : "contactForm" })
        table = bs.find("table", { "class" : "result-table" })
        td = table.find_all('td')
        categorized = (td[len(td)-3].text).lstrip().rstrip()
        category = (td[len(td)-2].text[2:]).lstrip().rstrip()
        risk = (td[len(td)-1].text).lstrip().rstrip()
        data = ('{},{},{},{}'.format(url,categorized, category, risk))
        writedata(data, 'trustedsource-results.csv')
        return categorized, category, risk
    except Exception as err:
        error = '{},{}' .format(url,err)
        writedata(error, 'trustedsource-error.csv')

def process_arguments(args):
    parser = argparse.ArgumentParser(description="CLI Tool To Query Website Reputation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f',
                        '--file',
                        help="File with hostnames, each separated by a new line"
                        )
    group.add_argument('-H',
                        '--host',
                        help="Single host to query"
                        )
    options = parser.parse_args(args)
    return vars(options)

if len(sys.argv) < 2:
    process_arguments(['-h'])
userOptions = process_arguments(sys.argv[1:])

# Calculate runtime
start_time = time.time()

# Reference: https://github.com/mohlcyber/TrustedSource-Service-Lookup
headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5)',
'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Language' : 'en-US,en;q=0.9,de;q=0.8'}
base_url = 'http://www.trustedsource.org/sources/index.pl'
r = requests.get(base_url, headers=headers)
bs = BeautifulSoup(r.content, "html.parser")
form = bs.find("form", { "class" : "contactForm" })
token1 = form.find("input", {'name': 'e'}).get('value')
token2 = form.find("input", {'name': 'c'}).get('value')
headers['Referer'] = base_url

try:
    os.system('clear')
except Exception as err:
    os.system('cls')
print ("\n\n\n\t\tMcAfee TrustedSource Category Check\n\n")

if userOptions['host'] != None:
    pbar = tqdm(total=1)
    url = userOptions['host'].lstrip().rstrip() 
    categorized, category, risk = lookup(url)
    print ('{},{},{},{}'.format(url,categorized, category, risk))

else:
    file = userOptions['file']
    hosts =  [x.replace('\n', '').replace('[.]', '.').lstrip().rstrip() for x in open(file)]
    pbar = tqdm(total=len(hosts))
    pool = ThreadPool(25)
    results = pool.map(lookup, hosts) 
    pool.close()
    pool.join() 

end_time = time.time()
print ("\n\n\nExecution Time: {}".format(end_time-start_time))
