'''
Created on Mar 21, 2016
Module to handle creation of list of pseudo people and run simulations for a given number of steps for those people
People currently age, partner up, have children, and die
NYI List:
    Re-partnering/Multiple partners
    Additional attributes for people to impact decisions
    More complex matching for potential partners
    
@author: Eric Marshall
'''
from flask import Flask
import random
import pickle
import sys
import uuid
import shutil
import logging
import constants
import filemanagement
import traceback

logging.basicConfig(filename=constants.LOG_FILE, level=logging.INFO)

app = Flask(__name__)

#Class to handle people
#Used a lookup table (dictionary) to store links to people using UUID to avoid storing direct object links as direct object links lead to a massively recurvise tree that is impossible to save
#This implementation is slightly less performant than using direct object links but only marginally
class Person:
    lookupTable = {}
    def __init__(self, age = -1, happiness = -1, attributes = {}, parents = [], children = [], partner = []):
        self.personId = uuid.uuid1()
        #Use -1 to indicate a generated person since 0 is for babies
        #Original ancestor, start them all at a decent age to kickstart the simulation
        if age == -1:
            self.age = random.randint(18,30)
        else:
            self.age = age
        #Original ancestor, random happiness
        if happiness == -1:
            self.happiness = random.randint(50,100)
        else:
            self.happiness = happiness
        #Original ancestor, only attribute for them is health
        if attributes == {}:
            self.attributes = { 'health' : random.randint(1,100)}
        else:
            self.attributes = attributes
        self.parents = list(parents)
        self.children = list(children)
        self.partner = list(partner)
        #Deceased people aren't removed but are used both for auditing and for maintaining genealogical relationships
        self.alive = True
        #Add new person to the dictionary
        self.lookupTable[self.personId] = self

        

@app.route('/restore', methods=['GET'])
def restoreBackup():
    if filemanagement.restorePeopleFile() == True:
        return 'Successfully backed up people file'
    return 'Failed to backup people file'


@app.route('/empty', methods=['GET'])
def emptyPeople():
    logging.info("Emptying person file")
    if filemanagement.emptyPeopleFile() == True:
        return 'Successfully emptied people file'
    return 'Failed to empty people file'
    


@app.route('/backup', methods=['GET'])
def backupPeople():
    if filemanagement.backupPeopleFile() == True:
        return 'Successfully backed up people file'
    return 'Failed to backup people file'
    
    
def processYear(people):
    logging.info('Processing people')
    logging.debug('Opening file')
    logging.info('Began processing year, number of people is ' + str(len(people)))
    #Iterate over a copy of the list of people since we may be deleting
    
    #Keep track of possible partners on an ongoing basis
    #Filtering in real time becomes a massive performance hit once the population becomes large
    possiblePartners = []
    #Only process living people, the dead do not change
    peopleToProcess = [x for x in people if x.alive == True]
    logging.info("Living people: " + str(len(peopleToProcess)))
    for person in list(peopleToProcess):
        #Very primitive check for death from old age/disease/failing health
        #TODO: Develop beyond simply abstract 'health' system
        #Health applies a random factor both for semi-realism and to avoid a minimum age of health/2
        if random.randint(1,100) * 2 < person.age - random.randint(1,person.attributes['health']):
            
            logging.info('Person ' + str(person.personId) + ' with age ' + str(person.age) + ' has died, their happiness was ' + str( person.happiness) + ' and they had ' + str(len(person.children)) + ' children')
            #If the person's parents are still alive reduce their happiness by 10, siblings by 5, partner by 20, children by 10
            #Don't remove data from those objects for future analysis or dumping. This does prevent re-partnering right now
            for parentId in person.parents:
                
                parent = Person.lookupTable[parentId]
                if parent.alive == True:
                    parent.happiness = parent.happiness - 10
                #Figure out siblings by going up to parents and digging down a level
                for siblingId in parent.children:
                    sibling = Person.lookupTable[siblingId]
                    if sibling != person and sibling.alive == True:
                        #Subtract a random amount
                        #Full siblings will end up being counted twice, once per parent, half siblings only once
                        #Social commentary? Terrible assumption? Both? Probably but this is also straightforward to implement
                        sibling.happiness = sibling.happiness - random.randint(1,5)
            for partnerId in person.partner:
                partner = Person.lookupTable[partnerId]
                if partner.alive == True:
                    partner.happiness = partner.happiness - 20
            for childId in person.children:
                child = Person.lookupTable[childId]
                if child.alive == True:
                    child.happiness = child.happiness - 10
            #Finally remove the person from the list
            #TODO: Add the person to some historical data structure                       
            peopleToProcess.remove(person)
            person.alive = False
            
            
            continue
        else:
            #If the person survived increment their age and check to see if they are valid to be added to the partner list
            logging.debug('Person ' + str(person.personId) + ' survived, increasing age')
            person.age = person.age + 1
            #Slight happiness fluctuation per year
            person.happiness = person.happiness + random.randint(-3,3)
            if not person.partner and person.age >= 18:
                possiblePartners.append(person)
                
    #Now that deaths are processed take care of everything else            
    for person in list(peopleToProcess):    
        #Time for happy thoughts!
        if not person.partner and person.age >= 18 and random.randint(1,100) < person.happiness:
            #TODO: Need better checks here, such as for siblings
            for prospectivePartner in [x for x in possiblePartners if x.personId not in person.parents and x.personId not in person.children and (not person.parents or set(x.parents) != set(person.parents))  and x.personId != person.personId]:
                #Try to arrange a marriage, mirrored happiness requirements and a 50/50 shot right now
                #TODO: More attributes matching!
                if  random.randint(1,100) < prospectivePartner.happiness and random.randint(1,2) > 1:
                    person.partner.append(prospectivePartner.personId)
                    prospectivePartner.partner.append(person.personId)
                    logging.debug('Person ' + str(person.personId) + " has become partners with " + str(prospectivePartner.personId))
                    #Both people gain a variable amount of happiness with the average being slightly above what they'd lose if their partner dies
                    person.happiness = person.happiness + (random.randint(11,30))
                    prospectivePartner.happiness = prospectivePartner.happiness + (random.randint(11,30))
                    possiblePartners.remove(person)
                    possiblePartners.remove(prospectivePartner)
                    #Only one marriage per person at a time right now
                    break
                    
        #Maybe create some children? All children come from partnered couples just because
        #Since both sides of a couple will be checked independently there maybe be 0-2 children. Twin case
        if len(person.partner) > 0 and random.randint(1,8)  == 1 and person.age < 50:
            #In case of multiple partners pick a random one to be the other parent
            secondParent = Person.lookupTable[random.choice(person.partner)]
            child = Person(age=0, parents=[person.personId, secondParent.personId], happiness = person.happiness / 3 + secondParent.happiness /3 + random.randint(1,33),attributes={'health' :   person.attributes['health'] / 3 + secondParent.attributes['health'] /3 + random.randint(1,33)})
            people.append(child)
            #Both parents gain a variable amount of happiness with the average being slightly above what they'd lose if a child dies
            person.happiness = person.happiness + (random.randint(1,20))
            secondParent.happiness = secondParent.happiness + (random.randint(1,20))
            person.children.append(child.personId)
            secondParent.children.append(child.personId)
        
            logging.debug('New child ' + str(child.personId) + ' born to ' + str(person.personId) + ' and ' + str(secondParent.personId))
        
    logging.info('Completing processing year, number of people is ' + str(len(people)))
    return people


