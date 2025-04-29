import abc
import logging
import random

from llm.openrouter import blank_conversation_request


class TopicChecker:

    def check(self, items, topics):
        cache = {}  # between (item title, topic) and True/False
        identified_topics = []
        for item in items:
            identified = []
            for topic in topics:
                key = (item.title, topic)
                if key not in cache:
                    cache[key] = self.check_single(item, topic)
                identified.append(cache[key])
            identified_topics.append(identified)
        return identified_topics

    @abc.abstractmethod
    def check_single(self, item, topic):
        return NotImplementedError()


class RandomChecker(TopicChecker):

    def check_single(self, item, topic):
        return random.randint(0, 1)


class LLMChecker(TopicChecker):

    def check_single(self, item, topic):
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
            logging.debug('Response is %s', repr(response))
        if response not in ['True', 'False']:
            logging.error("Invalid response from LLM: %s", repr(response))
            return False
        return response == 'True'


def build_topic_checker(config):
    return LLMChecker()
