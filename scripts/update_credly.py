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

    rows = []

    for badge in badges:

        rows.append(
            f"""
<td align="center" width="200">

<a href="{badge['url']}">

<img src="{badge['image']}" width="120" height="120">

<br>

<b>{badge['name']}</b>

<br>

<sub>{badge['issuer']}</sub>

</a>

</td>
"""
        )

    # 4 badges per row
    table = ["<table>", "<tr>"]

    for i, card in enumerate(rows, start=1):

        table.append(card)

        if i % 4 == 0:
            table.append("</tr><tr>")

    table.extend([
        "</tr>",
        "</table>"
    ])

    return "\n".join(table)


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
