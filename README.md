# Personal Expense Tracker
<br> 

This is valid only for Desktop
<br> 

A simple **Python-based Personal Expense Tracker** that helps users
record and manage their income and expenses from a menu-driven console
application.

## Project Description

The Personal Expense Tracker is designed to make basic personal money
management easier. Users can add income and expenses, view transactions,
search for a transaction, calculate total income and expenses, check the
current balance, delete transactions, and save or load transaction data.

The project uses **JSON file handling** to store transaction data so
that saved records can be loaded again later.

## Features

-   Add Income
-   Add Expenses
-   View All Transactions
-   Search Transaction
-   Show Total Income
-   Show Total Expenses
-   Show Current Balance
-   Show Expenses
-   Delete Transaction
-   Save Data
-   Load Data
-   Exit the application

## Main Menu

``` text
====================================
      Personal Expense Tracker
====================================

1. Add Income
2. Add Expenses
3. View All Transactions
4. Search Transaction
5. Show Total Income
6. Show Total Expenses
7. Show Current Balance
8. Show Expenses
9. Delete Transaction
10. Save Data
11. Load Data
12. Exit
```

## Technologies Used

-   **Python**
-   **JSON**
-   File Handling
-   Lists and Dictionaries
-   Loops
-   Conditional Statements
-   Exception Handling
-   Date Handling

## Frontend / UI Design

The project's frontend/UI design was created with assistance from **Claude AI**. Claude AI was used to help design and improve the user interface, layout, and overall presentation of the application.

The core application logic and functionality are implemented in **Python**.

## Balance Calculation

The current balance is calculated using:

``` text
Current Balance = Total Income - Total Expenses
```

## Data Storage

Transaction data is stored in a JSON file. The application can save
existing transactions and load them when required.

A transaction may contain information such as:

-   Transaction ID
-   Amount
-   Source/Category
-   Date
-   Description

## How to Run

1.  Install Python 3.x.
2.  Clone or download this repository.
3.  Open the project folder in VS Code or a terminal.
4.  Run:

``` bash
python main.py
```

## Project Structure

``` text
Personal-Expense-Tracker/
│
├── main.py
├── README.md
└── .gitignore
```

## Future Improvements

Possible future improvements include:

-   Monthly expense reports
-   Expense categories
-   Graphs and charts
-   Budget limits
-   Export to CSV or Excel
-   A graphical user interface (GUI)
-   Database support

## Author

**Mohit Kumar Yadav**

## License

This project is created for learning and educational purposes.
