from prometheus_client import Gauge, start_http_server
import requests
import time
import os

response_time_metric = Gauge('website_response_time_seconds', 'Website response time in seconds', ['url'])
WEBSITE_URL = os.getenv('WEBSITE_URL')
PORT = os.getenv('PORT')

WEBSITE_URL = "http://minio.thanhlam.com"
PORT = 8000
def measure_response_time(url):
    try:
        start_time = time.time()
        response = requests.get(url)
        response_time = time.time() - start_time
        response_time_metric.labels(url=url).set(response_time)
    except Exception as e:
        print(f"Error measuring response time for {url}: {e}")

if __name__ == '__main__':
    start_http_server(PORT)
    while True:
        measure_response_time(WEBSITE_URL)
        time.sleep(5)
