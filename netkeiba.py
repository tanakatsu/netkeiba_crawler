# encoding: utf-8
import chardet
from bs4 import BeautifulSoup
import traceback
from time import sleep
import requests

class HorseListPageCrawler:

    URL = "http://db.netkeiba.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

    def __init__(self, listSize=100):
        self.list_size = listSize

    def getFirstPage(self):
        self.current_page = 1
        payload = {
            'pid':'horse_list', 
            'under_age': 2,
            'sort':'prize', 
            'list': self.list_size
        } 

        response = requests.get(
             self.URL,
             headers=self.headers,
             params=payload
        )
        response.encoding = response.apparent_encoding
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        self.sort_key = soup.find("input", {"type": "hidden", "name": "sort_key"})["value"]
        self.sort_type = soup.find("input", {"type": "hidden", "name": "sort_type"})["value"]
        self.serial = soup.find("input", {"type": "hidden", "name": "serial"})["value"]
        self.current_page = 1
        self.current_html = html
        return html

    def getPage(self, page=1):
        if page == 1:
            return self.getFirstPage()
        self.current_page = page
        payload = {"sort_key": self.sort_key, "sort_type": self.sort_type, "page": self.current_page, "pid": "horse_list"}  # Modify this depending on your needs
        response = requests.get(
             self.URL,
             headers=self.headers,
             params=payload
        )
        response.encoding = response.apparent_encoding
        self.current_html = response.text
        return response.text

    def getNextPage(self):
        return self.getPage(self.current_page + 1)

    def haveNextPage(self):
        soup = BeautifulSoup(self.current_html, "html.parser")
        try:
            pager = soup.select("div.pager")[0]
        except Exception as e:
            print (e.message)
            return False
        pager_elms = pager.find_all("a")
        if len(pager_elms) == 0:
            return False
        if len(pager_elms) == 1 and pager_elms[0].string == u'前':
            return False
        return True


class HorsePageFetcher:

    URL = "http://db.netkeiba.com/"

    def getPage(self, hid):
        url = "{base_url}/horse/{hid}/".format(base_url=self.URL, hid=hid)
        response = requests.get(
             self.URL,
             headers=self.headers
        )
        response.encoding = response.apparent_encoding
        return response.text

    def getMareChildrenResultsPage(self, hid):
        url = "{base_url}/?pid=horse_select&id={hid}&year=0000&mode=wn&type=mare".format(base_url=self.URL, hid=hid)
        response = requests.get(
             self.URL,
             headers=self.headers
        )
        response.encoding = response.apparent_encoding
        return response.text


class HorseDataParser:

    def parse_horse_list(self, html):
        result = []
        soup = BeautifulSoup(html, "html.parser")
        if len(soup.select("table.race_table_01")) > 0:
            race_table = soup.select("table.race_table_01")[0]
        else:
            print( html)
            return result
        uma_elms = race_table.find_all("tr")[1:]
        for elm in uma_elms:
            data = elm.find_all("td")
            name = data[1].string
            hid = data[1].a.get("href").replace("/horse/", "")[:-1]
            sex = data[2].string
            birth_year = int(data[3].a.string)
            if data[5].a:
                stable = data[5].a.string
            else:
                stable = data[5].string
            if data[6].a:
                sire = data[6].a.string
            else:
                sire = data[6].string
            if data[7].a:
                mare = data[7].a.string
            else:
                mare = data[7].string
            if data[8].a:
                bms = data[8].a.string
            else:
                bms = data[8].string
            if data[9].a:
                owner = data[9].a.string
            else:
                owner = data[9].string
            if data[10].a:
                breeder = data[10].a.string
            else:
                breeder = data[10].string
            prize = float(data[11].string.replace(",", ""))
            result.append({"hid": hid, "name": name, "sex": sex, "birth_year": birth_year, "stable": stable, "sire": sire, "mare": mare, "bms": bms, "owner": owner, "breeder": breeder, "prize": prize})
        return result

    def parse_horse_prof(self, html):
        soup = BeautifulSoup(html, "html.parser")
        prof_tables = soup.select("table.db_prof_table")
        if len(prof_tables) > 0:
            prof_table = prof_tables[0]
            prof_elms = prof_table.find_all("td")
            birth = prof_elms[0].string.replace(u'年', '/').replace(u'月', '/').replace(u'日', '')
        else:
            birth = None
        result_tables = soup.select("table.db_h_race_results")
        if len(result_tables) > 0:
            result_table = soup.select("table.db_h_race_results")[0]
            debut_race_elm = result_table.find_all("tr")[-1]
            debut_race_elms = debut_race_elm.find_all("td")

            debut_weight = int(debut_race_elms[23].string[0:3])
        else:
            debut_weight = None
        blood_table = soup.select("table.blood_table")[0]
        blood_elms = blood_table.find_all("td")
        mare_hid = blood_elms[3].a.get("href").replace('/horse/ped/', '')[:-1]

        return {"birth": birth, "debut_weight": debut_weight, "mare_hid": mare_hid}

    def parse_mare_children_results(self, html):
        result = {}
        soup = BeautifulSoup(html, "html.parser")
        race_tables = soup.select("table.race_table_01")
        if len(race_tables) > 0:
            race_table = race_tables[0]
            race_elms = race_table.find_all("tr")[1:]
            for race_elm in race_elms:
                data = race_elm.find_all("td")
                h_name = data[12].a.string
                if h_name in result:
                    result[h_name] += 1
                else:
                    result[h_name] = 1
        return result


if __name__ == '__main__':
    page = 1
    max_page = 2
    crawler = HorseListPageCrawler(listSize=100)
    print ('Getting page', page, '...')
    html = crawler.getFirstPage()
    print (html)
    parser = HorseDataParser()
    data_in_page = parser.parse_horse_list(html)
    print (data_in_page)
    print (len(data_in_page))
    
    while crawler.haveNextPage():
        sleep(1)
        page += 1
        print ('Getting page', page, '...')
        html = crawler.getNextPage()
        if html is not None:
            print (html)
            data_in_page = parser.parse_horse_list(html)
            print (data_in_page)
            print (len(data_in_page))
        if max_page >= 0 and page >= max_page:
            break

    print ('done.')
