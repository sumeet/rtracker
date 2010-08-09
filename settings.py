import redis

redis_servers = [
	redis.Redis(port=6379),
	redis.Redis(port=6380),
	redis.Redis(port=6381),
	redis.Redis(port=6382),
]