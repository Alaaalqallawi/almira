#!/usr/bin/env python3
"""
invoice.pyw - Invoice management application with enhanced print/export functionality
Enhanced to use tabular format similar to Bill.pyw with professional styling.
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QLineEdit, QComboBox,
                             QMessageBox, QDialog, QDialogButtonBox,
                             QRadioButton, QButtonGroup, QFileDialog,
                             QFormLayout, QDoubleSpinBox, QTextEdit, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument, QTextCursor
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch


class PrintExportDialog(QDialog):
    """Dialog to choose between printing and PDF export"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Print/Export Options")
        self.setModal(True)
        self.resize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # Add explanation label
        label = QLabel("Please choose how you want to output the invoice:")
        layout.addWidget(label)
        
        # Radio buttons for options
        self.button_group = QButtonGroup(self)
        
        self.print_radio = QRadioButton("Print to Printer")
        self.print_radio.setChecked(True)  # Default option
        self.button_group.addButton(self.print_radio)
        layout.addWidget(self.print_radio)
        
        self.pdf_radio = QRadioButton("Export to PDF")
        self.button_group.addButton(self.pdf_radio)
        layout.addWidget(self.pdf_radio)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_choice(self):
        """Returns 'print' or 'pdf' based on selection"""
        return 'print' if self.print_radio.isChecked() else 'pdf'


class InvoiceEntryDialog(QDialog):
    """Dialog for adding/editing invoice entries"""
    
    def __init__(self, parent=None, entry_data=None):
        super().__init__(parent)
        self.setWindowTitle("Invoice Entry")
        self.setModal(True)
        self.resize(400, 300)
        
        self.entry_data = entry_data or {}
        self.setup_ui()
        self.populate_fields()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Entry number
        self.entry_number = QLineEdit()
        form_layout.addRow("Entry Number:", self.entry_number)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        # Account
        self.account = QLineEdit()
        form_layout.addRow("Account:", self.account)
        
        # Amount
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.00, 999999.99)
        self.amount.setDecimals(2)
        self.amount.setSuffix(" $")
        form_layout.addRow("Amount:", self.amount)
        
        # Debit Account
        self.debit_account = QLineEdit()
        form_layout.addRow("Debit Account:", self.debit_account)
        
        # Credit Account
        self.credit_account = QLineEdit()
        form_layout.addRow("Credit Account:", self.credit_account)
        
        # Statement
        self.statement = QTextEdit()
        self.statement.setMaximumHeight(80)
        form_layout.addRow("Statement:", self.statement)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def populate_fields(self):
        """Populate fields with existing data if editing"""
        if self.entry_data:
            self.entry_number.setText(self.entry_data.get('entry_number', ''))
            date_str = self.entry_data.get('date', '')
            if date_str:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                self.date_edit.setDate(date)
            self.account.setText(self.entry_data.get('account', ''))
            self.amount.setValue(self.entry_data.get('amount', 0.0))
            self.debit_account.setText(self.entry_data.get('debit_account', ''))
            self.credit_account.setText(self.entry_data.get('credit_account', ''))
            self.statement.setPlainText(self.entry_data.get('statement', ''))
    
    def get_data(self):
        """Get the entered data"""
        return {
            'entry_number': self.entry_number.text(),
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'account': self.account.text(),
            'amount': self.amount.value(),
            'debit_account': self.debit_account.text(),
            'credit_account': self.credit_account.text(),
            'statement': self.statement.toPlainText()
        }
    
    def validate_data(self):
        """Validate the entered data"""
        data = self.get_data()
        
        if not data['entry_number'].strip():
            QMessageBox.warning(self, "Validation Error", "Entry number is required.")
            return False
        
        if not data['account'].strip():
            QMessageBox.warning(self, "Validation Error", "Account is required.")
            return False
        
        if data['amount'] <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than zero.")
            return False
        
        if not data['debit_account'].strip() and not data['credit_account'].strip():
            QMessageBox.warning(self, "Validation Error", "Either debit or credit account is required.")
            return False
        
        return True
    
    def accept(self):
        """Override accept to validate data"""
        if self.validate_data():
            super().accept()


