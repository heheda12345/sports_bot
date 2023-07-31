# sports_bot
Upload activity gpx to strava with the control of telegram bot. Currently supports xingzhe and Zeeplife.
# Setup
1. `cp config.ini.example` and fill config.ini with your personal information
2. `pip install -r requirements.txt`
3. Get strava oauth token
    * Generate ssl certificate and put the path in config.ini
        * `openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365`
    * `python3 strava_token.py`
    * visit `https://server_ip:server_port/strava` (`https://localhost:8000` by default) and authorize the app. The token will be saved at token.json
4. Setup selenium
    ```bash
    # install chrome
    sudo apt install google-chrome-stable
    # install chromedriver
    sudo apt install chromium
    # test
    python3 -c "from selenium import webdriver; options = webdriver.chrome.options.Options(); options.add_argument('headless'); webdriver.Chrome(options=options); print('success')"
    ```
5. Launch telegram bot
    ```bash
    python3 telegram_bot.py
    ```