# Sample Wave Apps

H2O Wave allows you to build AI apps, faster. This directory houses sample applications that you can download and run locally, modify, and integrate into your own AI apps. 

## Installation 

Follow the instructions [here](https://wave.h2o.ai/docs/installation) to download and run the latest Wave Server, a requirement for all sample apps. Then, choose an app from below for setup instructions.



## Available Apps 

### [Explainable Hotel Ratings](explaining-ratings/README.md)

**Details:** This app allows you to filter hotel reviews and compare the most common phrases from the subset to the overall most common phrases.



### [Guess the Number](guess-the-number/README.md)

**Details:** This a game where the machine "thinks" of a number and the human has to guess, getting told higher or lower. This application has a leader board where different users can compete to see who can guess numbers in the fewest number of turns, on average. This application teaches the developer about different app states and could be fun for new users.



### [Human-in-the-Loop Credit Risk](credit-risk/README.md)

**Details:** This application allows a business user to review model predictions on whether or not someone will pay off their credit card - a model used to approve or deny credit card applications. Specifically, this app provides a list of predictions the model is not confident about (predictions in the 0.4 to 0.6 range) and allows the end user to mark someone as approved or not.



### [Mitigating Churn Risk](churn-risk/README.md)

**Details:** This application builds a churn prediction model with H2O-3 and provides the likelihood to churn and actionable recommendations to prevent churn via nicely-presented top shapley values.



### [Online Shopping Recommendations](shopping-cart-recommendations/README.md)

**Details:** This application allows a marketing anlayst to understand how their recommendation engine works. It allows them to add items to their cart and as they do a list of recommended products is updated.



### [Sales Forecasting EDA](sales-forecasting/README.md)

**Details:** This application provides easy-to-use interface for exploring historical sales values and looking at future forecasts across store segments



 ### [Social Media Sentiment](twitter-sentiment/README.md)

**Details:** This application pulls tweets and uses the open source VaderSentiment to understand positive and negative tweets



## FAQs
While trying to run any of the apps particularly on Windows terminal, below are given some common errors and their fixes:

**1. make (e=2): The system cannot find the file specified** This is due to the os confusing between 'bin' and 'Scripts'. If you face this issue, open the Makefile present in the app folder using some Text Editor, and replace the word 'bin' with 'Scripts' in the virtual environment path of Setup and Run sections.

**2. make command not found:** This error comes when make is not installed on your OS. You can install make easily in Windows. More info on installing make is available on the Internet. You can also refer to their official website here: https://gnuwin32.sourceforge.net/packages/make.htm

**3. Python not found:** This error is probably if Windows is not able to recognise the path of Python. The path of Python can be updated in the pyvenv.cfg file, located in [App Folder]/venv. The venv folder comes preloaded in the app repo.


