# -*- coding: utf-8 -*-

import requests
import configparser
import re, json, time, random
from concurrent.futures import ThreadPoolExecutor
import os


# 引入音视频合并的包
from mergemp4tools import Merge

box_client_version = '2.84.0'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
# user_agents = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'

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
        self.quality = self.config['base']['quality']
        self.cookie = self.config['base']['cookie']
        self.pool = self.config['base']['pool']
        self.filename = ''
        self.videoSize = 0
        self.audioSize = 0
        self.getVersion()

    def getID(self):
        headers = {
            'cookie': self.cookie,
            'referer': 'https://tus.app.box.com/'
        }
        print('原始url:', self.url)
        ret = requests.get(self.url, headers=headers)
        # print('debug getID result:',ret.text)
        try:
            self.id = re.findall('\"itemID\":(.*?),', ret.text)[0]
        except:
            if 'file/' in self.url and '?s=' in self.url:
                self.id = self.url.split('/')[-1].split('?')[0]
            elif 'file/' in self.url:
                self.id = self.url.split('/')[-1]
        try:
            self.requestToken = re.findall('requestToken\":\"(.*?)\"', ret.text)[0]
        except:
            self.requestToken = re.findall('Box.config.requestToken(.*?);', ret.text)[0].replace('=', '').replace("'",
                                                                                                                  '').replace(
                " ", '')
        print('requestToken:', self.requestToken)
        print('ID:', self.id)

    def getToken(self):
        self.getID()
        headers = {
            'cookie': self.cookie,
            'referer': 'https://tus.app.box.com/',
            'x-request-token': self.requestToken,
            'request-token': self.requestToken,
            'origin': 'https://tus.app.box.com'
        }
        data = {"fileIDs": ["file_{}".format(self.id)]}
        ret = requests.post('https://tus.app.box.com/app-api/enduserapp/elements/tokens', headers=headers, json=data)
        self.accesstoken = json.loads(ret.text)['file_{}'.format(self.id)]['read']
        self.writetoken = json.loads(ret.text)['file_{}'.format(self.id)]['write']

    def getVersion(self):
        self.getToken()
        if 'file/' in self.url:
            referer = '/'.join(self.url.split('/')[:-2])
        else:
            referer = self.url
        print('referer:', referer)
        url = 'https://api.box.com/2.0/files/{}' \
              '?fields=permissions,shared_link,sha1,file_version,name,size' \
              ',extension,representations,watermark_info,' \
              'authenticated_download_url,is_download_available'.format(self.id)
        headers = {
            'boxapi': 'shared_link={}'.format(referer),
            'authorization': 'Bearer {}'.format(self.writetoken)
        }
        ret = requests.get(url, headers=headers)
        self.version = json.loads(ret.text)['file_version']['id']
        self.SIZE = json.loads(ret.text)['size']
        # 日 1
        self.filename = json.loads(ret.text)['name'].replace(' ', '').replace('\n', '').replace(' ', '')

    def getPDF(self):
        # self.getVersion()
        print('version:', self.version)
        url = 'https://dl.boxcloud.com/api/2.0/files/{}/content'.format(self.id)
        print(url)
        params = {
            'preview': 'true',
            'version': self.version,
            'access_token': self.accesstoken,
            'shared_link': self.url,
            'box_client_name': 'box-content-preview',
            'box_client_version': box_client_version,
            'encoding': 'gzip'
        }
        headers = {
            'user-agent': UA,
            'origin': 'https://tus.app.box.com',
            'referer': 'https://tus.app.box.com/',
        }
        ret = requests.get(url, params=params, headers=headers)
        print('下载到的pdf文件大小为:', len(ret.text))
        f = open('downloadfile/' + self.filename, 'wb')
        f.write(ret.content)
        f.close()

    def download_m4s(self, page):
        if page == 0:
            page = 'init'
        for video in [0, self.quality]:
            data = 'audio' if video == 0 else 'video'
            if 'file/' in self.url:
                referer = '/'.join(self.url.split('/')[:-2])
            else:
                referer = self.url

            params = {
                'access_token': self.accesstoken,
                'shared_link': referer,
                'box_client_name': 'box-content-preview',
                'box_client_version': '2.84.0'
            }
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
                'origin': 'https://tus.app.box.com',
                'referer': 'https://tus.app.box.com/',
            }
            url = 'https://dl.boxcloud.com/api/2.0/internal_files/{}/versions/{}/representations/dash/content/{}/{}/{}.m4s'.format(
                self.id, self.version, data, video, page)

            try:
                resp = requests.get(url=url, params=params, headers=headers, timeout=60)
            except:
                for _ in range(3):
                    try:
                        resp = requests.get(url, params=params, headers=headers, timeout=60)
                        break
                    except:
                        time.sleep(3)
                        continue
            try:
                tmp = json.loads(resp.text)
                print(tmp)
                return False
            except:
                pass
            if data == 'video':
                with open(f"video/{page}.m4s", mode="wb") as f:
                    f.write(resp.content)  # 把下载到的内容写入到文件中

            else:
                with open(f"audio/{page}.m4s", mode="wb") as f:
                    f.write(resp.content)  # 把下载到的内容写入到文件中

            print(f"{data}/{page}.m4s下载完毕")

    def main(self):
        page = int(self.config['mp4conf']['start'])
        endPage = int(self.config['mp4conf']['end'])

        with ThreadPoolExecutor(50) as t:
            for p in range(page, endPage+1):
                t.submit(self.download_m4s, p)
                t.submit(self.download_m4s, p)

    def combine(self):
        endPage = int(self.config['mp4conf']['end'])
        file_read = open("video/init.m4s", "rb")
        file_write = open("testvideo.m4s", "wb")

        text = file_read.read()
        file_write.write(text)

        file_read.close()
        file_write.close()

        file_read = open("audio/init.m4s", "rb")
        file_write = open("testaudio.m4s", "wb")

        text = file_read.read()
        file_write.write(text)

        file_read.close()
        file_write.close()

        for page in range(1, endPage + 1):
            file_read = open(f"video/{page}.m4s", "rb")
            file_write = open("testvideo.m4s", "ab")

            text = file_read.read()
            file_write.write(text)

            file_read.close()
            file_write.close()

            file_read = open(f"audio/{page}.m4s", "rb")
            file_write = open("testaudio.m4s", "ab")

            text = file_read.read()
            file_write.write(text)

            file_read.close()
            file_write.close()


crawl = crawlPDF()
if '.mp4' in crawl.filename:
    print('{}-->mp4'.format(crawl.url))
    crawl.main()
    crawl.combine()
    Merge(crawl.filename)

else:
    print('{}-->pdf'.format(crawl.url))
    crawl.getPDF()
