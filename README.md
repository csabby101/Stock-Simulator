# Stock Simulator

#### Video Demo: to be added

## Description:
* Web application that allows simulated trading of stocks from the US stock market. 
* Investors can practice buying and selling of stocks without risking real money.

## Configuring:
To register for an API key in order to be able to query IEX’s data, follow these steps:

* Visit iexcloud.io/cloud-login#/register/.
* Select the “Individual” account type, then enter your email address and a password, and click “Create account”.
* Once registered, scroll down to “Get started for free” and click “Select Start” to choose the free plan.
* Once you’ve confirmed your account via a confirmation email, visit https://iexcloud.io/console/tokens.
* Copy the key that appears under the Token column (it should begin with pk_).
* In the terminal (for windows) execute: 'set API_KEY=value', where value is the key/API Token.

## Tech and files :
This project was created using the python framework Flask.
The HTML template files were implemented using Jinja.
The real time stock price data was fetched from [IEX CLoud](https://iexcloud.io/) as it lets you download stock quotes via their API.

## Resources : 
This project is inspired by a problem set which I encountered during the course [CS50x 2021](https://cs50.harvard.edu/x/2021/).
Along with that, the official documentation of [Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/) and [Jinja](https://jinja.palletsprojects.com/en/2.11.x/templates/) were really useful.