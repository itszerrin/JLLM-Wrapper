"""
This file contains the unofficial API class which is used to interact with JAI in a sleazy way."""

from typing import Generator

from . import requests, json, UserAgent, uuid4, logger, HTTPAdapter, Retry

class API():

    """
    This is the API class which is used to interact with the JAI API. It contains the generate function which is used to generate a response from the API.
    """

    def __init__(self, _jwt: str) -> None:
        
        """
        This function is used to initialize the API class.
        """
        
        self.jwt = _jwt

        # remove the "Bearer " prefix from the JWT token
        if self.jwt.startswith("Bearer "):

            self.jwt = self.jwt.removeprefix("Bearer ")

    def generate(
            self, 
            messages, 
            max_tokens: int = 150, 
            repetition_penalty: float = 1.2, 
            min_p: float = 0.1, 
            stream: bool = False, 
            temperature: float = 0.7, 
            stop: list[str] = ["<"]

    ) -> Generator[str, None, None]:

        """
        This function is used to generate a response from the JAI API.
        
        :param messages: The messages to send to the API.
        :type messages: list[dict[str, str]]
        
        :param max_tokens: The maximum number of tokens to generate.
        :type max_tokens: int
        
        :param repetition_penalty: The repetition penalty.
        :type repetition_penalty: float
        
        :param min_p: The minimum probability.
        :type min_p: float
        
        :param stream: Whether to stream the response.
        :type stream: bool
        
        :param temperature: The temperature.
        :type temperature: float
        
        :param stop: The stop sequence.
        :type stop: list
        
        :return: The response.
        :rtype: Generator[str, None, None]
        """

        headers = {
            "Host": "kim.janitorai.com",
            "User-Agent": f"{UserAgent().random}",
            "Accept": "application/json, text/event-stream, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": f"{self.jwt}",
            "Origin": "https://janitorai.com",
            "Connection": "keep-alive",
            "Referer": "https://janitorai.com/",
            "Content-Length": "7764",
            "TE": "Trailers",
            "X-Request-ID": f"{uuid4()}",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"
        }

        data = {
            "max_tokens": max_tokens,
            "messages": messages,
            "repetition_penalty": repetition_penalty,
            "min_p": min_p,
            "stream": stream,
            "temperature": temperature,
            "stop": stop
        }

        # retry the request 3 times if it fails.
        # JAI sometimes does a funny and returns a 403 error for no reason.
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[403])

        with requests.Session() as session:

            session.mount('https://', HTTPAdapter(max_retries=retries))

            #print("API - Using JWT:", self.jwt + "\n") # for debugging purposes

            try:

                response = session.post("https://kim.janitorai.com/generate", headers=headers, json=data, stream=stream)
                response.raise_for_status()

                if stream:

                    for chunk in response.iter_lines():

                        if chunk:

                            try:

                                delta_chunk = json.loads(chunk.decode("utf-8").removeprefix("data: "))
                                yield delta_chunk["choices"][0]["delta"]["content"] # returns a word (token, actually) without all the other stuff

                            except:
                                pass

                else:

                    yield str(response.json()["choices"][0]["message"]["content"])

            except requests.exceptions.HTTPError as e:

                # Handle the HTTPError
                logger.error(f"HTTP Error {e.response.status_code}. Retrying...")
            
    """
    # made this in a hurry
    def upload_bot(
            self,
            description: str = "", 
            example_dialogs: str = "", 
            first_message: str = " ", 
            is_nsfw: bool = False,  
            is_public: bool = True,
            name: str = " ",
            personality: str = " ",
            scenario: str = "",
            showdefinition: bool = False,

    ) -> dict[str, Any]:
        
        ---
        # -- UNFINISHED --

        This function is used to upload a bot to the JAI API.
        
        :param description: The description of the bot.
        :type description: str
            
        :param example_dialogue: The example dialogue of the bot.
        :type example_dialogue: str
        
        :param first_message: The first message of the bot.
        :type first_message: str
        
        :param is_nsfw: Whether the bot is NSFW.
        :type is_nsfw: bool
        
        :param is_public: Whether the bot is public.
        :type is_public: bool
        
        :param name: The name of the bot.
        :type name: str
        
        :param personality: The personality of the bot.
        :type personality: str
        
        :param scenario: The scenario of the bot.
        :type scenario: str
        
        :param showdefinition: Whether to show the definition.
        :type showdefinition: bool
        
        :return: The response.
        :rtype: dict[str, Any]
        ---

        _image_id: str = "" # pre-init this variable
        _tag_ids: list = [], # hard-coded tag ids too lol. (coming soon)

        headers = {
            'Host': 'kim.janitorai.com',
            'User-Agent': f'{UserAgent().random}',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Content-Length': '245',
            'x-app-version': '2024-04-16.6c2e59db',
            'Origin': 'https://janitorai.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Authorization': f'Bearer {self.jwt}', # oh so NOW it needs the "Bearer " prefix. What the f*ck..
            'Connection': 'keep-alive',
            'TE': 'trailers'
        }

        data = {
            "avatar": _image_id,
            "description": description,
            "example_dialogs": example_dialogs,
            "first_message": first_message,
            "is_nsfw": is_nsfw,
            "is_public": is_public,
            "name": name,
            "personality": personality,
            "scenario": scenario,
            "showdefinition": showdefinition,
            "tag_ids": _tag_ids
        }

        # --- first segment, send a request to the 'check' path to create a resource
        response_check = requests.post("https://kim.janitorai.com/characters/check", headers=headers, json={"name": name, "personality": personality})
        response_check.raise_for_status()

        # logging
        logger.info("Bot checked successfully!")

        # --- second segment, upload the file ---
        response_img = requests.post("https://kim.janitorai.com/upload/uploadFile", headers=headers, json={"extension": "webp", "type": "bot"})
        response_img.raise_for_status()

        _url_to_put_image: str = response_img.json()["url"]

        # send a put request
        with open("bot.jpg", "rb") as f:

            __img_headers = {
                'Host': 'pictures.a88a0a0ec0a380338bfd981ac867c85a.r2.cloudflarestorage.com',
                'User-Agent': f'{UserAgent().random}',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'image/webp',
                'Content-Length': '2832',
                'Origin': 'https://janitorai.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'Connection': 'keep-alive'
            }

            response_img_put = requests.put(_url_to_put_image, data=f, headers=__img_headers)
            response_img_put.raise_for_status()

        # logging
        logger.info("Bot image (uploaded) successfully!")

        # parse filename from the response
        _image_id = response_img.json()["filename"]

        # set the avatar to the image id
        data["avatar"] = _image_id

        # --- third segment, send a request to the 'characters' path to create the bot

        response = requests.post("https://kim.janitorai.com/characters", headers=headers, json=data)
        response.raise_for_status()

        logger.info("Bot uploaded successfully!")

        return response.json()
    """
