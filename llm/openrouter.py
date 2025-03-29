from openai import OpenAI

DEFAULT_MODEL = "deepseek/deepseek-r1:free"


def blank_conversation_request(request_content):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",

        # TODO no hard coded data directory
        api_key=open("data/openrouter_api_key.txt", 'r').read(),
    )

    completion = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "user",
                "content": request_content
            }
        ]
    )
    return completion.choices[0].message.content


def test_blank_conversation_request():
    answer = blank_conversation_request('What is the meaning of life?')
    assert len(answer) > 10
    print(answer)
    print('\n\nTest passed')
