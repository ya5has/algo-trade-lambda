## Automate execution of trades on Zerodha

Using algo-trade-lambda you can execute the stock trades on zerodha automatically. Currently the best way is to code your trading strategy on amibroker AFL and run the trading system. Configure to send the buy or short signals to your aws lambda server where the trade is then executed and all subsequent updates will be sent to your telegram group. 


### How to Install

Install python libraries

` $ pip install -r requirements.txt`

Edit your kite account constants in app.py

To test the code locally

`$ python app.py`

Login to your kite account to get access token for the day

Test the app by sending http request from a rest client to your local server


### Deploy on aws Lambda

To deploy on aws lambda, configure zappa settings.json

`$ zappa deploy`

Congrats you can now send trade signals from your amibroker to kite.


#### More information on setting up telegram group will be updated soon.


### License

The content of this repository is licensed under a [Creative Commons Attribution License](http://creativecommons.org/licenses/by/3.0/us/)
