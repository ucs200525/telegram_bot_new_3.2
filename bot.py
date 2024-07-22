import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
import pytz
from opencage.geocoder import OpenCageGeocode
import os
import logging
import subprocess
from flask import Flask, send_from_directory
import platform
import pandas as pd
from openpyxl import load_workbook


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
LOCATION = 0
DATE_LOCATION = 1
CONFIRMATION = 2

# Function to get sunrise and sunset times for a specific date
def get_sun_times_for_date(lat, lng, local_tz, date):
    next_day = (date + timedelta(days=1)).strftime('%Y-%m-%d')
    date_str = date.strftime('%Y-%m-%d')

    url = f'https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&formatted=0&date='

    date_response = requests.get(url + date_str).json()
    next_day_response = requests.get(url + next_day).json()

    sunrise_date_utc = date_response['results']['sunrise']
    sunset_date_utc = date_response['results']['sunset']
    sunrise_next_day_utc = next_day_response['results']['sunrise']

    # Convert to local time
    ist = pytz.timezone(local_tz)
    sunrise_date = pd.to_datetime(sunrise_date_utc).tz_convert(ist)
    sunset_date = pd.to_datetime(sunset_date_utc).tz_convert(ist)
    sunrise_next_day = pd.to_datetime(sunrise_next_day_utc).tz_convert(ist)

    return sunrise_date, sunset_date, sunrise_next_day

# Function to convert specific data to image using Python script
def save_image_with_nodejs_date(output_image_path, sunrise_today, sunset_today, sunrise_tmrw, weekday):
    try:
        py_script = r'./images/bharghav.py'  # Update this path to your Playwright script
        subprocess.run(['python', py_script, output_image_path, sunrise_today, sunset_today, sunrise_tmrw, weekday], check=True)
        logger.info(f"Image successfully saved to {output_image_path}")
    except Exception as e:
        logger.error(f"Error converting data to image: {e}")

# Function to get DrikPanchang screenshot using Node.js script with specific date
def get_drikpanchang_screenshot_date(city, date, output_image_path):
    try:
        py_script = r'./images/test.py'  # Update this path to your Node.js script
        subprocess.run(['python', py_script, city, date, output_image_path], check=True)
        logger.info(f"DrikPanchang screenshot successfully saved to {output_image_path}")
    except Exception as e:
        logger.error(f"Error capturing DrikPanchang screenshot: {e}")

# Flask application
app = Flask(__name__)

# Endpoint to start the bot
@app.route('/start-bot', methods=['GET'])
def start_bot():
    main()
    return "Bot started", 200

# Command handler to start the conversation for /gt
@app.route('/')
def index():
    return "Hello, World!"

# Command handler to serve favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Command handler to start the conversation for /dgt
@app.route('/dgt')
def dgt():
    return "This is the route for /dgt"

# Command handler to handle unknown routes
@app.errorhandler(404)
def page_not_found(e):
    return "404 Not Found", 404

# Command handler to cancel ongoing operations
@app.route('/cancel')
def cancel():
    return "Operation cancelled."

# Command handler for /start
async def start_command_handler(update: Update, context: CallbackContext):
    start_message = (
        "Welcome to the Panchangam Bot!\n"
        "Here are the available commands:\n\n"
        "/gt - Get a screenshot of Bhargava Panchangam and Drik Panchangam for your location. Just send your location (e.g., Vijayawada).\n"
        "/dgt - Get a screenshot of Bhargava Panchangam and Drik Panchangam for a specific date and location. Send the date and location separated by a comma (e.g., 26/06/2024, Vijayawada).\n"
        "/cancel - Cancel the current operation."
    )
    await update.message.reply_text(start_message)

async def help_command_handler(update: Update, context: CallbackContext):
    await update.message.reply_text("This is the help message.")

async def main_handler(update: Update, context: CallbackContext):
    await update.message.reply_text("You sent a text message.")

