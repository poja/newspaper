import jinja2
import numpy as np

from news.fetch_news import EXAMPLE_NEWS

news_template = jinja2.Template("""
Hi {{ username }}!

Your news feed for today is:

{% for i in range(len_news_items) -%}
{% if identified_topics[i].sum() > 0 -%}
### {{ news_items[i]['title'] }}
*Authors*: {{ news_items[i]['authors'] }}
*Journal*: {{ news_items[i]['source'] }}
*Publish date*: {{ news_items[i]['publish_date'] }}
*Topics*: {% for topic_i in range(len_topic_options) %} {% if identified_topics[i][topic_i] %}{{ topic_options[topic_i] }} {% endif %}{% endfor %}
*Link*: {%if news_items[i]['doi'] %}http://doi.org/{{ news_items[i]['doi'] }}{%else%}Not found{%endif%}

{%- endif %}
{%- endfor %}
""")

no_news_template = jinja2.Template("""
Hi {{ username }}!

No news found since you were last updated.
""")


def build_message(config, username, news_items, topic_options, identified_topics):
    if np.sum(identified_topics) == 0:
        return no_news_template.render(username=username)
    else:
        return news_template.render(
            username=username,
            news_items=news_items,
            len_news_items=len(news_items),
            topic_options=topic_options,
            len_topic_options=len(topic_options),
            identified_topics=np.array(identified_topics))


def test():
    print(
        build_message(None,
                      'Yishai',
                      [EXAMPLE_NEWS],
                      ['Psychology'],
                      [[1]])
    )
