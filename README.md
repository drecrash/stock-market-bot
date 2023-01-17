# Stock Market Bot

This is a Discord bot that somewhat simulates a stock market in your server

## Setup

* Run these commands in your server when the bot is added. The bot won't work without these parameters set:
     * /define-officer-role [role]
          * This command will define the role that will be allowed to deposit money, withdraw money, respond to tickets, register companies, and close tickets
     * /define-stocks-channel [channel]
          * This command will define the channel that the instant buy and instant sell prices of companies will go to
     * /opencompanyticket
          * Run this in a dedicated channel, this will generate a message with a button that can be used to open tickets
* Follow [this tutorial](https://youtu.be/wrR0YLzh4DQ/ "Tutorial link title") from 0:00 to 5:20 . Rename the json file ‘credentials.json’ and put it in the folder with main.py (not the cogs folder). This will allow the bot to write data into a Google spreadsheet of your choice


## Buying and Selling

* To instantly buy shares of a company, run /instantbuy [company_name] [shares]. ‘Shares’ is the amount of shares that you’re buying. This command will find the lowest price of all the sell orders for that company and purchase the needed amount. If the needed amount is greater than the amount available for the company, then it will purchase all the available shares
* To instantly sell shares of a company, run /instantsell [company_name] [shares]. It works basically the same way as instant buy. It’ll find the buy order for the largest cost, and sell your shares to it.

* To create a sell order, run /createsellorder [company_name] [shares] [cost_per_share]. The cost per share can be a custom number, the cost of the lowest sell order, the cost of the lowest sell order -1%, or the cost of the lowest sell order -5%.
* To create a sell order, run /createsellorder [company_name] [shares] [cost_per_share]. The cost per share can be a custom number, the cost of the highest buy order, the cost of the highest buy order -1%, or the cost of the highest buy order -5%.

* To close a buy or sell order, run /close(buy/sell)order [company]. This will return the non-bought shares for a company, if it’s a sell order, or will return the non-sold shares for a company, if it’s a buy order.

## Financial Officer Commands

* Financial officers can register people into companies through the command /register-company [name] [percentage] [ipo] [owner]. 
  * The name of the company is case-sensitive, and will be what is used to refer to the company in all commands. 
  * The percentage should be an integer value with no symbols. For example, if you were selling 36% of the company, the percentage parameter should be 36. 
  * The ipo is how much money each share will cost when the company goes public. This should also be an integer value. For example, if you were selling each share of your company for $48, the ipo parameter should be 48.
  * The owner is who owns the company, this will be added to their portfolio
* Financial officers can close tickets through the command /close-ticket .
* Financial officers can deposit money to a user through the command /deposit-money [user] [amount]. User is the member that the money is being deposited to, and the amount is the amount of money.
* Financial officers can withdraw money from a user through the command /withdraw-money [user] [amount]. User is the member that the money is being withdrawn from, and the amount is the amount of money.


## Other

* Members can run the command /portfolio [member] to see anyone’s stock portfolio. This includes their balance, the shares that they own, and the companies that they own.

## License

[MIT](https://choosealicense.com/licenses/mit/)
