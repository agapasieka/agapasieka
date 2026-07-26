from playwright.sync_api import sync_playwright
from pathlib import Path
import re


CREDLY_URL = "https://www.credly.com/users/agnieszka-pasieka/badges/credly"

README = Path("README.md")

START = "<!--START_SECTION:badges-->"
END = "<!--END_SECTION:badges-->"


def inspect_credly():

    api_responses = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )

        page = browser.new_page(
            viewport={
                "width": 1400,
                "height": 3000
            }
        )

        def handle_response(response):
            url = response.url

            if (
                "api" in url.lower()
                or "badge" in url.lower()
                or "profile" in url.lower()
                or "graphql" in url.lower()
            ):
                api_responses.append(url)
                print("POSSIBLE API:", url)

        page.on("response", handle_response)

        print("Opening Credly...")

        page.goto(
            CREDLY_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("Waiting for JavaScript...")

        page.wait_for_timeout(15000)

        print("Saving debug files...")

        with open(
            "credly-page.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(page.content())

        page.screenshot(
            path="credly-page.png",
            full_page=True
        )

        print(
            "HTML length:",
            len(page.content())
        )

        print("\nVisible page text:")
        print(
            page.locator("body")
            .inner_text()[:2000]
        )

        print("\nAPI candidates:")

        for url in api_responses:
            print(url)

        print(
            "\nTotal possible API calls:",
            len(api_responses)
        )

        browser.close()


def update_readme_placeholder():

    if not README.exists():
        print("README not found")
        return

    text = README.read_text(
        encoding="utf-8"
    )

    # Do not overwrite existing badges yet.
    if START not in text or END not in text:
        print("Badge markers not found")
        return

    replacement = (
        START
        + "\n\n"
        + "Badge scraper diagnostics running..."
        + "\n\n"
        + END
    )

    pattern = (
        re.escape(START)
        + ".*?"
        + re.escape(END)
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

    inspect_credly()

    # Temporarily disabled:
    # update_readme_placeholder()

    print("Finished")
