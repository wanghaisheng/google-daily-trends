from cf_bypass import CloudflareBypass
from DrissionPage import (
    ChromiumOptions,
    ChromiumPage,
    SessionPage,
    WebPage,
    SessionOptions,
)
from DataRecorder import Recorder

import time
import json

from thread_worker import LimitWorker, Worker


file=open('country-code.json',encoding='utf8')

geo='US'
url='https://trends.google.com.hk/trends/trendingsearches/realtime?geo=US&hl=zh-HK&category=all'
geos=json.load(file).get('data').keys()
categories=[

    'all',
    # qiye
    'b',
# yule
    'e',
    #keji
    't',
    # jiankang
    'm',
    #jiandianxingwen
    'h',
    #tiyu
    's'

]
def getdata(data):
    outfile=data['outfile']
    url=data['url']
    browser=data['browser']
    c=data['c']
    geo=data['geo']

    tab = browser.new_tab()

    tab.get(url)
    print(tab.title)
    if tab.ele('.:no-search-error'):
        print('found error')
        data=geo+','+c
        errorile.add_data(data)
        tab.close()
        return 
    else:
        more=True
        count=0
        start=0
       
        while more:


        # <div class="feed-load-more-button" ng-if="ctrl.shouldShowLoadingMoreItemsSpinner()" ng-click="ctrl.loadMoreFeedItems()" role="button" tabindex="0" style="">
                # 載入更多
            #   </div>
            try:
                # print(tab.ele('.feed-load-more-button'))
                # print(tab.ele('@class=feed-load-more-button'))
                # print(tab.ele('text:載入更多'))
                # print(tab.ele('載入更多'))
                # print(tab.ele('css:div[role="button"]'))
                ele=tab.ele('css:div[role="button"]')    
                ele=tab.ele('.feed-load-more-button')    
                # 判断是否找到元素
            
                print(f"找到了{count}查看更多")

                now=time.strftime("%Y-%m-%d_%H-%M", time.localtime())                    
                riqi=now
                # print(riqi)
                # print(dd.html)
                end=len(tab.eles('.:md-list-block'))
                print(f"找到了{end}组数据")

                print(f"保存了{start}组数据")
                print(f"剩余了{end-start}组数据")

                for e in tab.eles('.:md-list-block')[start:]:
                    # print(e.text)
                    data=e.text+'\n'+riqi+'\n'+geo+'\n'+c


                    data={

                    'date':riqi,
                    'geo':geo,
                    "c":c
                    }
                    rawdata=[]
                    for ele in e.children():
                        rawdata.append(ele.raw_text)
                    data['raw']=rawdata
                    print(f'add data {count}')
                    outfile.add_data([data])

                
                with open (f'logs/googletrends-{now}.html','w',encoding='utf8') as f:
                    f.write(tab.html)
                start=end

                ele.click()
                # ele.click(by_js=None)
                time.sleep(3)
                count = count + 1
                tab.run_js("document.documentElement.scrollTop=1000")

                # time.sleep(5)s
            except:
                print("没有找到。")
                more=False
                # break
            # print(page.html)

        time.sleep(3)

        tab.close()
co = ChromiumOptions().auto_port()
so = SessionOptions()
co.set_proxy('socks5://localhost:1080')

co.set_browser_path(r"C:\Users\Administrator\AppData\Local\Google\Chrome\Bin\chrome.exe")

# browser = SessionPage(so)
browser = WebPage(chromium_options=co, session_or_options=so)
outfile=Recorder(f'glivetrends.csv',cache_size=20)
errorile=Recorder(f'eror.csv',cache_size=1)
w = Worker(getdata, consumer_count=3, block=True)

for c in categories:
    for geo in geos:
        url=f'https://trends.google.com.hk/trends/trendingsearches/realtime?geo={geo}&hl=zh-HK&category={c}'

        data={}
        data["browser"]=browser
        data["url"]=url
        data["outfile"]=outfile
        data["c"]=c
        data["geo"]=geo

        w.put(data)

    while not w.is_end():
        time.sleep(3)
outfile.record()
