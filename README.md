# JLLM Wrapper for Python

## Table of Contents
- [Installation](#installation)
- [Introduction](#introduction)
    - [Why I did this](#why-i-did-this)
    - [Brief description of this repository](#brief-description-of-this-repository)
- [Getting your JWT](#getting-your-jwt)
    - [Using an existing account](#using-an-existing-account)
    - [Registering with a burner account](#registering-with-a-burner-account)
- [Chatting with the JLLM](#chatting-with-the-jllm)
- [Badges](#badges)

## Installation

1. Clone this repository
```bash
git clone https://github.com/Recentaly/JLLM-Wrapper.git
```

2. Install requirements
```bash
pip install -r requirements.txt
```

<strong>Side-note: You need to have Google Chrome installed alongside Selenium!</strong>

3. All finished! Now create a python file at the root of the directory to get started.

## Introduction

This is an unofficial API repository that allows you to interact with the JLLM through your own code. It includes many helper functions, including functions for registering accounts, logging in and chatting with the JLLM.

### Why I did this

This was a rather challenging project for me and I had fun developing this. I had reversed JanitorAI before but now they added CloudFlare protection. I was about to give up but didn't quit and developed this as a follow-up.

## Brief description of this repository

This repository includes:

- A registering function to easily register
- Comes with `python-tempmail` so you can create temporary mails for registration.
- On top of that, this project includes functions to verify your `python-tempmail` account on JanitorAI's site.
- Allows you to log in and retrieve your JWT
- With the JWT, you can chat with the JLLM (Janitor LLM) for free.

## Getting your JWT

You require the `JWT` to use the JLLM. Luckily, it's pretty simple. In the following, I will describe step-by-step instructions on creating a Python script to retrieve your JWT from JanitorAI. Here's a curt explanation on how I pulled this off:

First of all, I couldn't use Selenium anymore. This is because JAI added Cloudflare. And this made stuff **so** much more complicated. `undetected-chromedriver` also kept getting caught when trying to log in or register. So I resorted to `nodriver`-A hidden gem I hadn't found yet.

... However... Logging in worked perfectly fine now. Expect for the fact that I couldn't retrieve the JWT from localstorage like I'd normally do because `nodriver` doesn't support that feature. Instead, I had to use a brain-meltingly complicated alternative.

When you log in, my Request middleman (aka the network handler) listens carefully for any on-going requests to `https://kim.janitorai.com/profiles/mine` Because when you enter the home page, where you'll automatically be redirected to after logging in, it sends a request to that exact URL (to of-course fetch your profile). The handler middleman then can snoop inside that request and extract the Authorization header.

That header is then written to a temporary file (Because using `return` isn't possible) and the log-in script reads that value before deleting the temporary file again. This was a headache to figure out, I'll admit.

### Using an existing account

You require the `JWT` to use the JLLM. Luckily, it's pretty simple. In the following, I will describe step-by-step instructions on creating a Python script to retrieve your JWT from JanitorAI.

1. Import all neccessary modules
```py
from scripts.__login import login
from scripts import uc 
```

2. create an asynchronous main function in your code (We need it to be asynchronous for `nodriver` to work.)
```py
# after the imports, create this function:
async def main():
    ...
```

3. Using the `login` function in your `main` function to retrieve your JWT.
```py
async def main():

    jwt = await login(
        email="your_email_here@whatever.com",
        password="your_password_here"
    )
```

4. Running your function

Since we're using `nodriver`, we need to use its pre-made loop and run it until completion like this:

```py
# start the code
if __name__ == "__main__":

    uc.loop().run_until_complete(main())
```

All done now! Here's the full example code:

```py
"""
A simple example of how to use the API.
"""

from scripts.__login import login
from scripts import uc

async def main():

    jwt = await login(
        email="xxxxxxxxx@xxxxx.xxx",
        password="xxxxxxxx"
    )
    
# start the code
if __name__ == "__main__":

    uc.loop().run_until_complete(main())
```

### Registering with a burner account

If you don't want to use a pre-exisiting account, you can simply register a burner account for each run. However, this process of registering takes some additional time and it's always faster to use pre-exisiting accounts.

1. Importing neccessary modules
This time, we need some more modules:

```py
from scripts.__login import login
from scripts import uc, logger, verify_mail, get_message, random_string, EMail
from scripts.__register import register
```

2. Creating your `main` and random credentials (and logging)
```py
# imports would be here
async def main():

    email = EMail() # instance of tempmail-python
    password = random_string(8)

    # --- additional logging --- #
    logger.info(f"Email address: {email.address}")
    logger.info(f"Password: {password}")
```

3. Registering your account
To register your account now, all you need to do is call the `register` function in an asynchronous context.

```py
...
# comment: Use email.address for a string representation of the full E-Mail
# instead of the E-Mail class object
await register(email.address, password) # no return.
```

4. Getting the confirmation E-Mail by JanitorAI and verifying it.
`tempmail-python` has in-built functions to automatically retrieve any received E-Mails which is super helpful. On top of that, we'll be using a headless Selenium webdriver to access the verification mail and verify.

(Side-note: If you'd like the Selenium driver not to be headless, you can simply change that in the `__init__.py` by commenting out line 51 (`__options.add_argument("--headless")`))

Yes, you are required to verify your mail. Only after verification, you're allowed JLLM access for free.

```py
message = get_message(email)
logger.info("Got a message.")

verify_mail(message)
logger.info("Mail verified.")
```

5. Logging in and fetching your JWT
You can now simply log in again like we did above.

Full code:

```py
from scripts.__login import login
from scripts import uc, logger, verify_mail, get_message, random_string, EMail
from scripts.__register import register

async def main():

    # Use code below to register and login using fake email and password

    email = EMail()
    password = random_string(8)

    logger.info(f"Email address: {email.address}")
    logger.info(f"Password: {password}")

    await register(email.address, password)

    message = get_message(email)
    logger.info("Got a message.")

    verify_mail(message)
    logger.info("Mail verified.")

    jwt = await login(
        email="whatever@idontreally.gaf",
        password="xxxxxxxxxxx"
    )

# start the code
if __name__ == "__main__":

    uc.loop().run_until_complete(main())
```

## Chatting with the JLLM

Warning. Following section assumes you already have your JWT via the code above.

1. Importing the API module
```py
from scripts.API import API
```

2. Initializing the API class
```
"""
Your JWT is needed upon initializing the API class. 
You could also pass an empty string but you must update the value
with an actually valid JWT before sending your request
"""

api = API(jwt) # replace jwt with the actual variable for you that holds your JWT value.
```

3. Preparing your parameters:

The `generate` function, responsible for chatting with the JLLM, takes following parameters:

- `messages` | `list[dict[str, str]]`: A list of messages in OpenAI's format to pass to the LLM.
Example:
```json
[
    {
        "role": "system",
        "content": "You're an AI assistant!"
    },
    {
        "role": "assistant",
        "content": "Hello! How can I assist you today?"
    },
    {
        "role": "user",
        "content": "What's 9+10?"
    }
]
```

- `max_tokens` | `int`: This number represents the number of tokens the AI may generate. Refer to the [OpenAI official tokenizer website](https://platform.openai.com/tokenizer) to experiment with tokens as they differ from words. Defaults to `150` tokens.

- `repetition_penalty` | `depracated, float`: As this isn't passed to the JLLM on the official JAI website, I'm not sure whether this actually has a difference. However, it once was used but I will call it depracated anyways now. Defaults to `1.2`. Wouldn't recommend changing this value.

- `min_p` | `depracated, float`: Also 'depracated' but was once used. Defaults to `0.1` and refers to the minimum presence.

- `stream` | `bool`: Whether to stream the AI's response or not. If `True`, then the `generate` function will use a `Generator[str, Any, Any]` to gradually yield tokens as the JLLM generates them. If `False`, the `generate` function will simply return the full text. Defaults to False.

- `temperature` | `float`: Value of 'randomness' for the AI. Defaults to `0.7`. Wouldn't recommend you to have this value over `1.2` but results vary, I suppose.

- `stop` | `list[str]`: A list of 'stop' elements for the LLM. JAI uses only a `<` and I would recommend using this too. Like I mentioned, defaults to `['<']`.

4. Calling the `generate` function example **without** streaming:
```py
api = API(jwt) # use your actual JWT here

resp = api.generate(
    messages=[{"role": "user", "content": "Yo"}],
    stream=False)

print(next(resp))

# Output: Hello! How can I help you today? If you have any questions or need assistance, feel free to ask.
```

5. Calling the `generate` function but this time with streaming
```py
api = API(jwt)

for chunk in api.generate(
    messages=[{"role": "user", "content": "Yo"}],
    stream=True
):

    print(chunk, end="", flush=True)
print("\n") # final newline so AI's output doesn't merge with the debug message of selenium when the webdriver closes

# Output: Hello! How can I assist you today? If you have any questions or need help with something, feel free to ask.
```


## Badges
[![License: GPL v3.0](https://img.shields.io/badge/License-GPL%20v3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)
