'''
Created on Mar 23, 2016
File to handle caching data and session management
NYI
@author: Arentios
'''
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': '/cache/data',
    'cache.lock_dir': '/cache/lock'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))

@cache.cache('get_people_data')