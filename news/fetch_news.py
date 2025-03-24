import abc
from dataclasses import dataclass
from datetime import datetime


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


class Nature(NewsSource):
    pass  # TODO


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


def build_news_source(config, news_source_config):
    return DummyNews()
