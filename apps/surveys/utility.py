def generate_cache_key(endpoint_identifier, query_params):
    query_params: dict = {key: value for key, value in query_params.items()}
    sorted_query_params: dict = {param: query_params[param] for param in sorted(query_params)}
    query_params: str = '&'.join(f'{key}={value}' for key, value in sorted_query_params.items())
    cache_key: str = f'{endpoint_identifier}_query_params_{query_params}'

    return cache_key
