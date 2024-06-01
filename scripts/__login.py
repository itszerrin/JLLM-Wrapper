"""
Full login script. This script is used to login the user automatically by using the email address and password provided by the user. it then returns a JWT.
"""

from . import uc, logger, makefile, file_exists, _WEBDRIVER_GLOBAL_HEADLESS, _WEBDRIVER_GLOBAL_MINIMIZE
from .__handlers import send_handler

async def login(email: str, password: str) -> str:
    
    """
    This function is used to login the user automatically by using the email address and password provided by the user. it then returns a JWT.

    :param email: The email address.
    :type email: str

    :param password: The password.
    :type password: str

    :return: The JWT.
    :rtype: str
    """

    # create a browser instance which is headless
    br = await uc.start(headless=_WEBDRIVER_GLOBAL_HEADLESS, lang="en-US")

    # add handler to the browser to intercept the JWT token
    br.main_tab.add_handler(uc.cdp.network.RequestWillBeSent, send_handler)

    # check if the browser should be minimized
    if _WEBDRIVER_GLOBAL_MINIMIZE:
        
        # minimize the browser window
        await br.main_tab.minimize()

        # add a lil' warning coz it's true
        logger.warning("Minimized the browser window. High chance of failure to intercept the JWT.")

    # logging
    logger.info("Starting log-in process...")

    # go to the login page
    await br.get("about:blank")
    await br.get("https://janitorai.com/login")

    # logging
    logger.info("On the login page.")

    # fill the email and password fields
    email_field = await br.main_tab.select("input[id='email']")
    await email_field.send_keys(f"{email}")

    # logging
    logger.info("Email entered.")

    # fill the password field
    password_field = await br.main_tab.select("input[id='password']")
    await password_field.send_keys(password)

    # logging
    logger.info("Password entered.")

    # wait for 3 seconds (cloudflare protection).
    await br.wait(3)

    # click the submit button
    submit_button = await br.main_tab.select("button[type='submit']")
    await submit_button.click()

    await br.wait(1) # 1 second(s) is important because the request interceptor needs enough time to catch the right request

    # logging
    logger.info("User logged in successfully!")

    # get the JWT by reading the TOKEN.temp file's content
    try:

        # check if file exists
        if not file_exists("TOKEN.temp"):
            makefile("TOKEN.temp")


        with open("TOKEN.temp", "r") as f:
            _jwt: str = f.read()

        

    except FileNotFoundError as e:
        logger.error("Could not intercept the JWT token. Please try again." + str(e))

        # close main tab and stop the browser
        await br.main_tab.close()
        br.stop()

        quit()

    # delete the file
    await br.wait(0.1) # wait for 0.1 seconds to prevent have enough time to close the file
    #remove("TOKEN.temp")

    # stop the browser
    await br.main_tab.close()
    br.stop()

    return _jwt
