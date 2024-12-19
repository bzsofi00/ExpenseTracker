#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import csv
import matplotlib.pyplot as plt
from datetime import datetime


# In[2]:


class User:
    def __init__(self, name):
        self.name = name
        self.file = f"{name}_expenses.json"
        self.expenses = []
        self.budgets = {}
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.expenses = data.get('expenses', [])
                    self.budgets = data.get('budgets', {})
                else:
                    print(f"Invalid data format in {self.file}. Initializing with default values.")
                    self.expenses = []
                    self.budgets = {}
        except FileNotFoundError:
            self.expenses = []
            self.budgets = {}
            print(f"There is no existing data found for user: {self.name}. Starting a new list.")
        except json.JSONDecodeError:
            print(f"The JSON file is corrupted for user: {self.name}. Initializing with default values.")
            self.expenses = []
            self.budgets = {}
    
    def save_data(self):
        with open(self.file, 'w') as f:
            json.dump({'expenses': self.expenses, 'budgets': self.budgets}, f, indent=4)
            print(f"Data saved for user: {self.name}")


# In[3]:


class Expense:
    def __init__(self, amount, category, date, description):
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description
        
    def to_dict(self):
        return vars(self)


# In[4]:


class ExpenseTracker:
    def __init__(self, user):
        self.user = user
        self.allowed_categories = ["food", "transport", "entertainment", "utilities", "services", "others"]
          
    def add_expense(self):
        while True:
            try:
                amount = float(input("Enter the expense amount: "))
                if amount <= 0:
                    print("Amount should be a positive number. Please try again.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid number for the amount.")
        
        while True:
            category = input(f"Enter the expense category ({', '.join(self.allowed_categories)}): ").strip().lower()
            if category in self.allowed_categories:
                break
            else:
                print(f"Invalid category. Please choose from the allowed categories: {', '.join(self.allowed_categories)}")
                
        while True:
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today's date: ").strip()
            if not date_input:
                date = datetime.today().strftime('%Y-%m-%d')
                print(f"Date: {date}")
                break
            else:
                try:
                    date = datetime.strptime(date_input, '%Y-%m-%d').strftime('%Y-%m-%d')
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    continue

        while True:
            description = input("Enter a description of the expense: ")
            if description:
                break
            print("Description cannot be empty. Please provide some details.")
        
        while True:
            currency = input("Enter currency (DKK, EUR, HUF): ").strip().upper()
            if currency not in ["DKK", "EUR", "HUF"]:
                print("Unsupported currency. Please enter one of: DKK, EUR, HUF")
                continue

            try:
                currencies = self.convert_amounts(amount, currency)
                break
            except Exception as e:
                print(f"An error occurred during currency conversion: {e}")
                continue

        for curr, value in currencies.items():
            if curr != currency:
                print(f"Converted amount in {curr}: {value:.2f}")

        try:
            expense = Expense(amount=currencies["DKK"], category=category, date=date, description=description)
            self.user.expenses.append(expense.to_dict())
            self.user.save_data()

            print("Expense added successfully!")
            print(f"Details: Amount: {amount}, Category: {category}, Date: {date}, Description: {description}")

            self.check_budget(category, currencies["DKK"])
            
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
    def is_valid_date(self, date):
        try:
            parts = date.split('-')
            if len(parts) != 3 or len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
                return False
            return True
        except Exception:
            return False
    
    def convert_currency(self, amount, from_currency, to_currency):
            exchange_rates = {
                'DKK': {'EUR': 0.134, 'HUF': 55.0},
                'EUR': {'DKK': 1/0.13, 'HUF': 55.0/0.13},
                'HUF': {'DKK': 1/55.0, 'EUR': 1/55.0*0.13}
            }
            
            if from_currency in exchange_rates and to_currency in exchange_rates[from_currency]:
                conversion_rate = exchange_rates[from_currency][to_currency]
                return amount * conversion_rate
            else:
                print(f"Currency conversion from {from_currency} to {to_currency} is not supported.")
                return amount
         
    def convert_amounts(self, amount, currency):
        allowed_currencies = ["DKK", "EUR", "HUF"]
        conversions = {currency: amount}
        for target_currency in allowed_currencies:
            if target_currency != currency:
                conversions[target_currency] = self.convert_currency(amount, currency, target_currency)
        return conversions
    
    def check_budget(self, category, amount):
        if category in self.user.budgets:
            budget_limit = self.user.budgets[category]
            spent = sum(exp['amount'] for exp in self.user.expenses if exp['category'] == category)
            remaining = budget_limit - spent

            if spent > budget_limit:
                print(f"Over budget for {category} by DKK {spent - budget_limit:.2f}!")
            else:
                print(f"Remaining budget for {category}: DKK {remaining:.2f}")

    def view_expenses(self, expenses=None):
        if expenses is None:
            expenses = self.user.expenses
        if not expenses:
            print("There are no expenses to show.")
            return

        print("ID    | Date         | Category        | Amount         | Description")
        print("--------------------------------------------------")
        for idx, exp in enumerate(expenses, start=1):
            amount = exp.get('amount', 0)
            print(f"{idx:<5} | {exp['date']:<12} | {exp['category']:<15} | DKK {float(exp['amount']):<10.2f} | {exp['description']}")
              
    def edit_expense(self):
        self.view_expenses()

        while True:
            try:
                expense_id = int(input("Enter the expense ID of the expense you want to edit: "))
                if 1 <= expense_id <= len(self.user.expenses):
                    break
                else:
                    print("Invalid ID. Please enter a valid expense ID.")
            except ValueError:
                print("Invalid input. Please enter a valid expense ID.")

        expense = self.user.expenses[expense_id - 1]

        print("Current details of the expense:")
        print(f"Amount: {expense['amount']}, Category: {expense['category']}, Date: {expense['date']}, Description: {expense['description']}")

        new_amount = input(f"Enter the new amount (current: {expense['amount']}): ").strip()
        if new_amount:
            expense['amount'] = float(new_amount)

        new_category = input(f"Enter the new category (current: {expense['category']}): ").strip()
        if new_category:
            expense['category'] = new_category

        new_date = input(f"Enter the new date (current: {expense['date']}): ").strip()
        if new_date:
            expense['date'] = new_date

        new_description = input(f"Enter the new description (current: {expense['description']}): ").strip()
        if new_description:
            expense['description'] = new_description

        try:
            self.user.save_data()
            print("Expense updated successfully!")
        except Exception as e:
            print(f"An unexpected error occurred while saving the expense: {e}")

    def delete_expense(self):
        self.view_expenses()

        while True:
            try:
                expense_id = int(input("Enter the expense ID to delete: "))
                if 1 <= expense_id <= len(self.user.expenses):
                    break
                else:
                    print("Invalid ID. Please enter a valid expense ID.")
            except ValueError:
                print("Invalid input. Please enter a numeric expense ID.")

        try:
            del self.user.expenses[expense_id - 1]
            self.user.save_data()
            print("Expense deleted successfully!")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def sort_expenses(self):
        if not self.user.expenses:
            print("No expenses to sort.")
            return

        while True:
            print("\n--- Sort Expenses ---")
            print("2. By Expense Amount")
            print("1. By Date")
            print("3. By Category")

            try:
                choice = int(input("Choose a sorting criterion (1-3): ").strip())
                if choice == 1:
                    sorted_expenses = sorted(self.user.expenses, key=lambda exp: exp['date'])
                elif choice == 2:
                    sorted_expenses = sorted(self.user.expenses, key=lambda exp: float(exp['amount']))
                elif choice == 3:
                    sorted_expenses = sorted(self.user.expenses, key=lambda exp: exp['category'].lower())
                else:
                    print("Invalid choice. Please choose a number between 1 and 3.")
                    continue
                
                while True:
                    order = input("Enter sorting order ('asc' for ascending, 'desc' for descending): ").strip().lower()
                    if order == 'asc':
                        break
                    elif order == 'desc':
                        sorted_expenses.reverse()
                        break
                    else:
                        print("Invalid sorting order. Please enter 'asc' for ascending or 'desc' for descending.")

                print("\n--- Sorted Expenses ---")
                self.view_expenses(sorted_expenses)
                break

            except ValueError:
                print("Invalid input. Please enter a number between 1 and 3.")

    def search_expenses(self, search_term):
        search_term = search_term.strip().lower()

        while not search_term:
            print("Search term cannot be empty.")
            search_term = input("Please enter a valid search term: ").strip().lower()

        matching_expenses = [
            exp for exp in self.user.expenses
            if search_term in exp['category'].lower() or
               search_term in exp['description'].lower() or
               search_term in exp['date']
        ]

        if matching_expenses:
            print("\n--- Search Results ---")
            self.view_expenses(matching_expenses)
        else:
            print(f"No expenses found matching the term '{search_term}'.")
   
    def set_budget(self):
        while True:
            print(f"Available categories: {', '.join(self.allowed_categories)}")
            category = input("Enter category to set budget for: ").strip().lower()

            if category not in self.allowed_categories:
                print(f"Invalid category. Please choose from the available categories.")
                continue

            while True:
                try:
                    limit = input(f"Enter budget limit for {category}: ").strip()
                    if limit == "":
                        print("Budget limit cannot be empty. Please enter a valid number.")
                        continue
                    limit = float(limit)
                    if limit <= 0:
                        print("Budget limit must be a positive number. Please try again.")
                        continue
                    break
                except ValueError:
                    print("Invalid input. Budget limit must be a number. Please try again.")

            self.user.budgets[category] = limit
            self.user.save_data()
            print(f"Budget set for {category}: DKK {limit}")
            break

    def view_budget(self):
        if not self.user.budgets:
            print("\nThere are no budgets to show.")
            return
    
        print("\n--- Budget Overview ---")
        for category, limit in self.user.budgets.items():
            spent = sum(exp['amount'] for exp in self.user.expenses if exp['category'] == category)
            print(f"{category}: Budget DKK {limit} | Spent DKK {spent:.2f} | Remaining DKK {limit - spent:.2f}")
            if spent > limit:
                print(f" Over budget by DKK {spent - limit:.2f}!")
    
    def add_category(self):
        new_category = input("Enter the new category to add: ").strip().lower()
        if new_category in self.allowed_categories:
            print(f"The category '{new_category}' already exists.")
        elif new_category == "":
            print("Category name cannot be empty.")
        else:
            self.allowed_categories.append(new_category)
            print(f"Category '{new_category}' added successfully.")
    
    def generate_report(self):
        categories = {}
        for exp in self.user.expenses:
            categories[exp['category']] = categories.get(exp['category'], 0) + exp['amount']
        
        print("\n--- Expense Report by Category ---")
        for category, total in categories.items():
            print(f"{category}: DKK {total:.2f}")

    def export_data(self, file_type='csv'):
        file_name = input("Enter file name (without extension): ")
        if file_type == 'csv':
            file_name += '.csv'
            try:
                with open(file_name, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Date', 'Category', 'Amount', 'Description'])
                    for exp in self.user.expenses:
                        writer.writerow([exp['date'], exp['category'], exp['amount'], exp['description']])
                print(f"Expenses exported successfully to {file_name}")
            except Exception as e:
                print(f"Error exporting data: {e}")
        elif file_type == 'json':
            file_name += '.json'
            try:
                with open(file_name, 'w') as jsonfile:
                    json.dump(self.user.expenses, jsonfile, indent=4)
                print(f"Expenses exported successfully to {file_name}")
            except Exception as e:
                print(f"Error exporting data: {e}")
        else:
            print("Unsupported file type. Please choose 'csv' or 'json'.")

    
    def plot_category_spending(self):
        categories = {}
        for exp in self.user.expenses:
            categories[exp['category']] = categories.get(exp['category'], 0) + exp['amount']

        if categories:
            plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=90)
            plt.title("Spending by Category")
            plt.show()
        else:
            print("No expenses to visualize.")


