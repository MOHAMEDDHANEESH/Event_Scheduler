import urllib.request
import urllib.error

def check_url(url):
    print(f"Checking URL: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            print(f"Status Code: {response.getcode()}")
            content = response.read(200)
            print(f"Content snippet: {content}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read())
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
    except Exception as e:
        print(f"Generic Error: {e}")

if __name__ == "__main__":
    check_url("http://127.0.0.1:5000/events")
