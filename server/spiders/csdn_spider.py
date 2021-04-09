import re
import scrapy
from app.config import CSDN_NAME

from server.items import CsdnBlogItem

class CsdnSpiderSpider(scrapy.Spider):
    name = 'csdn_spider'
    allowed_domains = ['blog.csdn.net']
    start_urls = ['http://blog.csdn.net/' + CSDN_NAME]

    def parse(self, response):
        article_list = response.xpath("//div[@class='article-list']//div[contains(@class, 'article-item-box')]")
        for i_item in article_list:
            blog_item = CsdnBlogItem()
            blog_item['article_id'] = i_item.xpath(".//@data-articleid").extract_first()
            blog_item['title'] = i_item.xpath(".//h4//a//text()[2]").extract_first().strip()
            # blog_item['content'] = i_item.xpath(".//p[@class='content']//a//text()").extract_first().strip()
            blog_item['create_date'] = i_item.xpath(".//span[contains(@class, 'date')]//text()").extract_first().strip()
            blog_item['read_count'] = i_item.xpath(".//span[@class='read-num'][1]//text()").extract_first().strip()
            blog_item['comments_count'] = i_item.xpath(
                ".//span[@class='read-num'][2]//text()").extract_first().strip() if i_item.xpath(
                ".//span[@class='read-num'][2]//text()").extract_first() else 0
            yield blog_item
        current_page = re.compile(r'var[\s]+currentPage[\s]*=[\s]*(\d*?)[\s]*[\;]').findall(response.text)[0]
        page_size = re.compile(r'var[\s]+pageSize[\s]*=[\s]*(\d*?)[\s]*[\;]').findall(response.text)[0]
        list_total = re.compile(r'var[\s]+listTotal[\s]*=[\s]*(\d*?)[\s]*[\;]').findall(response.text)[0]
        if int(list_total) > (int(current_page) * int(page_size)):
            yield scrapy.Request("https://blog.csdn.net/" + "CSDN_NAME" + "/article/list/" + str(int(current_page) + 1),
                                 callback=self.parse)
        pass