@app.route('/process', methods=['GET'])
def processSingleYear():
    try:
        people = filemanagement.loadPeopleFile()          
        people = processYear(people)
        filemanagement.savePeopleFile(people)
    except Exception as e:
        logging.error(e)
        return 'Failed to process'
    return 'Processed a single year'
                          
@app.route('/process/<int:numYears>', methods=['GET'])
def processMultipleYears(numYears):
    try:
        people = filemanagement.loadPeopleFile()      
        print len(people[0].lookupTable)
        for i in range(0,numYears):
            logging.info('Processing year ' + str(i+1))
            people = processYear(people)
        filemanagement.savePeopleFile(people)
    except Exception as e:
        logging.error(e)
        traceback.print_tb(sys.exc_traceback)
        return 'Failed to process'
    return 'Processed ' + str(numYears) + ' years'
    


@app.route('/generate/<int:numPeople>',methods=['GET'])
def generatePeople(numPeople):
    
    
    people = []      
    logging.info('Generating ' + str(numPeople) + ' new people')
    for i in range(0,numPeople):        
        person = Person()
        people.append(person)
        
    logging.debug('Writing to file'  ) 
    try:
        filemanagement.savePeopleFile(people)
        return 'People generated successfully'
    except IOError as e:
        logging.error('Failed to write people file with error: ' + e)
    

#Auditing function used to get basic data on the people file and check for data integrity
@app.route('/peopleInformation',methods=['GET'])
def auditPeople():
    people = filemanagement.loadPeopleFile()         
    returnMessage = 'Number of people in people file: ' + str(len(people)) + '<br>'
    #Nothing more to do if there's nobody in the people file
    if not people:
        return returnMessage 
    parents = 0
    partners = 0
    children = 0.0
    deadHappiness = 0
    deadCount = 0
    deadChildren = 0
    liveHappiness = 0
    originalGeneration = [] #List of people with no parents
    for person in people:
        if len(person.partner) > 1:
            returnMessage = returnMessage + 'Detected multiple partners, should not happen in the current version<br>'
        if not person.parents:
            originalGeneration.append(person)
        parents = parents + len(person.parents)
        partners = partners + len(person.partner)
        children = children + len(person.children)
        if person.alive == False:
            deadHappiness = deadHappiness + person.happiness
            deadCount = deadCount + 1
            deadChildren = deadChildren + len(person.children)
        else:
            liveHappiness = liveHappiness + person.happiness
    liveCount = len(people) - deadCount
    returnMessage = returnMessage + 'Number of live people: ' + str(liveCount) + '<br>'                     
    returnMessage = returnMessage + 'Number of dead people: ' + str(deadCount) + '<br>' 
    returnMessage = returnMessage + 'Average number of children overall: ' + str(children/(len(people))) + '<br>'    
    returnMessage = returnMessage + 'Average happiness of the living: ' + str(liveHappiness/liveCount) + '<br>' 
    if deadCount > 0:
        returnMessage = returnMessage + 'Average number of children for the dead: ' + str(deadChildren/deadCount) + '<br>' 
        returnMessage = returnMessage + 'Average happiness of the dead: ' + str(deadHappiness/deadCount) + '<br>' 
    returnMessage = returnMessage + 'Number of partnered people: ' + str(partners)  + '<br>' 
    
    #Perform a recursive search to find total number of generations
    totalGenerations = 0 
    for person in originalGeneration:
        currGenerations = generationCount(person)
        if currGenerations > totalGenerations:
            totalGenerations = currGenerations
    returnMessage = returnMessage + 'Number of generations: ' + str(totalGenerations)  + '<br>' 
            
    return returnMessage

#Function to determine the total number of generations descended from a given person
def generationCount(person):
    if not person.children:
        return 1
    if len(person.children) > 0:
        return 1 + max(generationCount(person.lookupTable[child]) for child in person.children)


if __name__ == '__main__':
    random.seed()
    app.run(debug=False)