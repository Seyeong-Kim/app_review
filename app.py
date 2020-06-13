import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta

driver = webdriver.Chrome("./chromedriver")
res = driver.get("https://play.google.com/store/apps/details?id=com.ncsoft.lineage2m19&showAllReviews=true")
time.sleep(10)
b1 = driver.find_element_by_css_selector('#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div.JNury.Ekdcne > div > div > div.W4P4ne > div:nth-child(2) > c-wiz > div:nth-child(1) > div > div:nth-child(1) > div.ry3kXd.Ulgu9 > div.MocG8c.UFSXYb.LMgvRb.KKjvXb > span')
b1.click()
time.sleep(2)
b2 = driver.find_element_by_css_selector('#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div.JNury.Ekdcne > div > div > div.W4P4ne > div:nth-child(2) > c-wiz > div:nth-child(1) > div > div.OA0qNb.ncFHed > div:nth-child(1)')
b2.click()
time.sleep(5)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)

reviewers = driver.find_elements_by_css_selector("#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div.JNury.Ekdcne > div > div > div.W4P4ne > div:nth-child(2) > div > div > div > div.d15Mdf.bAhLNe > div.xKpxId.zc7KVe > div.bAhLNe.kx8XBd > span")
reviews = driver.find_elements_by_css_selector("#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div.JNury.Ekdcne > div > div > div.W4P4ne > div:nth-child(2) > div > div > div > div.d15Mdf.bAhLNe > div.UD7Dzf > span:nth-child(1)")
grades = driver.find_elements_by_css_selector("#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div.JNury.Ekdcne > div > div > div.W4P4ne > div:nth-child(2) > div > div > div > div.d15Mdf.bAhLNe > div.xKpxId.zc7KVe > div.bAhLNe.kx8XBd > div > span.nt2C1d > div > div")
clicks = driver.find_elements_by_css_selector("#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div.JNury.Ekdcne > div > div > div.W4P4ne > div:nth-child(2) > div > div > div > div.d15Mdf.bAhLNe > div.xKpxId.zc7KVe > div.YCMBp.GVFJbb > div > div.XlMhZe > div.jUL89d.y92BAb")
dates = driver.find_elements_by_css_selector("#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div.JNury.Ekdcne > div > div > div.W4P4ne > div:nth-child(2) > div > div > div > div.d15Mdf.bAhLNe > div.xKpxId.zc7KVe > div.bAhLNe.kx8XBd > div > span.p2TkOb")


for reviewer,date,grade,click,review in zip(reviewers,dates,grades,clicks,reviews):
    if len(list(db.appreviews.find({"reviewer":reviewer.text, "review": review.text}))) > 0:
        if click.text == '':
            db.appreviews.delete_one({"reviewer":reviewer.text, "review": review.text})
            db.appreviews.insert_one({"reviewer":reviewer.text, "date" : date.text,"grade" : grade.get_attribute('aria-label').split(' ')[3][:1], "click" : 0, "review" : review.text})
        else:
            db.appreviews.delete_one({"reviewer":reviewer.text, "review": review.text})
            db.appreviews.insert_one({"reviewer":reviewer.text, "date" : date.text,"grade" : grade.get_attribute('aria-label').split(' ')[3][:1], "click" : int(click.text), "review" : review.text})
    else:
        if click.text == '':
            db.appreviews.insert_one({"reviewer":reviewer.text, "date" : date.text,"grade" : grade.get_attribute('aria-label').split(' ')[3][:1], "click" : 0, "review" : review.text})
        else:
            db.appreviews.insert_one({"reviewer":reviewer.text, "date" : date.text,"grade" : grade.get_attribute('aria-label').split(' ')[3][:1], "click" : int(click.text), "review" : review.text})
driver.close()

# HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')

# API 역할을 하는 부분
@app.route('/appreviews/list', methods=['GET'])
def appreviews():
    appreviews = list(db.appreviews.find({},{'_id':False}))
    bunja = 0
    bunmo = 0
    for review in appreviews:
        bunja = bunja + int(review['grade']) * (review['click'] + 1)
        bunmo = bunmo + review['click'] + 1              
    return jsonify({'result': 'success','msg': appreviews, 'avg': bunja/bunmo})

@app.route('/appreviews/point', methods=['POST'])
def point_review():
    if request.form['grade'] == '0':
        appreviews = list(db.appreviews.find({},{'_id':False}))
    else:
        appreviews = list(db.appreviews.find({'grade': request.form['grade']},{'_id': False}))
    return jsonify({'result': 'success','msg': appreviews})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)