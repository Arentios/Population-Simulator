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
        self.assertTrue(filemanagement.backup_people_file(), 'People file failed to backup')
        self.assertTrue(filemanagement.empty_people_file(), 'People file failed to empty')
        emptyFileSize = filemanagement.get_people_file_size()()
        self.assertEqual(personsimulator.generate_people(1), 'People generated successfully', 'Failed to generate a single person')
        singleFileSize = filemanagement.get_people_file_size()()
        self.assertGreater(singleFileSize, emptyFileSize, 'Single person file size not greater than empty')
        self.assertTrue(filemanagement.load_people_file()(), 'Failed to load people file for a single person')
        self.assertEqual(personsimulator.generate_people(4), 'People generated successfully', 'Failed to generate multi run people file')
        multifileSize = filemanagement.get_people_file_size()()
        self.assertGreater(multifileSize, singleFileSize, 'Multi person file size not greater than single')
        self.assertTrue(filemanagement.load_people_file()(), 'Failed to load multi run people file')
        self.assertTrue(filemanagement.restore_people_file()(), 'Failed to restore backed up people file')
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()