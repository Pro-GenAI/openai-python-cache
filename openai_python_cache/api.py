
import json
import time

from typing import Optional
import openai

from openai_python_cache.provider import Sqlite3CacheProvider

DEFAULT_CACHE_PROVIDER = Sqlite3CacheProvider()


def create_chat_completion(
    cache_provider: Optional[Sqlite3CacheProvider] = DEFAULT_CACHE_PROVIDER,
    *args,
    **kwargs,
):
    """
    Creates a new chat completion for the provided messages and parameters.
    See https://platform.openai.com/docs/api-reference/chat-completions/create
    for a list of valid parameters.
    """
    params = kwargs

    if cache_provider is not None:
        cache_key = cache_provider.hash_params(params)
        cached_response = cache_provider.get(cache_key)
        if cached_response:
            # Cache hit, return the cached response
            return json.loads(cached_response)

        # Cache miss, make the request and cache it
        while True:
            try:
                response = openai.chat.completions.create(*args, **kwargs)
                cache_provider.insert(cache_key, params, dict(response))
                return response
            except openai.RateLimitError:
                time.sleep(30)
                pass
            except openai.APIStatusError as e:
                raise e
            except Exception as e:
                raise e
