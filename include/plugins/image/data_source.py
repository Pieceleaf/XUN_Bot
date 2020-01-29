import json
import requests
from lxml import etree
import sys

sys.path.append('../../../')
from config import TIMELIMIT_IMAGE
from kth_timeoutdecorator import *

class SauceNAO:

    def __init__(self, api_key, output_type=2, testmode=0, dbmask=None, dbmaski=None, db=999, numres=3, shortlimit=20, longlimit=300):
        params = dict()
        params['api_key'] = api_key
        params['output_type'] = output_type
        params['testmode'] = testmode
        params['dbmask'] = dbmask
        params['dbmaski'] = dbmaski
        params['db'] = db
        params['numres'] = numres
        self.params = params
        self.header = "————>saucenao<————"


    def get_sauce(self, url):
        self.params['url'] = url
        response = requests.get('https://saucenao.com/search.php', params=self.params)
        data = response.json()
        
        return data

    def get_view(self, sauce) -> str:
        sauces = self.get_sauce(sauce)

        repass = ""
        try:
            for sauce in sauces['results']:
                url = sauce['data']['ext_urls'][0].replace("\\","").strip()
                similarity = sauce['header']['similarity']
                putline = "[{}] 相似度:{}%".format(url, similarity)
                if repass:
                    repass = "\n".join([repass, putline])
                else:
                    repass = putline
        except Exception as e:
            pass

        return repass


class ascii2d:

    def __init__(self, num=2):
        self.num = num
        self.header = "————>ascii2d<————"

    def get_search_data(self, url: str, data=None):
        if data is not None:
            html = data
        else:
            html_data = requests.get(url)
            html = etree.HTML(html_data.text)

        all_data = html.xpath('//div[@class="detail-box gray-link"]/h6')
        info = []
        for data in all_data[:self.num]:
            info_url = data.xpath(".//a/@href")[0].strip()
            tag = (data.xpath("./small/text()") or data.xpath(".//a/text()"))[0].strip()
            info.append([info_url, tag])

        return info

    def add_repass(self, tag: str, data):
        po = "——{}——".format(tag)
        for line in data:
            putline = "[{}][{}]".format(line[1], line[0])
            po = "\n".join([po, putline])

        return po

    def get_view(self, ascii2d) -> str:
        repass = ''
        url_index = "https://ascii2d.net/search/url/{}".format(ascii2d)
        # print("url_index: ", url_index)
        html_index_data = requests.get(url_index)
        print("[info]index html data OK.")
        html_index = etree.HTML(html_index_data.text)

        neet_div = html_index.xpath('//div[@class="detail-link pull-xs-right hidden-sm-down gray-link"]')

        if neet_div:
            a_url_foot = neet_div[0].xpath('./span/a/@href')
            url2 = "https://ascii2d.net{}".format(a_url_foot[1])

            color = self.get_search_data('', data=html_index)
            bovw = self.get_search_data(url2)

            if color and bovw:
                putline1 = self.add_repass("色调检索", color)
                putline2 = self.add_repass("特征检索", bovw)
            repass = "\n".join([putline1, putline2])

        return repass


@timeout(TIMELIMIT_IMAGE)
async def get_view(sc, image_url: str) -> str:
    header = sc.header
    print("[info]Now starting get the {}".format(header))
    view = ''
    putline = ''

    view = sc.get_view(image_url)

    if view:
        putline = "\n\n".join([header, view])
        print("[info]Loading {} page succeeded".format(header))
    else: print("[warning]Loading {} page failed".format(header))

    return putline

async def get_image_data(image_url: str, api_key: str):
    if type(image_url) == list:
        image_url = image_url[0]

    print("[info]Loading Image Search Container……")
    NAO = SauceNAO(api_key)
    ii2d = ascii2d()

    print("[info]Loading all view……")
    repass = ''
    for sc in [NAO, ii2d]:
        try:
            putline = await get_view(sc, image_url)
            if putline:
                if repass:
                    repass = "\n\n".join([repass, putline])
                else:
                    repass = putline
        except TimeoutException as e:
            print("[warning] {}".format(e))

    return repass
