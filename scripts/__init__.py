"""
Init file for the scripts package.

Sets up the logging configuration, a webdriver, and helper functions that can be used in the main script.
Lastly, exports the necessary modules and functions.
"""

# Standard library imports
from os import remove
import json
import logging
from uuid import uuid4
from time import time as now

# Third-party imports
from secrets import token_urlsafe
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from tempmail import EMail

# Aliased imports
import nodriver as uc

# --------------------------------------------------------------------------- VARIABLES --------------------------------------------------------------------------- #
"""
The purpose of the below code is to provide a set of global variables that can be used in the main script to configure the behavior of the script.
"""

_WEBDRIVER_GLOBAL_HEADLESS: bool = False # whether to run the browser in headless mode. Not recommended for JWT interception
_WEBDRIVER_GLOBAL_MINIMIZE: bool = False # whether to minimize the browser window. Not recommended for JWT interception

_JANITORAI_JWT_EXPIRE_TIME: int = 10000 # the time in seconds after which the JWT token expires

# --------------------------------------------------------------------------- LOGGING --------------------------------------------------------------------------- #
"""
The purpose of the below code is to provide a logging configuration that can be used in the main script to log messages.
"""

# Configure the logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # will be exported

# --------------------------------------------------------------------------- WEBDRIVER --------------------------------------------------------------------------- #
"""
Here we create a webdriver using selenium 
"""

# Create a webdriver
__options: webdriver.ChromeOptions = webdriver.ChromeOptions()
__options.add_argument("--headless")
__options.add_argument("--no-sandbox")
__options.headless = True

__webdriver: webdriver.Chrome = webdriver.Chrome(options=__options) # will be exported

# --------------------------------------------------------------------------- HELPER FUNCTIONS --------------------------------------------------------------------------- #
"""
The purpose of the functions below is to provide a set of helper functions that can be used in the main script to perform various tasks.
"""

# following function is used to get the JWT token from the request
async def is_jwt(request) -> str | None:

    """
    This function is used to extract the JWT token from the request headers.
    
    :param request: The request object.
    :type request: dict
    
    :return: The JWT token.
    :rtype: str | None
    """

    # try to only intercept the profile request since it contains the JWT token
    if request["url"] == "https://kim.janitorai.com/profiles/mine":

        logger.info("Got JWT from profile request.")
        return request["headers"]["Authorization"]
    
    # If the JWT token is not found, return None
    return None

# following function is used to verify the email
def verify_mail(html_string: str) -> None:

    """
    This function is used to verify an email by parsing the HTML content and extracting the confirmation link.
    The confirmation link is then opened in a headless browser window to complete the verification process.
    
    :param html_string: The HTML content of the email.
    :type html_string: str
    
    :return: None
    """

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_string, 'html.parser')

    # Find the confirmation link
    confirmation_link = soup.select_one('.button')['href']

    # Open Selenium window and navigate to the confirmation link
    __webdriver.get("about:blank")  # Open a blank page first to prevent "data:" issue
    __webdriver.get(confirmation_link)

    logger.info("Email verified successfully!")

    # Close the browser window
    __webdriver.quit()

# following function is used to get the message from the email
def get_message(email) -> str:

    """
    This function is used to get the message from the email.
    
    :param email: The email object.
    :type email: EMail
    
    :return: The message body.
    :rtype: str
    """

    msg = email.wait_for_message()
    logging.info("Message received!")

    return msg.body

# function to create a random string using token_urlsafe
def random_string(length: int) -> str:

    """
    This function is used to generate a random string of a specified length.
    
    :param length: The length of the random string.
    :type length: int
    
    :return: The random string.
    :rtype: str
    """

    return token_urlsafe(length)

# new function
def is_jwt_valid(filepath: str):

    """
    This function is used to check if the JWT token is valid by comparing the creation date of the JWT token with the current time.
    
    :param filepath: The path to the JWT token file.
    :type filepath: str
    
    :return: Whether the JWT token is valid.
    :rtype: bool
    """

    # Read the JWT token from the file
    try:

        with open(filepath, "r") as f:
            jwt_creation_date = f.read()

            if int(now()) - int(jwt_creation_date) > _JANITORAI_JWT_EXPIRE_TIME:

                logger.info("JWT token is expired.")
                return False

    except FileNotFoundError:

        logger.error("JWT time file not found.")
        return False
    
    logger.info(f"JWT token is valid. Expires in {_JANITORAI_JWT_EXPIRE_TIME/60} minutes.")
    return True
    
# new function
def get_jwt_from_temp() -> str | None:

    """
    This function is used to get the JWT token from the temporary file. Will automatically point to the TOKEN.temp file.
    
    :param filepath: The path to the JWT token file.
    :type filepath: str
    
    :return: The JWT token.
    :rtype: str | None
    """

    # Read the JWT token from the file
    try:

        with open("TOKEN.temp", "r") as f:
            jwt = f.read()

    except FileNotFoundError:

        logger.error("JWT token file not found.")
        return None

    logger.info("JWT token found.")
    return jwt

# combining both functions above
def get_preexisting_jwt() -> str | None:

    """
    This function is used to get the JWT token from the temporary file and check if it is valid.
    Assumes that the JWT token is stored in a file named TOKEN.temp at root and the timestamp is stored in a file named TIME.temp at root.
    
    :param filepath: The path to the JWT token file.
    :type filepath: str
    
    :return: The JWT token.
    :rtype: str | None
    """

    # Read the JWT token from the file
    try:

        with open("TOKEN.temp", "r") as f:
            jwt = f.read()

    except FileNotFoundError:

        logger.error("JWT token file not found.")
        return None

    # Read the timestamp from the file
    try:

        with open("TIME.temp", "r") as f:
            jwt_creation_date = f.read()
            __now = int(now())

            if (__now - int(jwt_creation_date)) > _JANITORAI_JWT_EXPIRE_TIME:

                logger.info(f"JWT token has expired since {__now - int(jwt_creation_date)} seconds.")
                return None

    except FileNotFoundError:

        logger.error("JWT time file not found.")
        return None

    logger.info(f"JWT token found. Expires in {(_JANITORAI_JWT_EXPIRE_TIME - (int(now()) - int(jwt_creation_date)))/60} minutes.")
    return jwt

# exports
__all__ = [
    "_WEBDRIVER_GLOBAL_HEADLESS",
    "_WEBDRIVER_GLOBAL_MINIMIZE",

    "is_jwt",
    "verify_mail",
    "get_message",
    "random_string",
    "is_jwt_valid",
    "get_jwt_from_temp",
    "get_preexisting_jwt",

    "logger",
    "__webdriver",

    "uc",
    "requests",
    "HTTPAdapter",
    "Retry",
    "json",
    "now"
    "UserAgent",
    "uuid4",
    "EMail",
    "webdriver",
    "remove",
]
