#!/usr/bin/env python3
"""
test_invoice.py - Test script for invoice functionality
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
import tempfile

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    
    # Import our modules
    import invoice
    import Bill
    
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    print("PyQt5 not available - skipping GUI tests")


class TestInvoiceFunctionality(unittest.TestCase):
    """Test cases for invoice functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if QT_AVAILABLE:
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication([])
    
    def test_invoice_data_structure(self):
        """Test that invoice data has the correct structure"""
        if not QT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        window = invoice.InvoiceWindow()
        
        # Check that we have sample data
        self.assertGreater(len(window.invoice_data), 0)
        
        # Check data structure
        for entry in window.invoice_data:
            self.assertIn('entry_number', entry)
            self.assertIn('date', entry)
            self.assertIn('account', entry)
            self.assertIn('amount', entry)
            self.assertIn('debit_account', entry)
            self.assertIn('credit_account', entry)
            self.assertIn('statement', entry)
            
            # Check data types
            self.assertIsInstance(entry['entry_number'], str)
            self.assertIsInstance(entry['date'], str)
            self.assertIsInstance(entry['account'], str)
            self.assertIsInstance(entry['amount'], (int, float))
            self.assertIsInstance(entry['debit_account'], str)
            self.assertIsInstance(entry['credit_account'], str)
            self.assertIsInstance(entry['statement'], str)
    
    def test_html_generation(self):
        """Test HTML table generation for printing"""
        if not QT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        window = invoice.InvoiceWindow()
        html = window.generate_html_table()
        
        # Check that HTML contains required elements
        self.assertIn('<table>', html)
        self.assertIn('<thead>', html)
        self.assertIn('<tbody>', html)
        self.assertIn('Entry Number', html)
        self.assertIn('Date', html)
        self.assertIn('Account', html)
        self.assertIn('Amount', html)
        self.assertIn('Debit Account', html)
        self.assertIn('Credit Account', html)
        self.assertIn('Statement', html)
        
        # Check for styling
        self.assertIn('background-color', html)
        self.assertIn('border-collapse', html)
        self.assertIn('padding', html)
    
    def test_pdf_creation(self):
        """Test PDF creation functionality"""
        if not QT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        window = invoice.InvoiceWindow()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Try to create PDF
            window.create_pdf_report(tmp_path)
            
            # Check that file was created and has content
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 0)
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_bill_data_structure(self):
        """Test that bill data has the correct structure"""
        if not QT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        window = Bill.BillWindow()
        
        # Check that we have sample data
        self.assertGreater(len(window.bill_data), 0)
        
        # Check data structure
        for entry in window.bill_data:
            self.assertIn('id', entry)
            self.assertIn('date', entry)
            self.assertIn('account', entry)
            self.assertIn('amount', entry)
            self.assertIn('type', entry)
            self.assertIn('description', entry)
    
    def test_print_export_dialog(self):
        """Test the print/export dialog"""
        if not QT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        dialog = invoice.PrintExportDialog()
        
        # Test default selection
        self.assertEqual(dialog.get_choice(), 'print')
        
        # Test PDF selection
        dialog.pdf_radio.setChecked(True)
        self.assertEqual(dialog.get_choice(), 'pdf')
    
    def test_invoice_entry_dialog(self):
        """Test the invoice entry dialog"""
        if not QT_AVAILABLE:
            self.skipTest("PyQt5 not available")
            
        dialog = invoice.InvoiceEntryDialog()
        
        # Test validation with empty data
        self.assertFalse(dialog.validate_data())
        
        # Test with valid data
        dialog.entry_number.setText("TEST001")
        dialog.account.setText("Test Account")
        dialog.amount.setValue(100.0)
        dialog.debit_account.setText("Cash")
        dialog.credit_account.setText("Revenue")
        dialog.statement.setPlainText("Test statement")
        
        self.assertTrue(dialog.validate_data())
        
        # Test get_data
        data = dialog.get_data()
        self.assertEqual(data['entry_number'], "TEST001")
        self.assertEqual(data['account'], "Test Account")
        self.assertEqual(data['amount'], 100.0)


def run_tests():
    """Run all tests"""
    if not QT_AVAILABLE:
        print("Warning: PyQt5 not available. Install requirements to run all tests.")
        print("To install: pip install -r requirements.txt")
        return False
    
    unittest.main(verbosity=2)
    return True


if __name__ == "__main__":
    run_tests()