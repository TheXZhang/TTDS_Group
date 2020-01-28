from recipe_scrapers import scrape_me
from usp.tree import sitemap_tree_for_homepage
import json
import signal
import time



class TimeOutException(Exception):
   pass

def alarm_handler(signum, frame):
    print("ALARM signal received")
    raise TimeOutException()

docID=0
urllist=[]
recipes_dict={}

tree = sitemap_tree_for_homepage("https://www.bbc.co.uk/food/")
for page in tree.all_pages():
    url=page.url
    if "https://www.bbc.co.uk/food/recipes/" in url:
        urllist.append(page.url)

with open('url.txt','w') as fp:
    for url in urllist:
        fp.write(url+"\n")

signal.signal(signal.SIGALRM, alarm_handler)

with open('data.txt','w') as fp:
    for url in urllist:
        signal.alarm(8)
        try:
            print(url)
            scraper = scrape_me(url)
            title=scraper.title()
            time=scraper.total_time()
            ingredients=scraper.ingredients()
            if title and time and ingredients:
                docID +=1
                fp.write(str(docID) + "\n")
                fp.write(str(url) + "\n")
                fp.write(title + "\n")
                ingredients_str = '   '.join(ingredients)
                fp.write(ingredients_str + "\n")
                fp.write("\n")
                print("success")
            else:
                raise Exception
        except:
            pass

signal.alarm(0)
