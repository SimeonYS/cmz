import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import CmzItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class CmzSpider(scrapy.Spider):
	name = 'cmz'
	start_urls = ['https://www.cmzrb.cz/en/news/']

	def parse(self, response):

		articles = response.xpath('//div[@class="news-list-item"]')
		for article in articles:
			date = '.'.join([article.xpath('//div[@class="news-list-item-date-inner"]/text()').get() + article.xpath('//div[@class="news-list-item-date-inner"]/span/text()').get()])
			post_links = article.xpath('.//h5/a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//div[@class="d-flex justify-content-between paging-links"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):

		title = response.xpath('//div[@class="page-banner-content"]/h1/text()').get()
		content = response.xpath('//article//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CmzItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
