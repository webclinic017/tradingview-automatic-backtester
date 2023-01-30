### 【Archive】Automates Backtesting on TradingView by Python Selenium.

## Disclaimer  
1. If you run more than 4 backtest proccesses parallelly with this system on TradingView, you will get temporarily banned.
2. I haven't done any maintenance on this system since June 2022 and I won't.
  
## How does it work?  
  
This app was designed to backtest trading strategies on TradingView. Since an API is not available, it manipulates the TradingView website using Selenium. Users can input their trading strategy, parameters, time-frames, etc. into the app, which has been dockerized and deployed via a REST API. The app runs backtests and repeatedly optimizes parameters until it finds the best set. Finally, the app provides the user with the optimal parameters.
   
That's all I remember...  
  
## History  
  
This is my first ever application that I built in mid-2022. Although there are many mistakes in the code, I feel like keeping it as is. Creating this app was one of the biggest challenges and most painful experiences in my life before age 25. I had little experience with Python, so it took me a couple of months to build the app and days to install Python and a week to understand and activate the virtual environment. In the future, I would like to look back at the code and feel a sense of nostalgia, as it serves as a milestone in my personal and professional journey. 
