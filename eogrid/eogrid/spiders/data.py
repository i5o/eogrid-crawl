# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy import Request
from scrapy.http import FormRequest
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

USER_NAME = 'user'
PASSWORD = 'passwd'
formdata = {
    'cn': USER_NAME,
    'password': PASSWORD,
    'idleTime': 'halfaday',
    'sessionTime': 'oneday'
}


class DataSpider(Spider):
    name = "data"
    links = []
    visited = []  # just in case
    logintry = 1

    def __init__(self):
        dispatcher.connect(self.crawl_over, signals.spider_closed)

    def crawl_over(self, spider):
        f = open("links.txt", "w")
        f.write("\n".join(self.links))
        f.close()

    def start_requests(self):
        yield Request(url='https://eogrid.esrin.esa.int/login.php', callback=self.login)

    def login(self, response):
        if self.logintry <= 2:
            yield FormRequest.from_response(
                response,
                formdata=formdata,
                callback=self.login,
                dont_filter=True)
            self.logintry += 1
        else:
            yield Request(url="http://eogrid.esrin.esa.int/browse", callback=self.parse_mission)

    def parse_mission(self, response):
        links = response.xpath('.//a[@class="mainlinkmenu"]/@href').extract()
        for link in links:
            link = "https://eogrid.esrin.esa.int%s" % link
            if "https://eogrid.esrin.esa.int/download/" in link.lower():
                self.links.append(link)
                return
            if link not in self.visited:
                self.visited.append(link)
                yield Request(url=link, callback=self.parse_mission)
