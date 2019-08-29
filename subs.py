import requests
import sys
from bs4 import BeautifulSoup as bs
import re
import os
from zipfile import ZipFile
import io 
url = "http://www.tvsubtitles.net/search.php"
website_url = "http://www.tvsubtitles.net/"
season_name = input('Season Name >>> ').strip()
season_number = int(input('Season Number >>> ').strip())
post_data = { "q":season_name }

tv_show_link = ""
isFound = -1
with requests.post(url,data=post_data) as subs:
    subs = subs.text
    soup = bs(subs,"html.parser")
    div = soup.find_all(attrs={'class':'left_articles'})
    for el in div:
        a = el.select('ul > li > div > a')
        for anchor in a:
            temp = anchor.text.split('(')[0].strip()
            if(temp.lower() == season_name.lower()):
                isFound = 1
                tv_show_link = anchor['href']
                break
        if(isFound == -1):
            print("Can\'t Find Tv-Show With Name {},sorry try again with other name".format(season_name))
            sys.exit(0)
        
subtitles_page = requests.get(website_url+tv_show_link)
seasons_list = []

tv_show_id = re.findall(r'[\w]+',tv_show_link)[1]

html = subtitles_page.text
soup = bs(html,'html.parser')
seasons = soup.select('.description > a')

s_length = 0
if len(seasons) == 0:
    s_length = len(seasons) + 1
else:
    s_length = len(seasons) + 2

for season in range(1,s_length):
    seasons_list.append('tvshow-{}-{}.html'.format(tv_show_id,season))




# Subtitles Page


try:
    subtitles_page = requests.get(website_url+seasons_list[season_number - 1])
except:
    print('Cannot Find Season Number')
    sys.exit()

soup = bs(subtitles_page.text,'html.parser')
table = soup.find(attrs={'id':'table5'})

rows = table.find_all('tr')[1:-2]

episode_list = []

for row in rows:
   sub_link = row.find('a')
   sub_link = sub_link['href']
   episode_list.append(sub_link)

episode_list = episode_list[::-1]

# Episode Page
episode_number = 1
for ep in episode_list:
    episode_page = requests.get(website_url+ep)
    print('Downloading Episode {} - srt ...'.format(episode_number))
    soup = bs(episode_page.text,'html.parser')
    subtitles_group = soup.find(attrs={'class':'left_articles'})
    subtitles_list = subtitles_group.find_all('a')[1:-1]
    eng_sub_list = []
    for sub in subtitles_list:
        title = sub.find('h5').find('img')['src']
        if 'en.gif' in title.lower():
            eng_sub_list.append(sub['href'])

    english_subtitle_url = eng_sub_list[0]

    download_link = english_subtitle_url.replace('subtitle','download')
    srt = requests.get(website_url+download_link)

    path = os.getcwd()+'/subtitles/'
    if not os.path.isdir(path+season_name):
        os.mkdir(path+season_name)
    path_season = path+season_name+'/'
    file_name = "{}-{}X{}.zip".format(season_name,season_number,episode_number)
    z = ZipFile(io.BytesIO(srt.content))
    z.extractall(path_season+'season-'+str(season_number))
    episode_number += 1
sys.exit()