# In[ ]:


def main_menu(tracker):
    menu_options = {
        1: "Add New Expense",
        2: "View Expenses",
        3: "Set Budget",
        4: "View Budget",
        5: "Sort Expenses",
        6: "Search Expenses",
        7: "Edit Expense",
        8: "Delete Expense",
        9: "Add New Category",
        10: "Generate Report",
        11: "Export Data",
        12: "Visualize Category Spending",
        13: "Exit"
    }

    while True:
        print("\n--- Personal Expense Tracker ---")
        for key, value in menu_options.items():
            print(f"{key}. {value}")
        
        try:
            choice = int(input("Enter your choice (1-13): "))
            if choice in menu_options:
                print(f"Your choice: {choice}. {menu_options[choice]}")
                return choice
            else:
                print("Invalid choice. Please choose a number between 1 and 13.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():
    user_name = input("Enter your name: ").strip()
    user = User(user_name)
    tracker = ExpenseTracker(user)

    while True:
        choice = main_menu(tracker)

        if choice == 1:
            tracker.add_expense()
        elif choice == 2:
            tracker.view_expenses()
        elif choice == 3:
            tracker.set_budget()
        elif choice == 4:
            tracker.view_budget()
        elif choice == 5:
            tracker.sort_expenses()
        elif choice == 6:
            search_term = input("Search for expenses by category, description, or date. Enter a search term: ")
            tracker.search_expenses(search_term)
        elif choice == 7:
            tracker.edit_expense()
        elif choice == 8:
            tracker.delete_expense()
        elif choice == 9:
            tracker.add_category()
        elif choice == 10:
            tracker.generate_report()
        elif choice == 11:
            file_type = input("Enter file type for export (csv/json): ").strip().lower()
            tracker.export_data(file_type)
        elif choice == 12:
            tracker.plot_category_spending()
        elif choice == 13:
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()


# # The program can be tested with a sample json file, that already has some expense records, to do that download "Peter_expenses.json"
# ## Use "Peter" for the name to test the existing json file, or initialize a new user with any name and start by adding a few expense records
