import requests
from bs4 import BeautifulSoup
import sqlite3
import env
import datetime

import base64


list_create = []
list_exist = []
list_update = []
last_create=-1
last_exist=-1
last_update=-1

update_page_max=100
update_page_now=0

class title():
    def __init__(self, id, name, url, img, latest, favorite, updated):
        self.id = id
        self.name = name
        self.url = url
        self.img = img
        self.latest = latest
        self.favorite = favorite
        self.updated = updated

    def set_favorite(self, favorite):
        self.favorite = favorite
        set_favorite_by_name(self.name, self.favorite)

class database():
    def __init__(self):
        self.conn = sqlite3.connect(env.DATABASE_NAME)
        self.cur  = self.conn.cursor()

    def execute(self, sql):
        return self.cur.execute(sql)

    def __del__(self):
        self.conn.commit()
        self.conn.close()

def get_all():
    titles = []
    db = database()
    res = db.execute(f'SELECT * FROM pages')
    data = res.fetchall()
    for d in data:
        titles.append(title(d[0], d[1], d[2], d[3], d[4], d[5], d[6]))
    return titles

def get_page(page=1):
    global last_create
    global last_exist
    global last_update
    date = datetime.datetime.now()

    # HTMLの取得(GET)
    req = requests.get(env.PAGE_URL+str(page)+"/")
    req.encoding = req.apparent_encoding # 日本語の文字化け防止

    # HTMLの解析
    bsObj = BeautifulSoup(req.text,"html.parser")

    # Open DB
    db = database()

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
            res = db.execute(f'SELECT id FROM pages WHERE name="{name}"')
            if res.fetchone() is None:
                db.execute(f'INSERT INTO pages(name, url, img, latest, favorite, updated) values("{name}", "{url}", "{img}", "{latest}", {favorite}, "{date}")')
                update_base64(img, db)
                print(f'CREATE {name}')
                list_create.append(name)
                last_create=page
            else :
                res = db.execute(f'SELECT * FROM pages WHERE name="{name}"')
                id, db_name, db_url, db_img, db_latest, db_favorite, db_updated = res.fetchone()
                if db_latest != latest:
                    db.execute(f'UPDATE pages SET latest="{latest}", updated="{date}" WHERE name="{name}"')
                    if (not has_base64(id, db)):
                        update_base64(img, db)
                    print(f'UPDATE {name} db:{db_latest} web:{latest} updated:{date}')
                    list_update.append(name)
                    last_update=page
                else:
                    print(f'EXIST {name}')
                    list_exist.append(name)
                    last_exist=page


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

def get_title(id):
    if id < 1:
        return None

    db = database()
    
    res = db.execute(f'SELECT name FROM pages WHERE id="{id}"')
    if res.fetchone() is not None:
        res = db.execute(f'SELECT * FROM pages WHERE id="{id}"')
        return  res.fetchone()

def set_favorite_by_id(id, favorite):
    db = database()
    db.execute(f'UPDATE pages SET favorite="{favorite}" WHERE id="{id}"')

def set_favorite_by_name(name, favorite):
    db = database()
    db.execute(f'UPDATE pages SET favorite="{favorite}" WHERE name="{name}"')



def save_thumbnail(id):
    if id < 1:
        return None

    conn = sqlite3.connect(env.DATABASE_NAME)
    cur  = conn.cursor()
    
    res = cur.execute(f'SELECT name FROM pages WHERE id="{id}"')
    if res.fetchone() is not None:
        res = cur.execute(f'SELECT img FROM pages WHERE id="{id}"')
    name = res.fetchone()
    req = requests.get(env.BASE_URL+name)
    f = open(name, "wb")
    f.write(req.content)
    f.close()

def has_base64(id, db):
    res = db.execute(f'SELECT EXISTS(SELECT id FROM base64 WHERE id="{id}")')
    return res.fetchone()[0] == 0

def update_base64(url, db):
    res = db.execute(f'SELECT id FROM pages WHERE img="{url}"')
    id = res.fetchone()
    image_base64 = None
    if id is not None:
        image_src = env.BASE_URL+url
        req = requests.get(image_src)
        image_base64 = base64.b64encode(req.content).decode()
        res = db.execute(f'SELECT EXISTS(SELECT id FROM base64 WHERE id="{id}")')
        if res.fetchone()[0] == 0:
            print('Base64 inserted:', id)
            db.execute(f'INSERT INTO base64(id, img_base64) values("{id}", "{image_base64}")')
        else:
            print('Base64 updated:', id)
            db.execute(f'UPDATE base64 SET img_base64="{image_base64}" WHERE id="{id}"')
    else:
        print(f'[update_base64]:{url} is not found in TABLE(pages)')
    return image_base64

def get_base64(url):
    db = database()
    res = db.execute(f'SELECT id FROM pages WHERE img="{url}"')
    id = res.fetchone()
    image_base64 = None
    if id is not None:
        res = db.execute(f'SELECT EXISTS(SELECT id FROM base64 WHERE id="{id}")')
        if res.fetchone()[0] == 1:
            res = db.execute(f'SELECT img_base64 FROM base64 WHERE id="{id}"')
            image_base64 = res.fetchone()[0]
        else:
            image_base64 = update_base64(url, db)
    else:
        print(f'[get_base64]:{url} is not found in TABLE(pages)')
    return image_base64

def update_all_pages():
    global update_page_max, update_page_now
    last_page = get_last_page()
    update_page_max = last_page
    thresh_pages = 10
    for i in range(last_page):
        update_page_now = i
        print("PAGE:", i)
        get_page(i)
        if (last_create+thresh_pages<i) and (last_update+thresh_pages<i):
            break

    print("new titles:", list_create)
    print("list_update:",len(list_update))
    print("list_exist:", len(list_exist))
    print("last_create page:", last_create)
    print("last_update page:", last_update)
    print("last exist page:", last_exist)

def init():
    conn = sqlite3.connect(env.DATABASE_NAME)
    cur  = conn.cursor()
    cur.execute(
        "CREATE TABLE pages(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, url STRING, img STRING, latest STRING, favorite INTEGER, updated DATE)"
    )
    cur.execute(
        "CREATE TABLE base64(id INTEGER, img_base64 STRING)"
    )
    conn.commit()
    conn.close()

def main():
    update_all_pages()

if __name__ == "__main__":
    main()


