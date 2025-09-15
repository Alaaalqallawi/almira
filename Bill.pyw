#!/usr/bin/env python3
"""
Bill.pyw - Bill management application with professional print/export functionality
This serves as the reference implementation for tabular printing and PDF export.
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QLineEdit, QComboBox,
                             QMessageBox, QDialog, QDialogButtonBox,
                             QRadioButton, QButtonGroup, QFileDialog)
from PyQt5.QtCore import Qt
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
        label = QLabel("Please choose how you want to output the bill:")
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


class BillWindow(QMainWindow):
    """Main window for Bill management with professional print/export functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bill Management System")
        self.setGeometry(100, 100, 900, 600)
        
        # Sample bill data
        self.bill_data = [
            {'id': 'B001', 'date': '2024-01-15', 'account': 'Office Supplies', 
             'amount': 250.50, 'type': 'Debit', 'description': 'Stationery and office materials'},
            {'id': 'B002', 'date': '2024-01-16', 'account': 'Utilities', 
             'amount': 450.00, 'type': 'Credit', 'description': 'Electricity bill payment'},
            {'id': 'B003', 'date': '2024-01-17', 'account': 'Equipment', 
             'amount': 1200.00, 'type': 'Debit', 'description': 'Computer equipment purchase'},
            {'id': 'B004', 'date': '2024-01-18', 'account': 'Services', 
             'amount': 320.75, 'type': 'Credit', 'description': 'Professional consulting services'},
        ]
        
        self.setup_ui()
        self.populate_table()
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Bill Management System")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Table for bill data
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Bill ID', 'Date', 'Account', 'Amount', 'Type', 'Description'
        ])
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.print_button = QPushButton("Print/Export Bill")
        self.print_button.clicked.connect(self.print_export_bill)
        button_layout.addWidget(self.print_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def populate_table(self):
        """Populate the table with bill data"""
        self.table.setRowCount(len(self.bill_data))
        
        for row, bill in enumerate(self.bill_data):
            self.table.setItem(row, 0, QTableWidgetItem(bill['id']))
            self.table.setItem(row, 1, QTableWidgetItem(bill['date']))
            self.table.setItem(row, 2, QTableWidgetItem(bill['account']))
            self.table.setItem(row, 3, QTableWidgetItem(f"${bill['amount']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(bill['type']))
            self.table.setItem(row, 5, QTableWidgetItem(bill['description']))
        
        # Auto-resize columns
        self.table.resizeColumnsToContents()
    
    def print_export_bill(self):
        """Handle print/export functionality with dialog"""
        dialog = PrintExportDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            choice = dialog.get_choice()
            
            if choice == 'print':
                self.print_bill()
            else:  # PDF export
                self.export_to_pdf()
    
    def print_bill(self):
        """Print the bill using QPrinter and QTextDocument with tabular format"""
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
            
            QMessageBox.information(self, "Print Complete", "Bill has been sent to printer successfully!")
    
    def export_to_pdf(self):
        """Export bill to PDF using reportlab with tabular format"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Bill as PDF", f"bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                self.create_pdf_report(file_path)
                QMessageBox.information(self, "Export Complete", f"Bill has been exported to:\n{file_path}")
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
                }}
                tr:nth-child(even) {{ background-color: #f8f9fa; }}
                tr:nth-child(odd) {{ background-color: white; }}
                .amount {{ text-align: right; font-weight: bold; }}
                .total-row {{ background-color: #e8f5e8 !important; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Bill Management Report</h1>
            <div class="info">
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Total Records:</strong> {len(self.bill_data)}</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Bill ID</th>
                        <th>Date</th>
                        <th>Account</th>
                        <th>Amount</th>
                        <th>Type</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_amount = 0
        for bill in self.bill_data:
            amount = bill['amount']
            total_amount += amount if bill['type'] == 'Debit' else -amount
            
            html += f"""
                    <tr>
                        <td>{bill['id']}</td>
                        <td>{bill['date']}</td>
                        <td>{bill['account']}</td>
                        <td class="amount">${amount:.2f}</td>
                        <td>{bill['type']}</td>
                        <td>{bill['description']}</td>
                    </tr>
            """
        
        html += f"""
                    <tr class="total-row">
                        <td colspan="3"><strong>Net Total</strong></td>
                        <td class="amount"><strong>${total_amount:.2f}</strong></td>
                        <td colspan="2"></td>
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
        elements.append(Paragraph("Bill Management Report", title_style))
        
        # Info section
        info_style = styles['Normal']
        elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
        elements.append(Paragraph(f"<b>Total Records:</b> {len(self.bill_data)}", info_style))
        elements.append(Spacer(1, 20))
        
        # Prepare table data
        table_data = [['Bill ID', 'Date', 'Account', 'Amount', 'Type', 'Description']]
        
        total_amount = 0
        for bill in self.bill_data:
            amount = bill['amount']
            total_amount += amount if bill['type'] == 'Debit' else -amount
            
            table_data.append([
                bill['id'],
                bill['date'],
                bill['account'],
                f"${amount:.2f}",
                bill['type'],
                bill['description']
            ])
        
        # Add total row
        table_data.append([
            '', '', 'Net Total', f"${total_amount:.2f}", '', ''
        ])
        
        # Create table
        table = Table(table_data, colWidths=[1*inch, 1*inch, 1.5*inch, 1*inch, 0.8*inch, 2.2*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),  # Amount column right-aligned
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#2c3e50')),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    window = BillWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()