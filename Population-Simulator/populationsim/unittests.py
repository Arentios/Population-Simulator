'''
Created on Mar 23, 2016
Unit Testing for People Simulator
@author: Arentios
'''
import unittest
import filemanagement
import personsimulator


class TestPersonSimulator(unittest.TestCase):

    
    #Performs a suite of basic functions to make sure file management works fine
    def test_file(self):
        self.assertTrue(filemanagement.backupPeopleFile(), 'People file failed to backup')
        self.assertTrue(filemanagement.emptyPeopleFile(), 'People file failed to empty')
        emptyFileSize = filemanagement.getPeopleFileSize()
        self.assertEqual(personsimulator.generatePeople(1), 'People generated successfully', 'Failed to generate a single person')
        singleFileSize = filemanagement.getPeopleFileSize()
        self.assertGreater(singleFileSize, emptyFileSize, 'Single person file size not greater than empty')
        self.assertTrue(filemanagement.loadPeopleFile(), 'Failed to load people file for a single person')
        self.assertEqual(personsimulator.generatePeople(4), 'People generated successfully', 'Failed to generate multi run people file')
        multifileSize = filemanagement.getPeopleFileSize()
        self.assertGreater(multifileSize, singleFileSize, 'Multi person file size not greater than single')
        self.assertTrue(filemanagement.loadPeopleFile(), 'Failed to load multi run people file')
        self.assertTrue(filemanagement.restorePeopleFile(), 'Failed to restore backed up people file')
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()