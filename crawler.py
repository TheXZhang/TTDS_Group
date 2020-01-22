from recipe_scrapers import scrape_me
from usp.tree import sitemap_tree_for_homepage
import json


urllist=[]
recipes_dict={}

tree = sitemap_tree_for_homepage('https://www.bbcgoodfood.com/')
for page in tree.all_pages():
    url=page.url
    if "https://www.bbcgoodfood.com/recipes/" in url:
        urllist.append(page.url)



for url in [urllist[0]]:
    print(url)
    scraper = scrape_me(url)
    title=scraper.title()
    time=scraper.total_time()
    ingredients=scraper.ingredients()
    yields=scraper.yields()
    recipes_dict[title]={}
    recipes_dict[title]["time"]=time
    recipes_dict[title]["ingredients"]=ingredients
    recipes_dict[title]["yields"]=yields

print(recipes_dict)

with open('data.json','w') as fp:
    json.dump(recipes_dict,fp)
