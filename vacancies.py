from urllib.parse import urljoin

import scrapy
from scrapy.http import Response


class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["djinni.co"]
    start_urls = ["https://djinni.co/jobs/?primary_keyword=Data+Analyst"]

    def parse(self, response: Response, **kwargs):
        for vacancy in response.css("div.position-relative"):
            url = vacancy.css("a.job-list-item__link::attr(href)").get()
            yield response.follow(url, callback=self.parse_vacancy)

        next_page = response.css(".pagination > li")[-1].css("a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_vacancy(self, vacancy: Response):
        location = vacancy.css("span.location-text::text").get().split(",")
        country = location[0].strip()
        relocate = ",".join(location[1:]).strip() if len(location) > 1 else None
        city = vacancy.css('span.location-text > span::text').get()
        formatted_location = f"{country}, {relocate} {city}"
        text = vacancy.css("div.text-muted::text").getall()
        date = [str(item.strip()).split(" ") for item in text][1][-3:-1]
        views = [str(item.strip()).split(" ") for item in text][3][0]
        reviews = [str(item.strip()).split(" ") for item in text][4][0]

        yield {
            "company": vacancy.css("a.job-details--title::text").get().strip(),
            "title": vacancy.css("div.col > h1::text").get().strip(),
            "type_of_company": vacancy.css("ul:nth-of-type(3) li:nth-child(3) div.col.pl-2::text").get(),
            "technologies": vacancy.css("ul:nth-of-type(2) li:nth-child(2) div.col.pl-2::text").get(),
            "salary": vacancy.css(".public-salary-item::text").get().strip(),
            "workplace": vacancy.css("ul:nth-of-type(3) li:nth-child(2) div.col.pl-2::text").get(),
            "location": formatted_location,
            "test_task": vacancy.css("ul:nth-of-type(3) li:nth-child(5) div.col.pl-2::text").get(),
            "date": date,
            "views": views,
            "reviews": reviews,
        }
        