from playwright.sync_api import sync_playwright
from pathlib import Path
import re


CREDLY_URL = "https://www.credly.com/users/agnieszka-pasieka"

README = Path("README.md")

START = "<!--START_SECTION:badges-->"
END = "<!--END_SECTION:badges-->"


def extract_badges():

    badges = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )

        page = browser.new_page(
            viewport={"width": 1400, "height": 2000}
        )

        print("Opening Credly...")
        page.goto(
            CREDLY_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(10000)

        print("Scanning images...")

        images = page.locator("img")

        for i in range(images.count()):
            img = images.nth(i)

            src = img.get_attribute("src")
            alt = img.get_attribute("alt")

            if not src:
                continue

            if "credly" in src.lower() or "badge" in src.lower():

                parent = img.locator("xpath=..")

                link = parent.get_attribute("href")

                badges.append({
                    "name": alt or "Certification",
                    "image": src,
                    "url": link or CREDLY_URL
                })

        browser.close()

    # remove duplicates
    unique = {}

    for badge in badges:
        unique[badge["image"]] = badge

    return list(unique.values())


def build_html(badges):

    if not badges:
        return "<p>No badges found.</p>"

    rows = []

    rows.append(
        '<table><tr>'
    )

    for index, badge in enumerate(badges):

        if index > 0 and index % 3 == 0:
            rows.append("</tr><tr>")

        rows.append(f"""
<td align="center" width="33%">

<a href="{badge['url']}">
<img src="{badge['image']}" width="120"><br>
<b>{badge['name']}</b>
</a>

</td>
""")

    rows.append("</tr></table>")

    return "\n".join(rows)


def update_readme(html):

    text = README.read_text()

    pattern = (
        re.escape(START)
        + ".*?"
        + re.escape(END)
    )

    replacement = (
        START
        + "\n\n"
        + html
        + "\n\n"
        + END
    )

    new_text = re.sub(
        pattern,
        replacement,
        text,
        flags=re.DOTALL
    )

    README.write_text(new_text)


if __name__ == "__main__":

    badges = extract_badges()

    print(f"Found {len(badges)} badges")

    html = build_html(badges)

    update_readme(html)

    print("README updated")
