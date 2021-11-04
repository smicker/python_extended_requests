#!./myenv/bin/python3

from requests.models import HTTPError, ConnectionError
from src.web_caller import WebCaller

def main():
    """ Get your test url and see your postings here: http://ptsv2.com/
    Example below is for url http://ptsv2.com/t/8ut6c-1636028392/post
    """

    webcaller = WebCaller(base_url="http://ptsv2.com", retries=3, timeout=5)
    webcaller.set_basic_auth("Kalle", "LOPPAN")

    data: dict = {
        "Name": "Micke",
        "Profession": "Programming"
    }

    try:
        response = webcaller.web_post("/t/8ut6c-1636028392/post", data=data)
        print(response)
    except HTTPError as err:
        print("HTTPError is caught!")
        print(err)
    except ConnectionError as err:
        print("ConnectionError is caught!")
        print(err)

if __name__ == "__main__":
    main()
