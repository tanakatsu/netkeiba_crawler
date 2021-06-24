import pickle
from time import sleep
from argparse import ArgumentParser
import netkeiba

parser = ArgumentParser()
parser.add_argument('--max_page', type=int, dest='max_page', default=-1)
parser.add_argument('-i', '--interval', type=int, dest='interval', default=1)
parser.add_argument('-o', '--output', type=str, dest='output', default=None)  # horsedb.pkl
args = parser.parse_args()

data = []
page = 1

crawler = netkeiba.HorseListPageCrawler(listSize=100)
print ('Getting page', page, '...')
try:
    html = crawler.getFirstPage()
except Exception as e:
    print (e.message)
    html = None
if html:
    # print html
    parser = netkeiba.HorseDataParser()
    data_in_page = parser.parse_horse_list(html)
    if data_in_page:
        data.extend(data_in_page)
        # print data_in_page
        for d in data_in_page:
            print (d['name'])
        # print len(data_in_page)
        print ('Number of data=', len(data))

if args.max_page < 0 or page < args.max_page:
    while crawler.haveNextPage():
        sleep(args.interval)
        page += 1
        print ('Getting page', page, '...')
        try:
            html = crawler.getNextPage()
        except Exception as e:
            print (e.message)
            html = None
        if html is not None:
            # print html
            data_in_page = parser.parse_horse_list(html)
            if data_in_page:
                data.extend(data_in_page)
                # print data_in_page
                for d in data_in_page:
                    print (d['name'])
                # print len(data_in_page)
                print ('Number of data=', len(data))
            if args.max_page >= 0 and page >= args.max_page:
                break

if args.output:
    with open(args.output, "w") as f:
        pickle.dump(data, f)

print ('done.')
