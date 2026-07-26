import requests
from pathlib import Path
import re
import html


CREDLY_USER_ID = "f8a71d67-993f-4767-83f8-5ed1861371a7"

API_URL = (
    f"https://www.credly.com/api/v1/users/"
    f"{CREDLY_USER_ID}/external_badges/open_badges/public"
    "?page=1&page_size=48"
)

README = Path("README.md")

START = "<!--START_SECTION:badges-->"
END = "<!--END_SECTION:badges-->"


def get_badges():

    print("Fetching Credly badges...")

    response = requests.get(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    badges = []

    for badge in data.get("data", []):

        badge_info = badge.get("badge", badge)

        name = (
            badge_info.get("name")
            or badge.get("name")
            or "Certification"
        )

        image = (
            badge_info.get("image_url")
            or badge.get("image_url")
        )

        url = (
            badge_info.get("url")
            or badge.get("url")
            or ""
        )

        issuer = (
            badge_info.get("issuer", {})
            .get("name", "")
        )

        badges.append({
            "name": name,
            "issuer": issuer,
            "image": image,
            "url": url
        })

    print(f"Found {len(badges)} badges")

    return badges


def create_badge_grid(badges):

    cards = []

    for badge in badges:

        cards.append(f"""
<div style="
display:inline-block;
width:30%;
min-width:220px;
margin:10px;
padding:15px;
text-align:center;
border-radius:10px;
">

<a href="{badge['url']}">

<img 
src="{badge['image']}"
width="120"
alt="{html.escape(badge['name'])}"
>

<br>

<b>{html.escape(badge['name'])}</b>

<br>

<small>
{html.escape(badge['issuer'])}
</small>

</a>

</div>
""")

    return "\n".join(cards)


def update_readme(content):

    text = README.read_text(
        encoding="utf-8"
    )

    pattern = (
        re.escape(START)
        + ".*?"
        + re.escape(END)
    )

    replacement = (
        START
        + "\n\n"
        + content
        + "\n\n"
        + END
    )

    new_text = re.sub(
        pattern,
        replacement,
        text,
        flags=re.DOTALL
    )

    README.write_text(
        new_text,
        encoding="utf-8"
    )


if __name__ == "__main__":

    badges = get_badges()

    if badges:
        html_grid = create_badge_grid(badges)
        update_readme(html_grid)
        print("README updated")

    else:
        print("No badges returned - README unchanged")
