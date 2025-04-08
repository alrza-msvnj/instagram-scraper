import json
import httpx

client = httpx.Client(
    headers={
        "cookie": "sessionid=11465298300%3AKokynTDsi6qlQ5%3A8%3AAYeXI77t8VXQ3VerafqocuXq1Y0wjN9c8yciqKk6Hw; csrftoken=2XVG20S0C9mb3MX-hXn9T7;",
        # this is internal ID of an instegram backend app. It doesn't change often.
        "x-ig-app-id": "936619743392459",
        # use browser-like features
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
)


def scrape_user(username: str):
    """Scrape Instagram user's data"""
    result = client.get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
    )
    data = json.loads(result.content)
    return data["data"]["user"]

print(scrape_user("lorem.ipsum.v0"))