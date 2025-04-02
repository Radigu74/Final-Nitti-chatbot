import csv
import os

def save_user_data(email, phone, postal_code, country):
    """
    Saves the user details into a CSV file called 'user_logs.csv'.
    If it doesn't exist, we create it; if it does, we append a new row.
    """
    file_exists = os.path.isfile('user_logs.csv')
    with open('user_logs.csv', mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['email', 'phone', 'postal_code', 'country']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            # Write the header only if the file doesn't exist
            writer.writeheader()

        # Write the actual user data
        writer.writerow({
            'email': email,
            'phone': phone,
            'postal_code': postal_code,
            'country': country
        })
