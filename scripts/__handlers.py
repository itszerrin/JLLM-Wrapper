"""
This file is used to handle the events.
"""

from . import uc, logger, now

def send_handler(event: uc.cdp.network.RequestWillBeSent) -> None:

    """
    This function is used to extract the JWT token from the request headers.
    The JWT token is then written to a temporary file (TOKEN.temp). You need to delete the file after reading the JWT token yourself.
    
    :param event: The event object.
    :type event: uc.cdp.network.RequestWillBeSent
    
    :param _jwt: The JWT token.
    :type _jwt: str
    
    :return: The modified JWT.
    :rtype: str
    """

    r = event.request

    if r.url == "https://janitorai.com/hampter/profiles/mine":

        logger.info("Got a request to the profiles endpoint.")
        
        if r.headers.get('Authorization') is not None:

            logger.info("Got JWT from the request! (Could be duplicate. Ignore.)")
            
            # open a TOKEN.temp file and write the JWT token to it
            with open("TOKEN.temp", "w") as f:
        
                logger.info("Created a temporary file to store the JWT. The file is named TOKEN.temp.")
                f.write(r.headers.get('Authorization'))
                f.flush()

            with open("TIME.temp", "w") as f:

                f.write(str(int(now())))
                logger.info("Created a temporary file to store the timestamp. The file is named TIME.temp.")
                f.flush()
