import time

from typing import Optional
import openai
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from openai_python_cache.provider import Sqlite3CacheProvider


DEFAULT_CACHE_PROVIDER = Sqlite3CacheProvider()


def create_chat_completion(
    cache_provider: Optional[Sqlite3CacheProvider] = DEFAULT_CACHE_PROVIDER,
    **kwargs,
):
    """
    Creates a new chat completion for the provided messages and parameters.
    See https://platform.openai.com/docs/api-reference/chat-completions/create
    for a list of valid parameters.
    """

    if cache_provider is not None:
        cache_key = cache_provider.hash_params(kwargs)
        cached_response = cache_provider.get_response(cache_key)
        if cached_response:
            return ChatCompletion(
                id="cached-" + cache_key,
                created=int(time.time()),
                model=kwargs.get("model", ""),
                object="chat.completion",
                choices=[
                    Choice(
                        message=ChatCompletionMessage(
                            content=cached_response, role="assistant"
                        ),
                        index=0,
                        finish_reason="stop",
                    ),
                ],
            )

        # Cache miss, make the request and cache it
        while True:
            try:
                response: ChatCompletion = openai.chat.completions.create(**kwargs)
                cache_provider.insert(
                    cache_key, kwargs, response.choices[0].message.content or ""
                )
                return response
            except openai.RateLimitError:
                time.sleep(30)
                pass
            except openai.APIStatusError as e:
                raise e
            except Exception as e:
                raise e
