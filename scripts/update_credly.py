from playwright.sync_api import sync_playwright
from pathlib import Path
import re


CREDLY_URL = "https://www.credly.com/users/agnieszka-pasieka/badges/credly"

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

        print("Saving debug files...")

        with open("credly-page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        
        page.screenshot(
            path="credly-page.png",
            full_page=True
        )
        
        print("Debug files saved")

        # DEBUG
        html = page.content()
        
        with open("credly-page.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        page.screenshot(
            path="credly-page.png",
            full_page=True
        )
        
        print("HTML length:", len(html))

        # scroll to trigger lazy loading
        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(5000)

        print("Looking for badge cards...")

        cards = page.locator("a")

        print(f"Found {cards.count()} possible badge links")

        for i in range(cards.count()):

            card = cards.nth(i)

            href = card.get_attribute("href")

            if not href:
                continue
                
            if "badge" not in href.lower():
                continue
                
            img = card.locator("img").first

            if img.count() == 0:
                continue

            image = img.get_attribute("src")

            title = (
                img.get_attribute("alt")
                or card.inner_text()
                or "Certification"
            )

            badges.append({
                "name": title.strip(),
                "image": image,
                "url": (
                    href
                    if href.startswith("http")
                    else "https://www.credly.com" + href
                )
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
