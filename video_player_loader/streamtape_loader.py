import requests
import bs4
from ..tools.js_exe import js_runner
import re
from urllib.parse import urlparse
import time


class streamtape(object):
    def __init__(self,player_url) -> None:
        #input origin url:https://streamtape.com/e/XXXXXXXXXXXX
        #no ad url:https://adblocktape.online/e/XXXXXXXXXXXXX
        #mp4 video url:https://adblocktape.online/get_video?id=XXX&expires=XXX&ip=XXX&token=XXX&stream=X
        self.url=player_url
        self.domain = urlparse(self.url).netloc
        self.source_domain='adblocktape.online'
        self.noAD_url= self.url.replace(self.domain,self.source_domain)
        
        
        
    def get_player_info(self) -> None:
        
        req=requests.get(self.noAD_url)
        while req.status_code != requests.codes.ok:
            req=requests.get(self.noAD_url)
        try:
            html=bs4.BeautifulSoup(req.text,features="html.parser")
            get_video_js=html.find_all('script')
            # .text make python 3.8 error , 3.11 is fine
            # get_video_js=[x.text for x in get_video_js if 'robotlink' in str(x)]
            get_video_js=[str(x) for x in get_video_js if 'robotlink' in str(x)]
            robotlink_js=re.findall('\(\'robotlink\'\).innerHTML = (.*)',get_video_js[0])[0]
            end_str=re.findall(' \'(.*)\';',get_video_js[1])[0]
            js_worker=js_runner()
            js_worker.create_js_no_func('robotlink',robotlink_js)
            robotlink=js_worker.run_js('robotlink')
            self.video_url='https:'+robotlink+end_str
        except:
            time.sleep(1)

