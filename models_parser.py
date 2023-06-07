import scrapy


class ModelsSpider(scrapy.Spider):
    name = "models_spider"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    }

    file_path = 'car_dataset/model_links.txt'

    def start_requests(self):
        with open("car_models.txt", "r") as file:
            models = file.read().split("\n")
            for model in models:
                yield scrapy.Request(url=f'https://www.otomoto.pl/osobowe/{model}', headers=self.headers)

    def parse(self, response):
        models_div = response.css('ul.ooa-e0hsj.erf161l2')[0]
        models = models_div.css('a.erf161l0::attr(href)').getall()

        with open(self.file_path, "a") as links:
            for model_url in models:
                links.write(model_url + "\n")
