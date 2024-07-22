import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import sys

async def capture_screenshots(city, date):
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
        await page.wait_for_selector('button.ui-datepicker-close.ui-state-default.ui-priority-primary.ui-corner-all')
        await page.click('button.ui-datepicker-close.ui-state-default.ui-priority-primary.ui-corner-all')

        # Capture the <h3> element
        h3_element = await page.query_selector('body > div.dpPageWrapper > div.dpInnerWrapper > div.dpMuhurtaTable.dpFlexWrap.dpSingleColumnTable > h3')
        await h3_element.screenshot(path='./images/HDPI.png')

        # Capture the table element
        table_element = await page.query_selector('body > div.dpPageWrapper > div.dpInnerWrapper > div.dpMuhurtaTable.dpFlexWrap.dpSingleColumnTable > div')
        await table_element.screenshot(path='./images/MDPI.png')

        await browser.close()

def combine_images(output_image_path):
    header = Image.open('./images/HDPI.png')
    table = Image.open('./images/MDPI.png')

    # Get the sizes of the images
    header_width, header_height = header.size
    table_width, table_height = table.size

    # Define offsets for positioning the header image
    header_offset_x = -10
    header_offset_y = -14

    # Determine the width and height of the combined image
    combined_width = max(table_width, header_width + header_offset_x)
    combined_height = header_height + table_height

    # Create a new image with the combined dimensions
    combined_image = Image.new('RGB', (combined_width, combined_height + 5), (255, 255, 255))

    # Paste the header image (above the main image)
    combined_image.paste(header, (header_offset_x, 0))

    # Paste the table image (below the header image)
    combined_image.paste(table, (0, header_height + header_offset_y))

    # Save the combined image
    combined_image.save(output_image_path)
    print('The combined screenshot has been saved as DPI.png')

async def main(city, date,output_image_path):
    await capture_screenshots(city, date)
    combine_images(output_image_path)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <city> <date>")
        sys.exit(1)

    city = sys.argv[1]
    date = sys.argv[2]
    output_image_path = sys.argv[3]

    asyncio.run(main(city, date,output_image_path))
