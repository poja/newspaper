import abc
import logging
import random

from llm.openrouter import blank_conversation_request


class TopicChecker:

    @abc.abstractmethod
    def check(self, items, topics):
        return NotImplementedError()


class RandomChecker(TopicChecker):

    def check(self, items, topics):
        return [
            [random.randint(0, 1) for topic in topics]
            for item in items
        ]


class LLMChecker(TopicChecker):

    def check(self, items, topics):
        print(items)
        print(topics)
        return [
            [self._check_single(item, topic) for topic in topics]
            for item in items
        ]

    def _check_single(self, item, topic):
        query = (f"I will give you the title of a scientific article, then its "
                 f"abstract, then a scientific topic. You need to decide if the "
                 f"paper is about the given topic or not. Your response must be "
                 f"one word, either 'True' or 'False'. \n\n"
                 f"TITLE: {item.title}\n"
                 f"ABSTRACT: {item.summary}\n"
                 f"TOPIC: {topic}")
        logging.debug(query)
        response = ''
        while response == '':
            response = blank_conversation_request(query).strip()
            logging.debug('Response is', repr(response))
        assert response in ['True', 'False']
        return response == 'True'


def build_topic_checker(config):
    return LLMChecker()