# Command handler for handling unknown commands
async def unknown_command_handler(update: Update, context: CallbackContext):
    await update.message.reply_text("Sorry, I didn't understand that command. Please use one of the available commands:\n"
                                      "/gt - Get a screenshot of Bhargava Panchangam and Drik Panchangam for your location. Just send your location (e.g., Vijayawada).\n"
                                      "/dgt - Get a screenshot of Bhargava Panchangam and Drik Panchangam for a specific date and location. Send the date and location separated by a comma (e.g., 26/06/2024, Vijayawada).\n"
                                      "/cancel - Cancel the current operation.")

# Command handler to cancel ongoing operations
async def cancel_command_handler(update: Update, context: CallbackContext):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END  # End any active conversation

# Command handler to start the conversation for /gt
async def send_table_start(update: Update, context: CallbackContext):
    await update.message.reply_text("Please enter your location (e.g., Vijayawada) or type /cancel to abort.")
    return LOCATION

# Command handler to start the conversation for /dgt
async def send_date_location_start(update: Update, context: CallbackContext):
    await update.message.reply_text(f"Please enter the date (dd/mm/yyyy) and location separated by a comma (e.g., {datetime.now().strftime('%d/%m/%Y')}, Vijayawada) or type /cancel to abort.")
    return DATE_LOCATION

## Function to handle location input and send the table with images
async def receive_location(update: Update, context: CallbackContext):
    location = update.message.text
    user_id = update.message.from_user.id
    username = update.effective_user.username
    logger.info(f'User {user_id}, {username} sent location: {location}')
    await update.message.reply_text("Your task is in progress...")

    # Use OpenCage Geocoder to get coordinates
    geocoder = OpenCageGeocode(context.bot_data['opencage_api_key'])
    result = geocoder.geocode(location)

    if result and len(result):
        latitude = result[0]['geometry']['lat']
        longitude = result[0]['geometry']['lng']
        logger.info(f'Coordinates for {location}: {latitude}, {longitude}')

        local_tz = 'Asia/Kolkata'  # Assuming Indian Standard Time (IST)

        # Get sun times for today
        today = datetime.now()
        day_of_week = today.strftime('%A').upper()  # Get day of the week

        sunrise_today, sunset_today, sunrise_tomorrow = get_sun_times_for_date(latitude, longitude, local_tz, today)

        # Save image with today's data
        save_image_path = context.bot_data['image_save_path']
        save_image_with_nodejs_date(save_image_path, sunrise_today.strftime('%H:%M:%S'), sunset_today.strftime('%H:%M:%S'), sunrise_tomorrow.strftime('%H:%M:%S'), day_of_week)

        # Get DrikPanchang screenshot
        drikpanchang_image_path = context.bot_data['drikpanchang_image_path']
        city = location  # Use the provided location
        date = today.strftime('%d/%m/%Y')  # Current date in dd/mm/yyyy format
        get_drikpanchang_screenshot_date(city, date, drikpanchang_image_path)

        # Notify user of the day of the week
        await update.message.reply_text(f"Day of the week for today ({today.strftime('%d/%m/%Y')}) is {day_of_week}")

        # Send both images
        try:
            with open(save_image_path, 'rb') as f:
                await update.message.reply_photo(f, caption="Bhargava Panchangam")
            with open(drikpanchang_image_path, 'rb') as f:
                await update.message.reply_photo(f, caption="Drik Panchangam")
        except Exception as e:
            logger.error(f"Error sending images: {e}")
            await update.message.reply_text("An error occurred while sending the images. Please try again later.")

    else:
        logger.warning(f'Could not find coordinates for location: {location}')
        await update.message.reply_text("Sorry, I couldn't find coordinates for that location. Please try again.")
        return LOCATION

    return ConversationHandler.END

