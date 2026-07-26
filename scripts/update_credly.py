import requests
from pathlib import Path
import re
import html


CREDLY_USER_ID = "f8a71d67-993f-4767-83f8-5ed1861371a7"

API_URL = (
    f"https://www.credly.com/users/"
    f"{CREDLY_USER_ID}/badges.json"
    "?api=api&page=1&page_size=48"
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

        template = badge.get("badge_template", {})

        name = template.get(
            "name",
            "Certification"
        )

        image = template.get(
            "image_url",
            badge.get("image_url", "")
        )

        url = (
            "https://www.credly.com/badges/"
            + badge["id"]
        )

        issuer = ""

        try:
            issuer = (
                badge["issuer"]
                ["entities"][0]
                ["entity"]
                ["name"]
            )
        except Exception:
            pass

        badges.append({
            "name": name,
            "issuer": issuer,
            "image": image,
            "url": url
        })

        print(
            "BADGE:",
            name,
            "|",
            image
        )

    print(
        f"Found {len(badges)} badges"
    )

    return badges


def create_badge_grid(badges):

    cards = []

    for badge in badges:

        image = badge.get("image") or badge.get("image_url")
        name = badge.get("name", "Certification")
        issuer = badge.get("issuer", "")
        url = badge.get("url", "#")

        cards.append(f"""
<div style="
display:inline-block;
vertical-align:top;
width:30%;
min-width:220px;
margin:10px;
padding:15px;
text-align:center;
">

<a href="{url}">

<img 
src="{image}"
width="120"
height="120"
alt="{name}"
>

<br>

<strong>{name}</strong>

<br>

<small>{issuer}</small>

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
