# Population-Simulator
Simulator for a population of pseudo people

This simulator deploys a Flask based web service which can be used to generate a population of pseudo people
These people can then be run through a given number of steps and will age, partner up, have children, and pass away

Basic settings currently use Flask defaults, so if run from localhost a sample run would be something like:

http://localhost:5000/generate/500 #Generates 500 people to begin with

http://localhost:5000/process/100 #Runs 100 steps, vaguely equivalent to a year each

http://localhost:5000/peopleInformation #Reports auditing information such as number of people and and general statistics