# Function to handle date and location input
async def receive_date_location(update: Update, context: CallbackContext):
    date_location = update.message.text.split(',')
    if len(date_location) != 2:
        await update.message.reply_text(f"Invalid input format. Please enter the date (dd/mm/yyyy) and location separated by a comma (e.g., {datetime.now().strftime('%d/%m/%Y')}, Vijayawada).")
        return DATE_LOCATION

    date_str, location = date_location
    try:
        date = datetime.strptime(date_str.strip(), '%d/%m/%Y')
    except ValueError:
        await update.message.reply_text("Invalid date format. Please enter the date in dd/mm/yyyy format.")
        return DATE_LOCATION

    user_id = update.message.from_user.id
    username = update.effective_user.username
    logger.info(f'User {user_id}, {username} sent date: {date}, location: {location}')
    await update.message.reply_text("Your task is in progress...")

    # Use OpenCage Geocoder to get coordinates
    geocoder = OpenCageGeocode(context.bot_data['opencage_api_key'])
    result = geocoder.geocode(location)

    if result and len(result):
        latitude = result[0]['geometry']['lat']
        longitude = result[0]['geometry']['lng']
        logger.info(f'Coordinates for {location}: {latitude}, {longitude}')

        local_tz = 'Asia/Kolkata'  # Assuming Indian Standard Time (IST)

        # Get sun times for the specific date
        day_of_week = date.strftime('%A').upper()  # Get day of the week

        sunrise_today, sunset_today, sunrise_tomorrow = get_sun_times_for_date(latitude, longitude, local_tz, date)

        # Save image with date's data
        save_image_path = context.bot_data['image_save_path']
        save_image_with_nodejs_date(save_image_path, sunrise_today.strftime('%H:%M:%S'), sunset_today.strftime('%H:%M:%S'), sunrise_tomorrow.strftime('%H:%M:%S'), day_of_week)

        # Get DrikPanchang screenshot
        drikpanchang_image_path = context.bot_data['drikpanchang_image_path']
        city = location  # Use the provided location
        date_str = date.strftime('%d/%m/%Y')  # Specific date in dd/mm/yyyy format
        get_drikpanchang_screenshot_date(city, date_str, drikpanchang_image_path)

        # Notify user of the day of the week
        await update.message.reply_text(f"Day of the week for {date_str} is {day_of_week}")

        # Send both images
        try:
            with open(save_image_path, 'rb') as f:
                await update.message.reply_photo(f, caption="Bhargava Panchangam")
            with open(drikpanchang_image_path, 'rb') as f:
                await update.message.reply_photo(f, caption="Drik Panchangam")
        except Exception as e:
            logger.error(f"Error sending images: {e}")
            await update.message.reply_text("An error occurred while sending the images. Please try again later.")

    else:
        logger.warning(f'Could not find coordinates for location: {location}')
        await update.message.reply_text("Sorry, I couldn't find coordinates for that location. Please try again.")
        return DATE_LOCATION

    return ConversationHandler.END

def main():

    opencage_api_key = '699522e909454a09b82d1c728fc79925'
    image_save_path = r'./images/BPI.png'
    drikpanchang_image_path = r'./images/DPI.png'
    bharghav_image_path = r'./images/BPI.png'
    bot_token  ='7274941037:AAHIWiU5yvfIzo7eJWPu9S5CeJIid6ATEyM'

    # Create the Application instance
    application = Application.builder().token(bot_token).build()

    application.bot_data['opencage_api_key'] = opencage_api_key
    application.bot_data['image_save_path'] = image_save_path
    application.bot_data['bharghav_image_path'] = bharghav_image_path
    application.bot_data['drikpanchang_image_path'] = drikpanchang_image_path

    start_handler = CommandHandler('start', start_command_handler)
    help_handler = CommandHandler('help', help_command_handler)
    unknown_handler = MessageHandler(filters.COMMAND, unknown_command_handler)
    cancel_handler = CommandHandler('cancel', cancel_command_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('gt', send_table_start), CommandHandler('dgt', send_date_location_start)],
        states={
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_location)],
            DATE_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date_location)],
           
        },
        fallbacks=[cancel_handler]
    )

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(conv_handler)
    application.add_handler(cancel_handler)
    application.add_handler(unknown_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