class InvoiceWindow(QMainWindow):
    """Main window for Invoice management with enhanced print/export functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Management System")
        self.setGeometry(100, 100, 1100, 700)
        
        # Sample invoice data
        self.invoice_data = [
            {
                'entry_number': 'INV001',
                'date': '2024-01-15',
                'account': 'Sales Revenue',
                'amount': 1500.00,
                'debit_account': 'Cash',
                'credit_account': 'Sales Revenue',
                'statement': 'Sale of products to customer ABC Corp'
            },
            {
                'entry_number': 'INV002',
                'date': '2024-01-16',
                'account': 'Service Revenue',
                'amount': 750.50,
                'debit_account': 'Accounts Receivable',
                'credit_account': 'Service Revenue',
                'statement': 'Consulting services provided to XYZ Ltd'
            },
            {
                'entry_number': 'INV003',
                'date': '2024-01-17',
                'account': 'Product Sales',
                'amount': 2250.75,
                'debit_account': 'Cash',
                'credit_account': 'Product Sales',
                'statement': 'Hardware equipment sold to DEF Inc'
            },
            {
                'entry_number': 'INV004',
                'date': '2024-01-18',
                'account': 'Professional Services',
                'amount': 980.25,
                'debit_account': 'Accounts Receivable',
                'credit_account': 'Professional Services',
                'statement': 'Legal consultation and documentation services'
            },
        ]
        
        self.setup_ui()
        self.populate_table()
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Invoice Management System")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Table for invoice data
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Entry Number', 'Date', 'Account', 'Amount', 'Debit Account', 'Credit Account', 'Statement'
        ])
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Entry")
        self.add_button.clicked.connect(self.add_entry)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Entry")
        self.edit_button.clicked.connect(self.edit_entry)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete Entry")
        self.delete_button.clicked.connect(self.delete_entry)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        
        self.print_button = QPushButton("Print/Export Invoice")
        self.print_button.clicked.connect(self.print_export_invoice)
        button_layout.addWidget(self.print_button)
        
        layout.addLayout(button_layout)
        
    def populate_table(self):
        """Populate the table with invoice data"""
        self.table.setRowCount(len(self.invoice_data))
        
        for row, invoice in enumerate(self.invoice_data):
            self.table.setItem(row, 0, QTableWidgetItem(invoice['entry_number']))
            self.table.setItem(row, 1, QTableWidgetItem(invoice['date']))
            self.table.setItem(row, 2, QTableWidgetItem(invoice['account']))
            self.table.setItem(row, 3, QTableWidgetItem(f"${invoice['amount']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(invoice['debit_account']))
            self.table.setItem(row, 5, QTableWidgetItem(invoice['credit_account']))
            self.table.setItem(row, 6, QTableWidgetItem(invoice['statement']))
        
        # Auto-resize columns
        self.table.resizeColumnsToContents()
    
    def add_entry(self):
        """Add a new invoice entry"""
        dialog = InvoiceEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            self.invoice_data.append(data)
            self.populate_table()
            QMessageBox.information(self, "Success", "Invoice entry added successfully!")
    
    def edit_entry(self):
        """Edit selected invoice entry"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            entry_data = self.invoice_data[current_row]
            dialog = InvoiceEntryDialog(self, entry_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                self.invoice_data[current_row] = data
                self.populate_table()
                QMessageBox.information(self, "Success", "Invoice entry updated successfully!")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select an entry to edit.")
    
    def delete_entry(self):
        """Delete selected invoice entry"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                "Are you sure you want to delete this invoice entry?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                del self.invoice_data[current_row]
                self.populate_table()
                QMessageBox.information(self, "Success", "Invoice entry deleted successfully!")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select an entry to delete.")
    
    def print_export_invoice(self):
        """Handle print/export functionality with dialog"""
        if not self.invoice_data:
            QMessageBox.warning(self, "No Data", "No invoice data to print or export.")
            return
            
        dialog = PrintExportDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            choice = dialog.get_choice()
            
            if choice == 'print':
                self.print_invoice()
            else:  # PDF export
                self.export_to_pdf()
    
    def print_invoice(self):
        """Print the invoice using QPrinter and QTextDocument with tabular format"""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.A4)
        
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            # Create HTML content with table
            html_content = self.generate_html_table()
            
            # Create QTextDocument and set HTML content
            document = QTextDocument()
            document.setHtml(html_content)
            
            # Print the document
            document.print_(printer)
            
            QMessageBox.information(self, "Print Complete", "Invoice has been sent to printer successfully!")
    
    def export_to_pdf(self):
        """Export invoice to PDF using reportlab with tabular format"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Invoice as PDF", f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                self.create_pdf_report(file_path)
                QMessageBox.information(self, "Export Complete", f"Invoice has been exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{str(e)}")
    
    def generate_html_table(self):
        """Generate HTML content with properly formatted table"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
                .info {{ margin-bottom: 20px; }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 20px;
                    border: 2px solid #2c3e50;
                }}
                th {{ 
                    background-color: #3498db; 
                    color: white; 
                    padding: 12px; 
                    text-align: left; 
                    border: 1px solid #2c3e50;
                    font-weight: bold;
                }}
                td {{ 
                    padding: 10px; 
                    border: 1px solid #bdc3c7; 
                    text-align: left;
                    vertical-align: top;
                }}
                tr:nth-child(even) {{ background-color: #f8f9fa; }}
                tr:nth-child(odd) {{ background-color: white; }}
                .amount {{ text-align: right; font-weight: bold; }}
                .total-row {{ background-color: #e8f5e8 !important; font-weight: bold; }}
                .statement {{ max-width: 200px; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <h1>Invoice Management Report</h1>
            <div class="info">
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Total Entries:</strong> {len(self.invoice_data)}</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Entry Number</th>
                        <th>Date</th>
                        <th>Account</th>
                        <th>Amount</th>
                        <th>Debit Account</th>
                        <th>Credit Account</th>
                        <th>Statement</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_amount = 0
        for invoice in self.invoice_data:
            amount = invoice['amount']
            total_amount += amount
            
            html += f"""
                    <tr>
                        <td>{invoice['entry_number']}</td>
                        <td>{invoice['date']}</td>
                        <td>{invoice['account']}</td>
                        <td class="amount">${amount:.2f}</td>
                        <td>{invoice['debit_account']}</td>
                        <td>{invoice['credit_account']}</td>
                        <td class="statement">{invoice['statement']}</td>
                    </tr>
            """
        
        html += f"""
                    <tr class="total-row">
                        <td colspan="3"><strong>Total Amount</strong></td>
                        <td class="amount"><strong>${total_amount:.2f}</strong></td>
                        <td colspan="3"></td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        
        return html
    
    def create_pdf_report(self, file_path):
        """Create a professional PDF report using reportlab"""
        doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1,  # Center alignment
            spaceAfter=30
        )
        elements.append(Paragraph("Invoice Management Report", title_style))
        
        # Info section
        info_style = styles['Normal']
        elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
        elements.append(Paragraph(f"<b>Total Entries:</b> {len(self.invoice_data)}", info_style))
        elements.append(Spacer(1, 20))
        
        # Prepare table data
        table_data = [['Entry Number', 'Date', 'Account', 'Amount', 'Debit Account', 'Credit Account', 'Statement']]
        
        total_amount = 0
        for invoice in self.invoice_data:
            amount = invoice['amount']
            total_amount += amount
            
            # Wrap statement text if too long
            statement = invoice['statement']
            if len(statement) > 40:
                statement = statement[:37] + "..."
            
            table_data.append([
                invoice['entry_number'],
                invoice['date'],
                invoice['account'],
                f"${amount:.2f}",
                invoice['debit_account'],
                invoice['credit_account'],
                statement
            ])
        
        # Add total row
        table_data.append([
            '', '', 'Total Amount', f"${total_amount:.2f}", '', '', ''
        ])
        
        # Create table
        table = Table(table_data, colWidths=[0.8*inch, 0.8*inch, 1.2*inch, 0.8*inch, 1.0*inch, 1.0*inch, 1.9*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),  # Amount column right-aligned
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
            ('VALIGN', (0, 1), (-1, -2), 'TOP'),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 9),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#2c3e50')),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    window = InvoiceWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()