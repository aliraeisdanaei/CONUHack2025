## Inspiration
We are really concerned about the challenges of global warming and we are especially alarmed by the increasing number of wildfires that have been occurring since at least 2020. 
We want to leverage technology to better manage and predict wildfires.

## What it does
There are two main functions for our IOS app:

 1. Managing fire fightings units to minimize damages and operational costs according to given wildfire data.
 This data can be given as a CSV file or as a link on our app. 
 2. To predict future wildfire data according to our AI model trained on historical environmental and wildfire data. 
 The data can be given as a CSV file or as a link on our app. 


## How we built it
We built the app using SwiftUI on Xcode for all IOS devices including Mac. 
We built our backend using Python and Flask. 
We especially leveraged the [lovable platform](https://lovable.dev/) which we learned through Tail'Ed. 
We deployed our backend on a server through a cloud platform called [Render](https://dashboard.render.com/).


## Challenges we ran into
The long hours and the long night was especially rough on our relationships with each other. 
Our teamwork and collaboration were tested in most intense situations. 
We came out with more consideration for each other and with stronger relationships overall. 


## Accomplishments that we're proud of
We are especially proud that we were able to accomplish all the goals that we set out in the morning of our hackathon.
It was not easy to do all the following:

 * To build a fully functioning IOS app
 * Make our app bilingual
 * Develop and **deploy** a backend
 * Train a prediction model with a ~90% accuracy, 88% F1 Score based on our historical environmental data

## What we learned
Most importantly we learned teamwork and collaboration with one another. 
It was very easy to sometimes get lost in the project and forget that our main goal was to have fun in the hackathon. 
To laugh about our problems and come together to solve them through effective teamwork was our biggest lesson. 

This was our first time that we built a backend, and we learned how to work with Flask and put together a simple, yet professional, and clean work. 

## What's next for Quebec FireFighters
There are so many possible enhancements for this app.
At first we wanted to use [SAT solvers like Z3](https://en.wikipedia.org/wiki/Z3_Theorem_Prover) to give the optimized usage of units logically. 
The benefit of this would be that the optimal deployment would be 100% accurate given the logical nature of the solver. 

This app could be expanded to support all localizations of the world. 
There is no need that our app should not help a global problem. 
We would love to pitch this app to firefighters, and we will try to look into setting meetings with them soon. 

Expanding our app to Android would also increase the usage of it and would be a necessary future step for our project. 
