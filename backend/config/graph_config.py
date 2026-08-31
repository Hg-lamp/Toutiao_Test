from langgraph.types import RetryPolicy

retry_policy=RetryPolicy(
    max_attempts=3,
    initial_interval=1.0,#首次重试等待一秒
    max_interval=10.0,#最大等待时间为10秒
    backoff_factor=2.0,#指数退避因子为2
    jitter=True,#启用抖动，防止多个重试同时发生
)