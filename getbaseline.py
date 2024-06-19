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



geo='US'
url='https://trends.google.com.hk/trends/trendingsearches/realtime?geo=US&hl=zh-HK&category=all'
geos=['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AR', 'AS', 'AT', 'AU', 'AW', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW', 'BY', 'BZ', 'CA', 'CC', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU', 'CV', 'CX', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK', 'FM', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PS', 'PT', 'PW', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SD', 'SE', 'SG', 'SH', 'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SY', 'SZ', 'TC', 'TD', 'TG', 'TH', 'TJ', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI', 'VN', 'VU', 'WF', 'WS', 'XK', 'YE', 'YT', 'ZA', 'ZM', 'ZW']
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
                ele=tab.ele('.feed-load-more-button')    
                # ele=tab.ele('css:div[role="button"]')
                # ele=tab.ele('.feed-load-more-button')    
                # 判断是否找到元素  
                # ele=tab.ele('@ng-click:loadMoreFeedItems')
            
                print(f"找到了{count}查看更多")

                now=time.strftime("%Y-%m-%d_%H-%M", time.localtime())                    
                riqi=now
                # print(riqi)
                # print(dd.html)
                end=len(tab.eles('.feed-list-wrapper'))
                print(f"找到了{end}组数据")
                datedata=tab.eles('.feed-list-wrapper')
                print(f"保存了{start}组数据")
                print(f"剩余了{end-start}组数据")

                for dd in datedata[start:]:
                    riqi=dd.ele('.content-header-title').text                
                    for e in dd.eles('.:md-list-block'):
                        # print(e.text)
                        data={

                            'date':riqi,
                            'geo':geo,
                            "c":c
                        }
                        rawdata=[]
                        for ele in e.children():
                            rawdata.append(ele.raw_text)
                        data['raw']=rawdata

                        # print(data)
                        # if '\r' in data:
                            # data=data.replace('\r','\n')
                        # if '\n' in data:
                            # data=data.replace('\n',',')
                        outfile.add_data([data])
                    print(f'add data {count}-{riqi}')
                print(f"第{count}次查看更多")
                start=end

                ele.click()
                # ele.click(by_js=True)

                # ele.click(by_js=None)
                time.sleep(3)
                count = count + 1
                tab.run_js("document.documentElement.scrollTop=1000")

                
                with open (f'logs/googletrends-{now}.html','w',encoding='utf8') as f:
                    f.write(tab.html)
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
outfile=Recorder(f'ghistrends.csv',cache_size=20)
errorile=Recorder(f'eror.csv',cache_size=1)
w = Worker(getdata, consumer_count=3, block=True)

for geo in geos:
    # url=f'https://trends.google.com.hk/trends/trendingsearches/realtime?geo={geo}&hl=zh-HK&category={c}'
    url=f'https://trends.google.com/trends/trendingsearches/daily?geo={geo}'
    url=f'https://trends.google.com.hk/trends/trendingsearches/daily?geo={geo}'

    data={}
    data["browser"]=browser
    data["url"]=url
    data["outfile"]=outfile
    data["c"]=''
    data["geo"]=geo

    w.put(data)

while not w.is_end():
    time.sleep(3)
outfile.record()
