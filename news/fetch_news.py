import abc
from dataclasses import dataclass
from crossref.restful import Works
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
import requests


@dataclass
class NewsItem:
    title: str
    authors: list[str]
    source: str
    publish_date: datetime
    doi: str  # Data Object Identifier protocol, may be empty
    summary: str  # "abstract"


class NewsSource:

    @abc.abstractmethod
    def fetch(self) -> list[NewsItem]:
        raise NotImplementedError()


class NatureGroupRSS(NewsSource):

    def __init__(self, url):
        self.url = url

    def fetch(self):
        response = requests.get(self.url)
        response.raise_for_status()
        assert response.content[:5] == b'<rdf:'
        feed = feedparser.parse(response.content)
        news_items = []

        for entry in feed.entries:
            doi = entry.get('prism_doi', '')
            abstract = self.get_abstract(doi)
            news_item = NewsItem(
                title=entry.title,
                authors=[author.name for author in entry.authors] if 'authors' in entry else [],
                source=feed.feed.title,
                publish_date=datetime.fromisoformat(feed.entries[0].updated),
                doi=doi,
                summary=abstract
            )
            news_items.append(news_item)

        return news_items

    def get_abstract(self, doi):
        abstract = crossref_abstract(doi)
        if abstract != '':
            return abstract
        url = f'https://doi.org/{doi}'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        abstract = soup.find('meta', {'name': 'description'})
        if abstract:
            return abstract['content']
        else:
            return ''


def crossref_abstract(doi):
    works = Works()
    metadata = works.doi(doi)
    if 'abstract' not in metadata:
        return ''
    soup = BeautifulSoup(f'<i>{metadata["abstract"]}</i>', 'xml')
    p_element = soup.find('p')
    if p_element is None:
        return ''
    return p_element.get_text(separator=' ', strip=True)


class Science(NewsSource):
    pass  # TODO


class Neuron(NewsSource):
    pass  # TODO


EXAMPLE_NEWS = NewsItem(
    'Emotional responses to commercial entertainment content during aerial travel',
    ['Yishai Gronich', 'Yael Morose'],
    'Journal of Psychology',
    datetime.fromisoformat('2025-03-08'),
    '',
    'Commercial entertainment (TV shows, etc.) can cause various emotional response. '
    'Here we show that aerial travel might increase the potential of emotional response '
    'in some individuals.',
)


class DummyNews(NewsSource):

    def fetch(self):
        return [EXAMPLE_NEWS]


class BioRxivRSS(NewsSource):

    def __init__(self, url):
        self.url = url

    def fetch(self):
        response = requests.get(self.url)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        news_items = []

        for entry in feed.entries:
            news_item = NewsItem(
                title=entry.title,
                authors=[a['name'] for a in entry.get('authors', [])],
                source=feed.feed.title,
                publish_date=datetime.fromisoformat(entry.updated),
                doi=entry.get('dc_identifier', ''),
                summary=entry.get('summary', '')
            )
            news_items.append(news_item)

        return news_items


def build_news_source(config, news_source_config):
    news_source_config = news_source_config.lower()
    if news_source_config == 'nature neuroscience':
        rss_path = 'https://www.nature.com/neuro.rss'
        return NatureGroupRSS(rss_path)
    elif news_source_config == 'biorxiv:neuroscience':
        rss_path = 'https://connect.biorxiv.org/biorxiv_xml.php?subject=neuroscience'
        return BioRxivRSS(rss_path)
    else:
        return DummyNews()


def test():
    news_source = build_news_source(None, 'bioRxiv:Neuroscience')
    news_items = news_source.fetch()
    for item in news_items:
        print(item)
        print('\n' * 2)


test()
