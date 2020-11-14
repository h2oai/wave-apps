# wave-apps
Sample AI Apps built with H2O Wave. Maintained by the Wave core team.

## Sample Apps Overview

| Application Name                        | Priority | Progress                                                     | Something Can Be Demod Today |
| --------------------------------------- | -------- | ------------------------------------------------------------ | ---------------------------- |
| Mitigating Churn Risk                   | 1        | Needs to be re-written for OSS                               | √                            |
| Automatic Restock                       | 1        |                                                              |                              |
| Sales Forecasting EDA                   | 2        | Needs to be re-written for OSS                               | √                            |
| Explaining Hotel Ratings                | 2        | Explainable NLP app exists, need to make a paired down use case focused version | √                            |
| Identifying Fraudsters                  | 2        |                                                              |                              |
| Social Media Sentiment                  | 3        | Explainable NLP app exists, need to make a paried down use case focused version | √                            |
| Human-in-the-Loop Credit Risk           | 3        |                                                              |                              |
| Online Shopping Reccomendations         | 3        | Marketbasket application exists, need to make a paried down use case focused version | √                            |
| Model Revenue Impact                    | 3        |                                                              |                              |
| Getting Started with Teachable Machines | 4        |                                                              |                              |
| Getting Started with Images             | 4        |                                                              |                              |
| Getting Started with NLP                | 4        | Demo app from Gartner of text genration using GPT-2, needs to be rewritting for OSS | √                            |
| Model Card                              | 4        |                                                              |                              |
| Advanced Wave App Development           | 5        |                                                              |                              |
| Guess the Number                        | 5        |                                                              |                              |



### [Advanced Wave App Development](advanced-wave-dev/README.md)

**Industry:** N/A

**App User Persona:** Data Scientist

**Details:** Tutorial application that details software engineering best practices that data scientist may want to use in their applications: error handling, logs, readme, etc. This application uses these best practices and also is a flow walking through each one



### Automatic Restock

**Industry**: Supply Chain

**App User Persona:** Operations Manager

**Details:** Compares lead time, forecasts, and current inventory to provide an ordered list of items to restock and gives the user the ability to edit this information



### Explaining Hotel Ratings

**Industry:** Tourism

**App User Persona:** Data Scienist 

**Details:** After getting predictions of star raitings from AutoML this application will find the top words and phrases in each decile of predictions to help explain what about the hotels led to the reviews



### Getting Started with Images

**Industry:** Data Science

**App User Persona:** Application Developer

**Details:** Build an image-hello-world model using the MNIST dataset and view the images with the highest error



### Getting Started with NLP

**Industry:** Data Science

**App User Persona:** Application Developer

**Details:** A language generation application which takes text from a user and appends new, predictive text. This is a demo application for app devs to learn how to use third-party best in breed NLP models in their apps. This could evolve into a chat bot. 



### Getting Started with Teachable Machines

**Industry:** Data Science

**App User Persona:** Application Developer

**Details:** A language generation application which takes text from a user and appends new, predictive text. This is a demo application for app devs to learn how to use third-party best in breed NLP models in their apps. This could evolve into a chat bot. 



### Guess the Number

**Industry:**

**App User Persona:** Application Developer

**Details:** This a game where the machine "thinks" of a number and the human has to guess, getting told higher or lower. This application has a leader board where different users can compete to see who can guess numbers in the fewest number of turns, on average. This application teaches the developer about different app states and could be fun for new users.



### Human-in-the-Loop Credit Risk

**Industry:** Banking

**App User Persona:** Analyst

**Details:** This application allows a business uer to review model predictions on whether or not someone will pay off their credit card - a model used to approve or deny credit card applications. Specifically, this app provides a list of predictions the model is not confident about (predictions in the 0.4 to 0.6 range) and allows the end user to mark someone as approved or not



### Identifying Fraudsters

**Industry:** finance

**App User Persona:** Security Analyst

**Details:** Data dependent - network analysis to visualize relationship with known fraudsters is ideal



### Model Card

**Industry:** Anything regulated 

**App User Persona:** Risk Officer

**Details:** This application is robust documentation that explains one of the models in another OSS App. See https://modelcards.withgoogle.com/about for an example.



### Mitigating Churn Risk

**Industry**: Telco

**App User Persona:** Call center rep

**Details:** Provided liklihood to churn and actionable recommendations to prevent churn via nicely-presented top shapley values



### Model Revenue Impact

**Industry:** All

**App User Persona:** Data science project's business owner

**Details:** User puts in the cost of a False Negative and False Positive and then can explore different model thresholds to see how to best use this model in production. The machine learning concepts are abstracted away, the focus is to allow a business user to interact with a mojo.



### Online Shopping Reccomendations

**Industry:** Retail

**App User Persona:** Marketing Analyst

**Details:** This application allows a marketing anlayst to understand how their reccomendation engine works. It allows them to add items to their cart and as they do a list of reccomended products is updated.



### Sales Forecasting EDA

**Industry**: Retail

**App User Persona:** Analyst

**Details:** Provides easy-to-use interface for exploring historical sales values and looking at future forecasts accross store segments



 ### Social Media Sentiment

**Industry**: any customer facing business

**App User Persona:** Social Media Manager

**Details:** An explainable text model which runs on data pulled from a specific twitter hashtag and show the positive and negative words of each tweet. Data can be sorted by most or least negative so that the user can address worst tweets first.











