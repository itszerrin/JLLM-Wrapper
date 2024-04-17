"""
This script is used to register the user automatically by using the email address and password generated by the script.
"""

from . import uc, logger, _WEBDRIVER_GLOBAL_HEADLESS, _WEBDRIVER_GLOBAL_MINIMIZE

async def register(email: str, password: str) -> None:

    """
    This function is used to register the user automatically by using the email address and password generated by the script.
    
    :param email: The email address.
    :type email: str
    
    :param password: The password.
    :type password: str
    """

    # create a browser instance which is headless
    br = await uc.start(headless=_WEBDRIVER_GLOBAL_HEADLESS, lang="en-US")

    # check if the browser should be minimized
    if _WEBDRIVER_GLOBAL_MINIMIZE:
        
        # minimize the browser window
        await br.main_tab.minimize()
        
        # add a lil' warning coz it's true nr.2
        logger.warning("Minimized the browser window. High chance of failure to intercept the JWT.")

    # go to the registration page
    await br.get("https://janitorai.com/register")

    # fill the email and password fields
    email_field = await br.main_tab.select("input[id='email']")
    await email_field.send_keys(f"{email}")

    # fill the password field
    password_field = await br.main_tab.select("input[id='password']")
    await password_field.send_keys(password)

    # wait for 3 seconds (cloudflare protection)
    await br.wait(3)

    # click the submit button
    submit_button = await br.main_tab.select("button[type='submit']")
    await submit_button.click()
    await br.wait(1)

    logger.info("User registered successfully!")
    
    # stop the browser
    await br.main_tab.close()
    br.stop()

# export the function
__all__ = ["register"]
