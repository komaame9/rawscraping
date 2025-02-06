import requests
from bs4 import BeautifulSoup
import sqlite3
import env
import datetime


list_create = []
list_exist = []
list_update = []

def get_page(page=1):
    date = datetime.datetime.now()

    # HTMLの取得(GET)
    req = requests.get(env.PAGE_URL+str(page)+"/")
    req.encoding = req.apparent_encoding # 日本語の文字化け防止

    # HTMLの解析
    bsObj = BeautifulSoup(req.text,"html.parser")

    # Open DB
    conn = sqlite3.connect(env.DATABASE_NAME)
    cur  = conn.cursor()

    for i in bsObj.find_all('div', class_="post-list"):
        for j in i.find_all("a") :
            name = j.find('h3').text
            name = name.replace('"',' ')
            name = name.replace("'",' ')
            url = j.get('href')
            img = j.find('img').get('data-src')
            latest = j.find('div', class_='post-list-time').text
            latest = latest.replace("\n", "")
            if "【" in latest  and "】" in latest :
                latest = latest[latest.find("【" ) : latest.find("】")+1]
            favorite = 0
            print('GET:', name, url, img, latest, favorite, date)
            res = cur.execute(f'SELECT name FROM pages WHERE name="{name}"')
            if res.fetchone() is None:
                cur.execute(f'INSERT INTO pages(name, url, img, latest, favorite, updated) values("{name}", "{url}", "{img}", "{latest}", {favorite}, "{date}")')
                print(f'CREATE {name}')
                list_create.append(name)
            else :
                res = cur.execute(f'SELECT * FROM pages WHERE name="{name}"')
                id, db_name, db_url, db_img, db_latest, db_favorite, db_updated = res.fetchone()
                if db_latest != latest:
                    cur.execute(f'UPDATE pages SET latest="{latest}" WHERE name="{name}"')
                    print(f'UPDATE {name} db:{db_latest} web:{latest} updated:{date}')
                    list_update.append(name)
                else:
                    print(f'EXIST {name}')
                    list_exist.append(name)
    conn.commit()
    conn.close()


def get_last_page():
    page = 2
    req = requests.get(env.PAGE_URL+str(page)+"/")
    req.encoding = req.apparent_encoding # 日本語の文字化け防止

    # HTMLの解析
    bsObj = BeautifulSoup(req.text,"html.parser")

    return int(bsObj.find('a', class_="last").get('href').split('/')[-1])

    

def test_scraping(page=1):
    date = datetime.datetime.now()

    # HTMLの取得(GET)
    req = requests.get(env.PAGE_URL+str(page)+"/")
    req.encoding = req.apparent_encoding # 日本語の文字化け防止

    # HTMLの解析
    bsObj = BeautifulSoup(req.text,"html.parser")

    for i in bsObj.find_all('div', class_="post-list"):
        for j in i.find_all("a") :
            name = j.find('h3').text
            name = name.replace('"',' ')
            name = name.replace("'",' ')
            url = j.get('href')
            img = j.find('img').get('data-src')
            latest = j.find('div', class_='post-list-time').text
            latest = latest.replace("\n", "")
            if "【" in latest  and "】" in latest :
                latest = latest[latest.find("【" ) : latest.find("】")+1]
            favorite = 0
            print(name, url, img, latest , favorite)

    

def save_thumbnail():
    name = "e69d4121528548bc83f585f6daa46c97.jpg"
    req = requests.get("https://mangarawjp.tv/data/images/"+name)
    f = open(name, "wb")
    f.write(req.content)
    f.close()

def update_all_pages():
    last_page = get_last_page()
    for i in range(last_page):
        print("PAGE:", i)
        get_page(i)

    print(list_create)
    print("list_update:",len(list_update))
    print("list_exist:", len(list_exist))

def main():
    update_all_pages()

if __name__ == "__main__":
    main()


