import asyncio
import aiohttp

from selectolax.parser import HTMLParser

from .storage import SimpleStorage
from .realty import realty_factory
from .parser import (
    AvitoJsParser,
    AvitoHtmlParser,
    AvitoJsParserError,
    AvitoJsParserDisabledError,
    AvitoHtmlParserError,
    AvitoHtmlParserDisabledError
)


class AvitoParserError(Exception):
    pass


class Avito:
    __base_url = 'https://www.avito.ru'
    __mbase_url = 'https://m.avito.ru'

    def __init__(self, location, category, headers=None, from_page=1, pages=10, pool_size=3,
                 session=None, loop=None, id_separator='._', storage=None, exclude_ids=None):

        self.semaphore = asyncio.BoundedSemaphore(pool_size)
        self.loop = loop

        self.exclude_ids = set(exclude_ids) if isinstance(exclude_ids, (list, set)) else set()

        self.headers = headers
        self.id_separator = id_separator

        self.realty = realty_factory(self)()
        self.storage = storage if storage else SimpleStorage()

        self.session = session

        self.location = location
        self.category = category
        self.from_page = from_page
        self.pages = pages + 1

    def build_headers(self, **kwargs):
        _headers = {k: v for k, v in kwargs.items() if k and v}

        try:
            return {**self.headers, **_headers}
        except TypeError:
            return _headers

    async def get(self, url, headers=None):
        async with self.semaphore, self.session.get(url, headers=headers) as response:
            return await response.text()

    async def post(self, url, data, headers=None):
        async with self.semaphore, self.session.get(url, headers=headers, data=data) as response:
            return await response.text()

    async def uncaptcha(self, captcha_link):
        ch = self.build_headers(referer="https://www.avito.ru/blocked")
        image = await self.get(self.__base_url + captcha_link, headers=ch)
        await self.post(self.__base_url + captcha_link, data=image, headers=ch)
        # TODO

    async def card_links(self):
        results, candidates = list(), ['{}/{}/{}?p={}'.format(self.__base_url, self.location, self.category, p)
                                          for p in range(self.from_page, self.pages)]

        headers = self.build_headers(referer="{}/{}".format(self.__base_url, self.location))

        while candidates:
            candidate = candidates.pop()
            html = await self.get(candidate, headers=headers)

            # ссылки на объявления парсим согласно self.realty.__cardFilters
            # они сохранятся в self под атрибутом указанном в self.realty.__cardFilters
            AvitoHtmlParser(HTMLParser(html), self, filters=self.realty.cardFilters).parse()

            card_links = getattr(self, 'card_links', [])
            captcha = getattr(self, "captcha", None)

            if card_links and not captcha:
                results.extend(card_links)
            elif captcha:
                candidates.extend(candidate)
                await self.uncaptcha(captcha)

        # card_links - ключ фильтра, см. realty/flat.py для примера
        return [link for link in results if link.split(self.id_separator)[-1] not in self.exclude_ids]

    async def start(self):
        results, candidates = list(), await self.card_links()
        while candidates:
            candidate = candidates.pop()
            card_link = "{}/{}".format(self.__base_url, candidate)
            headers = self.build_headers(referer=card_link)
            html = await self.get(card_link, headers=headers)

            so_tree = HTMLParser(html)

            try:
                AvitoHtmlParser(so_tree, self.realty, filters=self.realty.htmlFilters).parse()
            except AvitoHtmlParserDisabledError as e:
                # TODO log facility info
                print('AvitoHtmlParserDisabledError')
            except AvitoHtmlParserError as e:
                # TODO log facility error
                print('AvitoHtmlParserError')

            try:
                AvitoJsParser(so_tree, self.realty, filters=self.realty.jsFilters).parse()
            except AvitoJsParserDisabledError as e:
                # TODO log facility info
                print('AvitoJsParserDisabledError')
            except AvitoJsParserError as e:
                # TODO log facility error
                print('AvitoJsParserError')

            html = await self.get(self.__mbase_url + card_link)

            try:
                AvitoHtmlParser(HTMLParser(html), self.realty, filters=self.realty.exFilters).parse()
            except AvitoHtmlParserDisabledError as e:
                # TODO log facility info
                print('EX AvitoHtmlParserDisabledError')
            except AvitoHtmlParserError as e:
                # TODO log facility error
                print('EX AvitoHtmlParserError')

            try:
                # в ключе кортеж с параметрами, для быстрой обработки
                r = self.realty.toDict()
                key = (r.get('id'), r.get('phone'))
                self.storage.push(key, r)
            except (Exception, AttributeError) as e:
                raise AvitoParserError(e)

    def run(self):
        if not self.loop:
            self.loop = asyncio.get_event_loop()

        if not self.session:
            self.session = aiohttp.ClientSession(loop=self.loop)

        self.loop.run_until_complete(self.start())
        self.loop.run_until_complete(asyncio.sleep(0.250))

        self.session.close()
        self.loop.close()
