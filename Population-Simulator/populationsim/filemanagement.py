'''
Created on Mar 22, 2016

@author: Eric Marshall
'''
import logging
import shutil
import constants
import cPickle

def savePeopleFile(people):
  
    try:
        with open(constants.PEOPLE_FILE, 'w') as output:
                cPickle.dump(people,output)
        return True
    except IOError as e:
        logging.error('Failed to write people file with error: ' + e)
        return False

def loadPeopleFile():
    people = []
    try:
        with open(constants.PEOPLE_FILE, 'r') as peopleInput:
            try:
                #Load from the pickle file, remembering that people can be generated in multiple batches
                while 1:
                    try:
                        picklePeople = cPickle.load(peopleInput)
                        for currPicklePerson in picklePeople:
                            people.append(currPicklePerson)
                    except EOFError:
                        break
                    except Exception as e:
                        logging.error('Error while processing people file: ' +e)
            except Exception as e:
                logging.error('Error while processing people file: ' + e)
    except IOError as e:
        logging.error('Failed to open people file with error: ' + e)
        return []
    #Add each person back to the lookup table
    for person in people:
        person.lookupTable[person.personId] = person
    return people




def backupPeopleFile():
    try:
        shutil.copyfile(constants.PEOPLE_FILE, constants.PEOPLE_FILE+'.bak')
    except Exception as e:
        logging.error(e)
        return False
    return True

def restorePeopleFile():
    try:
        shutil.copyfile(constants.PEOPLE_FILE+'.bak', constants.PEOPLE_FILE)
    except Exception as e:
        logging.error(e)
        return False
    return True

def auditPeopleFile():
    pass

def emptyPeopleFile():
    try:
        with open('people.txt', 'w') as output:
            pass
    except Exception as e:
        logging.error(e)
        return False
    return True