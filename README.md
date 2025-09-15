# Almira Invoice Management System

A professional invoice management application with enhanced print and export capabilities.

## Features

### Invoice Management (invoice.pyw)
- **Enhanced print/export system** with tabular format
- **Professional PDF export** using ReportLab with structured tables
- **Print to printer** using QTextDocument with HTML tables
- **Print/Export dialog** to choose between printing and PDF export
- **Data entry and validation** for invoice entries
- **Structured table layout** with:
  - Entry Number
  - Date
  - Account
  - Amount
  - Debit Account
  - Credit Account
  - Statement

### Bill Management (Bill.pyw)
- **Reference implementation** for professional print/export functionality
- **Consistent styling** and table format
- **Professional PDF generation** with ReportLab
- **HTML table printing** with QTextDocument

## Key Improvements

1. **Tabular Format**: Changed from plain text to structured tables for both print and PDF export
2. **Professional Styling**: Added borders, column headers, alternating row colors, and consistent formatting
3. **Print/Export Dialog**: Users can choose between printing to printer or exporting to PDF
4. **Enhanced Layout**: Invoice details are displayed in a clear, readable table format
5. **Data Validation**: Added proper validation for invoice entry data
6. **Consistent Design**: Matching styling between Bill.pyw and invoice.pyw

## Installation

```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.6+
- PyQt5 >= 5.15.0
- ReportLab >= 3.6.0

## Usage

### Running the Invoice System
```bash
python invoice.pyw
```

### Running the Bill System
```bash
python Bill.pyw
```

### Features Overview

#### Print/Export Functionality
1. Click "Print/Export Invoice" or "Print/Export Bill"
2. Choose between:
   - **Print to Printer**: Opens print dialog for direct printing
   - **Export to PDF**: Save as PDF file with professional formatting

#### Invoice Entry Management
- **Add Entry**: Create new invoice entries with validation
- **Edit Entry**: Modify existing invoice entries
- **Delete Entry**: Remove invoice entries with confirmation
- **Validation**: Ensures required fields are filled and data is valid

## Testing

Run the core functionality tests:
```bash
python test_core.py
```

This will test:
- HTML table generation for printing
- PDF generation with ReportLab
- Professional styling and formatting
- Data structure validation

## File Structure

```
almira/
├── invoice.pyw          # Main invoice management application
├── Bill.pyw             # Reference bill management application
├── requirements.txt     # Python dependencies
├── test_core.py        # Core functionality tests
├── test_invoice.py     # Full GUI tests (requires display)
└── README.md           # This file
```

## Implementation Details

### HTML Table Generation
- Uses CSS for professional styling
- Includes headers, borders, alternating row colors
- Responsive design with proper column alignment
- Total calculations and summary rows

### PDF Generation
- Uses ReportLab for high-quality PDF output
- Professional table styling with colors and borders
- Proper typography and spacing
- Header and footer information
- Consistent branding and layout

### Data Structure
Each invoice entry contains:
- `entry_number`: Unique identifier
- `date`: Entry date
- `account`: Account name
- `amount`: Monetary amount
- `debit_account`: Debit account name
- `credit_account`: Credit account name
- `statement`: Description/statement

### Validation
- Required field validation
- Amount validation (must be positive)
- Account validation (debit or credit required)
- Date format validation
- Data type validation

## Design Principles

1. **Professional Appearance**: Clean, modern styling suitable for business use
2. **User-Friendly**: Intuitive interface with clear dialogs and feedback
3. **Consistency**: Matching design between Bill.pyw and invoice.pyw
4. **Reliability**: Proper error handling and validation
5. **Flexibility**: Choice between printing and PDF export
6. **Maintainability**: Clean code structure with good separation of concerns

## Future Enhancements

Potential improvements could include:
- Database integration for persistent storage
- Advanced filtering and search capabilities
- Multiple invoice templates
- Email integration for sending PDFs
- Import/export from CSV or Excel
- Multi-language support
- Advanced reporting features