# coding=utf-8

import requests
import configparser
import re,json,time,random
import os

# 引入音视频合并的包
from mergemp4tools import Merge

MP4PATH = 'tmpMP4'
if not os.path.exists(MP4PATH):
    os.mkdir(MP4PATH)

MYFILE = 'downloadfile'
if not os.path.exists(MYFILE):
    os.mkdir(MYFILE)

class crawlPDF():
    def __init__(self):
        self.config = configparser.RawConfigParser()  # 类实例化
        self.config.read('config.ini', encoding='utf-8')
        self.url = self.config['base']['url']
        self.cookie = self.config['base']['cookie']
        self.filename = ''
        self.videoSize = 0
        self.audioSize = 0
        self.getVersion()

    def getID(self):
        headers = {
            'cookie':self.cookie,
            'referer':'https://tus.app.box.com/'
        }
        print('原始url:',self.url)
        ret = requests.get(self.url,headers=headers)
        # print('debug getID result:',ret.text)
        try:
            self.id = re.findall('\"itemID\":(.*?),',ret.text)[0]
        except:
            if 'file/' in self.url and '?s=' in self.url:
                self.id = self.url.split('/')[-1].split('?')[0]
            elif 'file/' in self.url:
                self.id = self.url.split('/')[-1]
        try:
            self.requestToken = re.findall('requestToken\":\"(.*?)\"',ret.text)[0]
        except:
            self.requestToken = re.findall('Box.config.requestToken(.*?);',ret.text)[0].replace('=','').replace("'",'').replace(" ",'')
        print('requestToken:',self.requestToken)
        print('ID:',self.id)

    def getToken(self):
        self.getID()
        headers = {
            'cookie':self.cookie,
            'referer':'https://tus.app.box.com/',
            'x-request-token':self.requestToken,
            'request-token':self.requestToken,
            'origin':'https://tus.app.box.com'
        }
        data = {"fileIDs":["file_{}".format(self.id)]}
        ret = requests.post('https://tus.app.box.com/app-api/enduserapp/elements/tokens', headers=headers,json=data)
        self.accesstoken = json.loads(ret.text)['file_{}'.format(self.id)]['read']
        self.writetoken = json.loads(ret.text)['file_{}'.format(self.id)]['write']


    def getVersion(self):
        self.getToken()
        if 'file/' in self.url:
            referer = '/'.join(self.url.split('/')[:-2])
        else:
            referer = self.url
        print('referer:',referer)
        url = 'https://api.box.com/2.0/files/{}' \
              '?fields=permissions,shared_link,sha1,file_version,name,size' \
              ',extension,representations,watermark_info,' \
              'authenticated_download_url,is_download_available'.format(self.id)
        headers = {
            'boxapi':'shared_link={}'.format(referer),
            'authorization':'Bearer {}'.format(self.writetoken)
        }
        ret = requests.get(url,headers=headers)
        self.version = json.loads(ret.text)['file_version']['id']
        self.SIZE = json.loads(ret.text)['size']
        # 日 1
        self.filename = json.loads(ret.text)['name'].replace(' ','').replace('\n','').replace(' ','')

    def getPDF(self):
        # self.getVersion()
        print('version:',self.version)
        url = 'https://dl.boxcloud.com/api/2.0/files/{}/content'.format(self.id)
        print(url)
        params = {
            'preview':'true',
            'version':self.version,
            'access_token':self.accesstoken,
            'shared_link':self.url,
            'box_client_name':'box-content-preview',
            'box_client_version':'2.80.0',
            'encoding':'gzip'
        }
        headers = {
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'origin':'https://tus.app.box.com',
            'referer':'https://tus.app.box.com/',
        }
        ret = requests.get(url,params=params,headers=headers)
        print('下载到的pdf文件大小为:',len(ret.text))
        f = open('downloadfile/'+self.filename,'wb')
        f.write(ret.content)
        f.close()


    def getMP4Video(self,page,video):
        if page == 0:
            # self.getVersion()
            page = 'init'
        if 'file/' in self.url:
            referer = '/'.join(self.url.split('/')[:-2])
        else:
            referer = self.url
        data = 'audio' if video == 0 else 'video'
        params = {
            'access_token': self.accesstoken,
            'shared_link': referer,
            'box_client_name': 'box-content-preview',
            'box_client_version': '2.80.0'
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'origin': 'https://tus.app.box.com',
            'referer': 'https://tus.app.box.com/',
        }
        url = 'https://dl.boxcloud.com/api/2.0/internal_files/{}/versions/{}/representations/dash/content/{}/{}/{}.m4s'.format(self.id,self.version,data,video,page)
        try:
            ret = requests.get(url,params=params,headers=headers,timeout=60)
        except:
            for _ in range(3):
                try:
                    ret = requests.get(url, params=params, headers=headers, timeout=60)
                    break
                except:
                    time.sleep(3)
                    continue
        try:
            tmp = json.loads(ret.text)
            print(tmp)
            return False
        except:
            pass
        if page == 0 or page == 'init':
            f = open('{}/test{}.m4s'.format(MP4PATH,data),'wb')
        else:
            f = open('{}/test{}.m4s'.format(MP4PATH,data),'ab')
        if data == 'video':
            self.videoSize += len(ret.text)
        else:
            self.audioSize += len(ret.content)
        f.write(ret.content)
        f.close()
        return True


    def controlMP4(self):
        page = int(self.config['mp4conf']['start'])
        endPage = int(self.config['mp4conf']['end'])
        while True:
            print('已经在获取文件，先不要停止程序'.format(page))
            if not crawl.getMP4Video(page, 1080):
                break
            if not crawl.getMP4Video(page, 0):
                break
            if page > endPage:
                break
            print('音视频第【{}】份文件爬取成功,现在可以停止程序，请记录编号，将编号【{}】设置到config.ini的start'.format(page,page+1))
            page+=1
            time.sleep(random.randint(3,5))

crawl = crawlPDF()
if '.mp4' in crawl.filename:
    print('{}-->mp4'.format(crawl.url))
    crawl.controlMP4()
    Merge(crawl.filename)
else:
    print('{}-->pdf'.format(crawl.url))
    crawl.getPDF()