from playwright.async_api import async_playwright
import asyncio
import sys

async def main(city, date, output_image_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to the website
        await page.goto('https://www.drikpanchang.com/muhurat/panchaka-rahita-muhurat.html', wait_until='networkidle')

        # Clear the existing city and date values
        await page.evaluate('''() => {
            document.getElementById('dp-direct-city-search').value = '';
            document.getElementById('dp-date-picker').value = '';
        }''')

        # Input the new city and date values
        await page.fill('#dp-direct-city-search', city)
        await page.fill('#dp-date-picker', date)

        # Wait for the date picker to become visible and then click the "Done" button
        await page.wait_for_selector('button.ui-datepicker-close.ui-state-default.ui-priority-primary.ui-corner-all', timeout=5000)
        await page.click('button.ui-datepicker-close.ui-state-default.ui-priority-primary.ui-corner-all')

        # Screenshot the specified element
        element = await page.query_selector('.dpMuhurtaCard.dpFlexEqual')
        await element.screenshot(path=output_image_path)

        # Close browser
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python playwright_script.py <city> <date> <output_image_path>")
        sys.exit(1)

    city = sys.argv[1]
    date = sys.argv[2]
    output_image_path = sys.argv[3]

    asyncio.run(main(city, date, output_image_path))
