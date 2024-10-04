import time
headers = {
    'action': '',
    'content-type': 'application/json',
    'user-agent': 'PostmanRuntime/7.42.0',
    'accept': '*/*',
    'cache-control': 'no-cache',
    'postman-token': '9515eaa8-7252-4354-aea8-ff289e94389d',
    'host': 'localhost:8000',
    'accept-encoding': 'gzip, deflate, br',
    'connection': 'keep-alive',
    'content-length': '22'
}

# Check if 'action' key exists
if headers.get('action', '') == 'abc':
    print("Key 'action' found:", headers['action'])
else:
    print("Error: 'action' key is missing in headers.")

for i in range(1000):
    print(f'transaction from: {i}')
