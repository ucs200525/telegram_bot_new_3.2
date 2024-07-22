from playwright.async_api import async_playwright
import asyncio
import sys
import os
async def main(output_image_path, sunrise_today, sunset_today, sunrise_tmrw, weekday):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        html_file_path = 'file://' + os.path.abspath('./images/index.html')

        # Navigate to your local HTML file
        await page.goto(html_file_path)

        # Optionally, update the table values by simulating user input
        await page.evaluate(f'''() => {{
            document.getElementById('sunriseToday').value = '{sunrise_today}';
            document.getElementById('sunsetToday').value = '{sunset_today}';
            document.getElementById('sunriseTmrw').value = '{sunrise_tmrw}';
            document.getElementById('weekday').value = '{weekday}';
            document.querySelector('button').click();
        }}''')
    

        # Select the table element
        element = await page.query_selector('body > table')
        await page.wait_for_timeout(2000);  

        # Take a screenshot of the table element with higher resolution
        await element.screenshot(path=output_image_path, type='png')

        # Close the browser
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python image2.py <output_image_path> <sunrise_today> <sunset_today> <sunrise_tmrw> <weekday>")
        sys.exit(1)

    output_image_path = sys.argv[1]
    sunrise_today = sys.argv[2]
    sunset_today = sys.argv[3]
    sunrise_tmrw = sys.argv[4]
    weekday = sys.argv[5]

    asyncio.run(main(output_image_path, sunrise_today, sunset_today, sunrise_tmrw, weekday))
