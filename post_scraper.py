import httpx
import json
from typing import Dict, Optional
from urllib.parse import quote

from parsers import parse_post

INSTAGRAM_DOCUMENT_ID = "8845758582119845"  # contst id for post documents instagram.com
INSTAGRAM_ACCOUNT_DOCUMENT_ID = "9310670392322965"


def scrape_post(url_or_shortcode: str) -> Dict:
    """Scrape single Instagram post data"""
    if "http" in url_or_shortcode:
        shortcode = url_or_shortcode.split("/p/")[-1].split("/")[0]
    else:
        shortcode = url_or_shortcode
    print(f"scraping instagram post: {shortcode}")

    variables = quote(json.dumps({
        'shortcode': shortcode, 'fetch_tagged_user_count': None,
        'hoisted_comment_id': None, 'hoisted_reply_id': None
    }, separators=(',', ':')))
    body = f"variables={variables}&doc_id={INSTAGRAM_DOCUMENT_ID}"
    url = "https://www.instagram.com/graphql/query"

    result = httpx.post(
        url=url,
        headers={"content-type": "application/x-www-form-urlencoded"},
        data=body
    )
    data = json.loads(result.content)
    return data["data"]["xdt_shortcode_media"]


async def scrape_user_posts(username: str, page_size=12, max_pages: Optional[int] = None):
    """Scrape all posts of an Instagram user given the username."""
    base_url = "https://www.instagram.com/graphql/query"
    variables = {
        "after": None,
        "before": None,
        "data": {
            "count": page_size,
            "include_reel_media_seen_timestamp": True,
            "include_relationship_info": True,
            "latest_besties_reel_media": True,
            "latest_reel_media": True
        },
        "first": page_size,
        "last": None,
        "username": f"{username}",
        "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True,
        "__relay_internal__pv__PolarisShareSheetV3relayprovider": True
    }

    prev_cursor = None
    _page_number = 1

    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as session:
        while True:
            body = f"variables={quote(json.dumps(variables, separators=(',', ':')))}&doc_id={INSTAGRAM_ACCOUNT_DOCUMENT_ID}"

            response = await session.post(
                base_url,
                data=body,
                headers={"content-type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            data = response.json()

            with open("ts2.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            posts = data["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]
            for post in posts["edges"]:
                yield post["node"]

            page_info = posts["page_info"]
            if not page_info["has_next_page"]:
                print(f"scraping posts page {_page_number}")
                break

            if page_info["end_cursor"] == prev_cursor:
                print("found no new posts, breaking")
                break

            prev_cursor = page_info["end_cursor"]
            variables["after"] = page_info["end_cursor"]
            _page_number += 1

            if max_pages and _page_number > max_pages:
                break


# Example usage:
# post = scrape_post("https://www.instagram.com/p/DIH5xdXtbFj/")
# parsed_post = parse_post(post)
#
# # save a JSON file
# with open("result.json", "w", encoding="utf-8") as f:
#     json.dump(parsed_post, f, indent=2, ensure_ascii=False)

# Example run:
if __name__ == "__main__":
    import asyncio


    async def main():
        posts = [parse_post(post) async for post in scrape_user_posts("lorem.ipsum.v0", max_pages=3)]
        print(json.dumps(posts, indent=2, ensure_ascii=False))


    asyncio.run(main())
