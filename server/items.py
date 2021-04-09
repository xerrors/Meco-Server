# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CsdnBlogItem(scrapy.Item):
    # define the fields for your item here like:
    article_id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    create_date = scrapy.Field()
    read_count = scrapy.Field()
    comments_count = scrapy.Field()
