from requests_cache import CachedSession
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dataclasses import dataclass, asdict, field
import pandas as pd 
import sqlite3
import os


@dataclass
class Web:
    name: str = None
    address: str = None
    website: str = None


@dataclass
class SaveData:
    data_list: list[Web] = field(default_factory=list)

    def dataframe(self):
        return pd.DataFrame((asdict(data) for data in self.data_list))

    def save_to_csv(self, filename: str):
        self.dataframe().to_csv(f'{filename}.csv', index=False)

    def save_to_json(self, filename: str):
        self.dataframe().to_json(f'{filename}.json', orient='records', force_ascii=False)
   
    def save_to_excel(self, filename: str):
        self.dataframe().to_excel(f'{filename}.xlsx', index=False)

    def save_to_sql(self, filename: str):
        conn = sqlite3.connect(f'{filename}.db')
        self.dataframe().to_sql(name='scrapedData', con=conn, index=False, if_exists='replace')
        conn.close()
        
    def makeDir(self):
        path = 'data'
        if os.path.exists(path):
            pass
        else:
            os.makedirs(path)
            return path

class Scraper:
    def __init__(self, url) -> None:
        self.url = url
        session = CachedSession(cache_name='cache/scraperSession')
        user_agent = UserAgent()
        self.response = session.get(self.url, headers={'User-Agent':user_agent.random})


    def start_requests(self):
        try:
            if self.response.status_code == 200:
                return self.response
            else:
                print(self.response.status_code)
                return 0
        except Exception as e:
            print(f'Error at get_response {e}')

    def bsScraper(self):
        soup = BeautifulSoup(self.response.content, 'html5lib')

        savedata = SaveData()

        items = soup.findAll('div', {"class":"card-body gz-directory-card-body"})
        for item in items:
            name = item.find('h5', {'itemprop':"name"}).a.text
            try:
                add = item.find('ul', class_ = 'list-group list-group-flush').li.a
                address = ''.join([x.text for x in add.find_all('span')])
            except:
                try:
                    add = item.find('ul', class_ = 'list-group list-group-flush').li.a.span
                    address = add.text
                except:
                    pass
            #website = None
            try:
                websi = item.find("li", class_ = "list-group-item gz-card-website").a    
            except:
                pass
            website = websi.get('href')
            result = Web(
                name=name,
                address=address,
                website=website
            )
            savedata.data_list.append(result)
            print(result)

        path = savedata.makeDir()
        savedata.save_to_csv(f'{path}/AESAData')
        savedata.save_to_excel(f'{path}/AESAData')
        savedata.save_to_json(f'{path}/AESAData')
        savedata.save_to_sql(f'{path}/AESAData')


if __name__ == '__main__':
    web = Scraper('https://members.aesa.us/directory/FindStartsWith?term=%23%21')
    web.start_requests()
    web.bsScraper()