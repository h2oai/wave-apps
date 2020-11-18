# wave-apps
Sample AI Apps built with H2O Wave. Maintained by the Wave core team.

| Application Name                                             | Priority | Progress                                                     | Something Can Be Demod Today | Dataset                                                      |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ---------------------------- | ------------------------------------------------------------ |
| [Mitigating Churn Risk](churn-risk/README.md)                | 1        | Needs to be re-written for OSS                               | √                            | https://www.kaggle.com/blastchar/telco-customer-churn        |
| [Automatic Restock](automatic-restock/README.md)             | 1        |                                                              |                              | https://www.kaggle.com/c/favorita-grocery-sales-forecasting/ |
| [Sales Forecasting EDA](sales-forecasting/README.md)         | 2        | Needs to be re-written for OSS                               | √                            | https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting |
| [Explaining Ratings](explaining-ratings/README.md)           | 2        | Explainable NLP app exists, need to make a paired down use case focused version | √                            | https://www.kaggle.com/datafiniti/hotel-reviews              |
| [Identifying Fraudsters](identifying-fraudsters/README.md)   | 2        |                                                              |                              |                                                              |
| [Social Media Sentiment](twitter-sentiment/README.md)        | 3        | Explainable NLP app exists, need to make a paried down use case focused version | √                            |                                                              |
| [Human-in-the-Loop Credit Risk](credit-risk/README.md)       | 3        |                                                              |                              | https://www.kaggle.com/uciml/default-of-credit-card-clients-dataset |
| [Online Shopping Recommendations](shopping-cart-recommendations/README.md) | 3        | Marketbasket application exists, need to make a paried down use case focused version | √                            |                                                              |
| [Model Revenue Impact](model-impact/README.md)               | 3        |                                                              |                              |                                                              |
| [Getting Started with Teachable Machines](getting-started-with-teachable-machines/README.md) | 4        |                                                              |                              |                                                              |
| [Getting Started with Images](getting-started-with-images/README.md) | 4        |                                                              |                              |                                                              |
| [Getting Started with NLP](getting-started-with-nlp/README.md) | 4        | Demo app from Gartner of text genration using GPT-2, needs to be rewritting for OSS | √                            |                                                              |
| [Model Card](model-card/README.md)                           | 4        |                                                              |                              |                                                              |
| [Advanced Wave App Development](advanced-wave-dev/README.md) | 5        |                                                              |                              |                                                              |
| [Guess the Number](guess-the-number/README.md)               | 5        |                                                              |                              |                                                              |



## Sample Apps Overview



### [Advanced Wave App Development](advanced-wave-dev/README.md)

**Industry:** N/A

**App User Persona:** Data Scientist

**Details:** Tutorial application that details software engineering best practices that data scientist may want to use in their applications: error handling, logs, readme, etc. This application uses these best practices and also is a flow walking through each one



### [Automatic Restock](automatic-restock/README.md)

**Industry**: Supply Chain

**App User Persona:** Operations Manager

**Details:** Compares lead time, forecasts, and current inventory to provide an ordered list of items to restock and gives the user the ability to edit this information



### [Explaining Ratings](explaining-ratings/README.md)

**Industry:** Tourism

**App User Persona:** Data Scienist 

**Details:** After getting predictions of star raitings from AutoML this application will find the top words and phrases in each decile of predictions to help explain what about the hotels led to the reviews



### [Getting Started with Images](getting-started-with-images/README.md)

**Industry:** Data Science

**App User Persona:** Application Developer

**Details:** Build an image-hello-world model using the MNIST dataset and view the images with the highest error



### [Getting Started with NLP](getting-started-with-nlp/README.md)

**Industry:** Data Science

**App User Persona:** Application Developer

**Details:** A language generation application which takes text from a user and appends new, predictive text. This is a demo application for app devs to learn how to use third-party best in breed NLP models in their apps. This could evolve into a chat bot. 



### [Getting Started with Teachable Machines](getting-started-with-teachable-machines/README.md)

**Industry:** Data Science

**App User Persona:** Application Developer

**Details:** A language generation application which takes text from a user and appends new, predictive text. This is a demo application for app devs to learn how to use third-party best in breed NLP models in their apps. This could evolve into a chat bot. 



### [Guess the Number](guess-the-number/README.md)

**Industry:**

**App User Persona:** Application Developer

**Details:** This a game where the machine "thinks" of a number and the human has to guess, getting told higher or lower. This application has a leader board where different users can compete to see who can guess numbers in the fewest number of turns, on average. This application teaches the developer about different app states and could be fun for new users.



### [Human-in-the-Loop Credit Risk](credit-risk/README.md)

**Industry:** Banking

**App User Persona:** Analyst

**Details:** This application allows a business uer to review model predictions on whether or not someone will pay off their credit card - a model used to approve or deny credit card applications. Specifically, this app provides a list of predictions the model is not confident about (predictions in the 0.4 to 0.6 range) and allows the end user to mark someone as approved or not



### [Identifying Fraudsters](identifying-fraudsters/README.md)

**Industry:** finance

**App User Persona:** Security Analyst

**Details:** Data dependent - network analysis to visualize relationship with known fraudsters is ideal



### [Mitigating Churn Risk](churn-risk/README.md)

**Industry**: Telco

**App User Persona:** Call center rep

**Details:** Provided liklihood to churn and actionable recommendations to prevent churn via nicely-presented top shapley values



### [Model Card](model-card/README.md)

**Industry:** Anything regulated 

**App User Persona:** Risk Officer

**Details:** This application is robust documentation that explains one of the models in another OSS App. See https://modelcards.withgoogle.com/about for an example.



### [Model Revenue Impact](model-impact/README.md)

**Industry:** All

**App User Persona:** Data science project's business owner

**Details:** User puts in the cost of a False Negative and False Positive and then can explore different model thresholds to see how to best use this model in production. The machine learning concepts are abstracted away, the focus is to allow a business user to interact with a mojo.



### [Online Shopping Recommendations](shopping-cart-recommendations/README.md)

**Industry:** Retail

**App User Persona:** Marketing Analyst

**Details:** This application allows a marketing anlayst to understand how their reccomendation engine works. It allows them to add items to their cart and as they do a list of reccomended products is updated.



### [Sales Forecasting EDA](sales-forecasting/README.md)

**Industry**: Retail

**App User Persona:** Analyst

**Details:** Provides easy-to-use interface for exploring historical sales values and looking at future forecasts accross store segments



 ### [Social Media Sentiment](twitter-sentiment/README.md)

**Industry**: any customer facing business

**App User Persona:** Social Media Manager

**Details:** An explainable text model which runs on data pulled from a specific twitter hashtag and show the positive and negative words of each tweet. Data can be sorted by most or least negative so that the user can address worst tweets first.











