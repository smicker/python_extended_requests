# About
This is an implementation of a web call helper class. It extends the python requests class
with some advanced features like:
- base_url
- default web call timeout
- default web call retries on every ConnectionError problem (not on 4xx or 5xx problems though)
- exponential backoff during retries
- setting basic auth once instead of for each web call
- throws HTTPError on every 4xx or 5xx response from server

# Requirements
The python libs requests and requests-toolbelt.

Install by:
```
python3 -m venv myenv
. myenv/bin/activate
pip install -r requirements.txt
```

# How to use
Just include the WebCaller class in src/web_caller and then create an instance of this class.
Then use this instance to do web calls in the same way as a requests instance.
See a typical example in the main.py file.
To see examples for all functionality, please look at the test cases tests/test_web_caller.py.

```
from src.web_caller import WebCaller
webcaller = WebCaller(base_url="http://ptsv2.com", retries=3, timeout=5)
webcaller.setBasicAuth("Kalle", "LOPPAN")
response = webcaller.web_post("/t/3hwxx-1632489409/post", data={"Name": "Micke"})
```

# Tests
First you need to create a test web site that can receive get and post calls.
To do this:
1. Browse to http://ptsv2.com/
2. Click "New Random Toilet"
3. Note down the Post URL, probably something like /t/8ut6c-1636028392/post
4. Insert the Post URL at the variable TEST_POSTFIX_URL in test_web_caller.py.

Run unittests from the project folder by:
```python3 -m unittest discover -s tests -t .```