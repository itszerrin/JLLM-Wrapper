"""
This file contains the unofficial API class which is used to interact with JAI in a sleazy way."""

from typing import Generator, Dict, Any
from random import randint

from . import requests, UserAgent, uuid4, logger, HTTPAdapter, Retry

class API():

    """
    This is the API class which is used to interact with the JAI API. It contains the generate function which is used to generate a response from the API.
    """

    def __init__(self, _jwt: str, _character: str) -> None:
        
        """
        This function is used to initialize the API class.
        """
        
        self.jwt = _jwt
        self.__cf_bm: str = "7sLHc0cfULW9qT.oYrB44bAsmN1kBkwjtzWZhXCwWfU-1719496065-1.0.1.1-8RTEqETSd1h_j2JLhoypCh3eS9fbRY7qqlOEKLOW4DY_EtkgqcQgkcx1wdOFK06gvPiFHjMEkFcgE2wprFVNDA"

        self.character_id = _character.split("_")[0]
        self.character_name = _character.split("_")[1]

        # remove the "Bearer " prefix from the JWT token
        if self.jwt.startswith("Bearer "):

            self.jwt = self.jwt.removeprefix("Bearer ")

    def upload_persona(self, name: str, appearance: str) -> Dict[str, Any]:

        url: str = "https://janitorai.com/hampter/personas"

        headers = {
            'Host': 'janitorai.com',
            'User-Agent': f'{UserAgent().random}',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'Content-Length': f'{randint(50, 55)}',
            'Referer': f'https://janitorai.com/my_personas',
            'x-app-version': '2024-06-27.4c3f76bc',
            'Origin': 'https://janitorai.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Authorization': f'Bearer {self.jwt}',
            'Connection': 'keep-alive',
            'Cookie': f'__cf_bm={self.__cf_bm}',
            'TE': 'trailers'
        }

        data = {
            "name": name,
            "appearance": appearance,
            "avatar": '',
            "order": 2
        }

        response = requests.post(url, headers=headers, json=data, cookies={"__cf_bm": self.__cf_bm})
        response.raise_for_status()

        return response.json()        

    def create_chat(self) -> Dict[str, Any]:

        """
        This function is used to create a chat.

        :param character_id: The character ID.
        :type character_id: str

        :param character_name: The character name.
        :type character_name: str

        :return: The response.
        :rtype: Dict[str, Any]
        """

        url: str = "https://janitorai.com/hampter/chats"

        headers = {
            'Host': 'janitorai.com',
            'User-Agent': f'{UserAgent().random}',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'Content-Length': f'{randint(50, 55)}',
            'Referer': f'https://janitorai.com/characters/{self.character_id}_{self.character_name}',
            'x-app-version': '2024-06-27.4c3f76bc',
            'Origin': 'https://janitorai.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Authorization': f'Bearer {self.jwt}',
            'Connection': 'keep-alive',
            'Cookie': f'__cf_bm={self.__cf_bm}',
            'TE': 'trailers'
        }

        data = {
            "character_id": self.character_id,
        }

        response = requests.post(url, headers=headers, json=data, cookies={"__cf_bm": self.__cf_bm})
        response.raise_for_status()

        return response.json()


    def generate(
            self, 
            messages, 
            max_tokens: int = 150, 
            repetition_penalty: float = 1.2, 
            stream: bool = False, 
            temperature: float = 0.7, 
            system_message: str = "You're a helpful AI assistant."

    ) -> Generator[str, None, None]:

        """
        This function is used to generate a response from the JAI API.
        
        :param messages: The messages to send to the API.
        :type messages: list[dict[str, str]]
        
        :param max_tokens: The maximum number of tokens to generate.
        :type max_tokens: int
        
        :param repetition_penalty: The repetition penalty.
        :type repetition_penalty: float
        
        :param stream: Whether to stream the response.
        :type stream: bool
        
        :param temperature: The temperature.
        :type temperature: float
        
        :param system_message: A system message that heavily influences the response.
        :type system_message: str
        
        :return: The response.
        :rtype: Generator[str, None, None]
        """

        # get the new message format
        new_messages = []

        for message in messages:

            new_messages.append({
                "chat_id": randint(10000000, 99999999),
                "id": randint(10000000, 99999999),
                "is_main": True,
                "is_bot": message["role"] == "assistant" or message["role"] == "system",
                "message": message["content"],
            })

        # create a fake new chat
        chat = self.create_chat()
        persona = self.upload_persona(f"jai-llm{randint(00000, 99999)}", " ")


        headers = {
            "Host": "janitorai.com",
            "User-Agent": f"{UserAgent().random}",
            "Accept": "application/json, text/event-stream, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": f"Bearer {self.jwt}",
            "Origin": "https://janitorai.com",
            "Connection": "keep-alive",
            "Cookie": f"__cf_bm={self.__cf_bm}",
            "Referer": "https://janitorai.com/",
            "Content-Length": f"{randint(6000, 7500)}",
            "TE": "Trailers",
            "X-Request-ID": f"{uuid4()}",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site"
        }

        data = {
            "chat": {
                "character_id": chat["character_id"],
                "id": chat["id"],
                "summary": '',
                "user_id": chat["user_id"],
            },
            "profile": {
                "id": chat["user_id"],
                "name": ' ',
                "user_appearance": ' ',
                "user_name": ' ',
            },
            "userConfig": {
                "api": "janitor",
                "api_url": "https://janitorai.com/generateAlpha",
                "chat_custom_background_blur": 0,
                "chat_custom_background_image": '',
                "chat_custom_background_opacity": 10,
                "chat_custom_foreground_color": "#ffffff",
                "debug_mode": False,
                "generation_settings": {
                    "context_length": 16384,
                    "max_new_token": max_tokens,
                    "repetition_penalty": repetition_penalty,
                    "temperature": temperature,
                },
                "immersive_mode": False,
                "jailbreak_prompt": f"{system_message}",
                "llm_prompt": f"{system_message}",
                "model": "jai-security-is-trash",
                "open_ai_mode": "proxy",
                "open_ai_reverse_proxy": "http://127.0.0.1:5000",
                "openAIKey": None,
                "reverseProxyKey": 'get-cucked',
                "show_clouds": False,
                "show_swords": False,
                "text_streaming": stream,
                "use_pygmalion_format": True,
            },
            "chatMessages": new_messages,
            "forcedPromptGenerationCacheRefetch": {
                "character": False,
                "chat": False,
                "profile": False
            },
            "generateMode": "NEW",
            "personas": [{'appearance': persona["appearance"], 'id': persona["id"], 'name': persona["name"]}],

        }

        # retry the request 3 times if it fails.
        # JAI sometimes does a funny and returns a 403 error for no reason.
        retries = 3
        for attempt in range(retries):
            with requests.Session() as session:
                session.mount('https://', HTTPAdapter(max_retries=Retry(
                    total=retries,
                    status_forcelist=[403]
                )))

                try:
                    response = session.post("https://janitorai.com/generateAlpha", headers=headers, json=data, stream=stream, cookies={"__cf_bm": self.__cf_bm})
                    response.raise_for_status()

                    if stream:
                        for chunk in response.iter_lines():
                            if chunk:
                                yield chunk

                except requests.exceptions.HTTPError as e:
                    logger.error(f"HTTP Error {e.response.status_code}. Retrying {attempt + 1}/{retries}...")
                    if attempt == retries - 1:

                        print(e.response.text)
                        raise e  # Re-raise the exception if we've exhausted all retries
