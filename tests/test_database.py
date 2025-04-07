import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import initialize_database, save_patient_data, save_session_data, save_report

class TestDatabase(unittest.TestCase):
    """Test cases for the database module"""
    
    @patch('pymongo.MongoClient')
    def setUp(self, mock_client_class):
        """Set up the test environment"""
        # Create mock client and database
        self.mock_client = MagicMock()
        mock_client_class.return_value = self.mock_client
        
        self.mock_db = MagicMock()
        self.mock_client.__getitem__.return_value = self.mock_db
        
        # Mock collection names list
        self.mock_db.list_collection_names.return_value = []
        
        # Mock collections
        self.mock_patients = MagicMock()
        self.mock_sessions = MagicMock()
        self.mock_reports = MagicMock()
        
        self.mock_db.__getitem__.side_effect = lambda x: {
            'patients': self.mock_patients,
            'sessions': self.mock_sessions,
            'reports': self.mock_reports
        }.get(x, MagicMock())
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_patient_data(self, mock_open, mock_makedirs):
        """Test saving patient data to the file system"""
        # Test data
        patient_id = "12345"
        data = {
            "name": "John Doe",
            "condition": "depression",
            "registration_date": datetime.now()
        }
        
        # Call the function
        result = save_patient_data(patient_id, data)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify that the directory was created
        mock_makedirs.assert_called_once()
        
        # Verify that the file was opened and written to
        mock_open.assert_called_once()
        mock_open().write.assert_called_once()
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_session_data(self, mock_open, mock_makedirs):
        """Test saving session data to the file system"""
        # Test data
        patient_id = "12345"
        session_id = "session_67890"
        data = {
            "start_time": datetime.now(),
            "end_time": datetime.now(),
            "interactions": [
                {"user_message": "Hello", "bot_response": "Hi there"}
            ]
        }
        
        # Call the function
        result = save_session_data(patient_id, session_id, data)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify that the directories were created
        self.assertEqual(mock_makedirs.call_count, 2)
        
        # Verify that the file was opened and written to
        mock_open.assert_called_once()
        mock_open().write.assert_called_once()
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_report(self, mock_open, mock_makedirs):
        """Test saving report data to the file system"""
        # Test data
        patient_id = "12345"
        report_id = "report_67890"
        report_data = {
            "creation_date": datetime.now(),
            "report_type": "progress",
            "content": {"overall_assessment": "Patient is making progress"}
        }
        
        # Call the function
        result = save_report(patient_id, report_id, report_data)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify that the directories were created
        self.assertEqual(mock_makedirs.call_count, 2)
        
        # Verify that the file was opened and written to
        mock_open.assert_called_once()
        mock_open().write.assert_called_once()
    
    def test_initialize_database_success(self):
        """Test successful database initialization"""
        # Call the function
        db = initialize_database()
        
        # Verify that the client was created with the correct URI
        self.assertEqual(db, self.mock_db)
        
        # Verify that collections were created
        self.assertEqual(self.mock_db.create_collection.call_count, 3)
        
        # Verify that indexes were created
        self.mock_patients.create_index.assert_called_once_with('telegram_id', unique=True)
        self.mock_sessions.create_index.assert_called_once_with('patient_id')
        self.mock_reports.create_index.assert_called_once()
    
    def test_initialize_database_error(self):
        """Test database initialization error handling"""
        # Configure the mock client to raise an exception
        self.mock_client.__getitem__.side_effect = Exception("Connection error")
        
        # Call the function and verify that it raises an exception
        with self.assertRaises(Exception):
            initialize_database()

if __name__ == '__main__':
    unittest.main()