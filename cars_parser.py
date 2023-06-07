import scrapy
import csv


class CarsSpider(scrapy.Spider):
    name = "cars_spider"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    }
    car_attributes = ['Rok produkcji',
                      'Przebieg',
                      'Pojemnosc skokowa',
                      'Rodzaj paliwa']
    csv_path = 'cars.csv'

    def start_requests(self):
        with open("models_links.txt", "r") as file:
            links = file.read().split("\n")
            for link in links:
                yield scrapy.Request(url=f'{link}?page=1', headers=self.headers, callback=self.parse, meta={
                    'dont_redirect': True,
                    'handle_httpstatus_list': [302]
                },
                    cb_kwargs={
                    'page': 1,
                    'link': link
                })

    def parse(self, response, page, link):
        ad_elements = response.css('[data-testid="listing-ad"]')

        for element in ad_elements:
            car_data = self.parse_car_data(response.url, element)
            self.write_car_data_to_csv(car_data, self.csv_path)

        try:
            last_page = int(response.css(
                'li[data-testid="pagination-list-item"]')[-1].attrib['aria-label'].split()[-1])
        except IndexError:
            last_page = 1

        if page + 1 < last_page:
            next_page_url = f'{link}?page={page+1}'

            yield scrapy.Request(url=next_page_url, headers=self.headers, callback=self.parse, meta={
                'dont_redirect': True,
                'handle_httpstatus_list': [302]
            },
                cb_kwargs={
                'page': page + 1,
                'link': link
            })

    def parse_car_data(self, url, raw_data):
        brand = url.split('/')[-2]
        model = url.split('/')[-1].split('?')[0]

        li_elements = raw_data.css('li.ooa-1k7nwcr.e19ivbs0')

        values = [value.strip()
                  for value in li_elements.css('::text').getall()]
        
        if values[0] == "Niski przebieg":
            del values[0]
            
        if "km" not in values[1]:
            values.insert(1, "0 km")
        
        if values[2] in ["Elektryczny", "Hybryda"]:
            values[3] = values[2]
            values[2] = "0 cm3"

        car_data = {'Marka pojazdu': brand, 'Model pojazdu': model}

        for key, value in zip(self.car_attributes, values):
            car_data[key] = value.strip()

        car_data['Cena'] = raw_data.css(
            'span.ooa-1bmnxg7.evg565y11::text').get()
        return car_data

    def write_car_data_to_csv(self, car_data, path):
        with open(path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Marka pojazdu',
                                                   'Model pojazdu',
                                                   'Rok produkcji',
                                                   'Przebieg',
                                                   'Pojemnosc skokowa',
                                                   'Rodzaj paliwa',
                                                   'Cena'])
            writer.writerow(car_data)
