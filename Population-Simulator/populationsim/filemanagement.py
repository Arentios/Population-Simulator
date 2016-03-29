'''
Created on Mar 22, 2016
Module to handle the people file for the people simulator
@author: Eric Marshall
'''
import logging
import shutil
import constants
import cPickle
import os

def save_people_file(people):
  
    try:
        with open(constants.PEOPLE_FILE, 'w') as output:
                cPickle.dump(people,output)
        return True
    except IOError as e:
        logging.error('Failed to write people file with error: ' + e)
        return False

def load_people_file():
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




def backup_people_file():
    try:
        shutil.copyfile(constants.PEOPLE_FILE, constants.PEOPLE_FILE+'.bak')
    except Exception as e:
        logging.error(e)
        return False
    return True

def restore_people_file():
    try:
        shutil.copyfile(constants.PEOPLE_FILE+'.bak', constants.PEOPLE_FILE)
    except Exception as e:
        logging.error(e)
        return False
    return True

def audit_people_file():
    pass

def empty_people_file():
    try:
        with open(constants.PEOPLE_FILE, 'w'):
            pass
    except Exception as e:
        logging.error(e)
        return False
    return True

def get_people_file_size():
    fileinfo = os.stat(constants.PEOPLE_FILE)
    return fileinfo.st_size
