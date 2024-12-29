#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import re
from datetime import datetime

# File path to the CSV file
file_path = "SMS-Data.csv"

# Load the CSV file
sms_data = pd.read_csv(file_path)

# Ensure the 'text' column contains strings
sms_data['text'] = sms_data['text'].fillna('').astype(str)

# Function to classify transaction types and extract details
def analyze_transaction(text):
    # Initialize details
    transaction_type = None
    platform = None
    payment_method = None
    
    # Extended keywords for debit and credit transactions
    debit_keywords = r'\b(paid|charged|debited|processed|withdrawn|deducted|spent|transferred|EMI|settled|fee|disbursed|purchase)\b'
    credit_keywords = r'\b(credited|received|refunded|reversed|deposited|added|reimbursed|awarded|bonus|loan approved|cashback|interest earned|payment received|gift)\b'
    spam_credit_keywords = r'\b(offer|avail|bonus|gift|win|reward|prize|lucky|exclusive|limited time|contest|promotion|claim|free|discount|unsecured loan|reward points|cashback|cash reward|surprise gift|redeem|voucher|free gift|congratulations|instant credit|loan sanctioned|apply now|eligibility)\b'

    # Classify transaction type
    if re.search(debit_keywords, text, re.IGNORECASE):
        transaction_type = "Paid/Debited"
    elif re.search(credit_keywords, text, re.IGNORECASE):
        transaction_type = "Credited"

    # Extract platform or service (e.g., Zomato)
    platform_match = re.search(r'on\s([\w\s]+?)\s(charged|paid|via)', text, re.IGNORECASE)
    if platform_match:
        platform = platform_match.group(1).strip()

    # Extract payment method (e.g., Simpl Pay)
    payment_method_match = re.search(r'via\s([\w\s]+)', text, re.IGNORECASE)
    if payment_method_match:
        payment_method = payment_method_match.group(1).strip()

    return transaction_type, platform, payment_method

# Apply the function to extract transaction details
sms_data[['transaction_type', 'platform', 'payment_method']] = sms_data['text'].apply(
    lambda x: pd.Series(analyze_transaction(x))
)

# Extract monetary amounts
def extract_amount(text):
    # Regex to extract Rs. or ₹ amounts
    amounts = re.findall(r'(₹|Rs\.?)\s?(\d+[.,]?\d*)', text)
    if amounts:
        # Check if the extracted number is realistic (e.g., not a phone number)
        amount = float(amounts[0][1].replace(',', ''))
        if amount > 1:  # Ensure the amount is a reasonable value (not a phone number or random digits)
            return amount
    return None

sms_data['amount'] = sms_data['text'].apply(extract_amount)

# Remove rows without a transaction type or valid amount
sms_data = sms_data[sms_data['transaction_type'].notnull() & sms_data['amount'].notnull()]

# Create Debited and Credited columns
sms_data['debited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Paid/Debited', 0)
sms_data['credited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Credited', 0)

# Calculate total amount (Debited + Credited)
sms_data['total_amount'] = sms_data['debited_amount'] + sms_data['credited_amount']

# Extract day, month, year, and time from the 'updatedAt' column
sms_data['day'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.day
sms_data['month'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.month
sms_data['year'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.year
sms_data['time'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.time

# Drop the updatedAt column as it's no longer needed
sms_data.drop(columns=['updateAt'], inplace=True)

# Save the updated CSV file
output_path = 'Reports.csv'
sms_data.to_csv(output_path, index=False)

print(f"Updated transaction reports saved to {output_path}")


# In[4]:


# import pandas as pd
# import re
# from datetime import datetime

# # File path to the CSV file
# file_path = "SMS-Data.csv"

# # Load the CSV file
# sms_data = pd.read_csv(file_path)

# # Ensure the 'text' column contains strings
# sms_data['text'] = sms_data['text'].fillna('').astype(str)

# # Function to classify transaction types and extract details (with spam filtering)
# def analyze_transaction(text):
#     # Initialize details
#     transaction_type = None
#     platform = None
#     payment_method = None
    
#     # Extended keywords for debit and credit transactions
#     debit_keywords = r'\b(paid|charged|debited|processed|withdrawn|deducted|spent|transferred|EMI|settled|fee|disbursed|purchase)\b'
#     credit_keywords = r'\b(credited|received|deposited|payment received|added|reimbursed|loan approved|refund|payment)\b'
    
#     # Spam detection keywords (to filter out fraud/lottery related messages)
#     spam_keywords = r'\b(gift|bonus|lottery|win|reward|promotional|offer)\b'
    
#     # Classify transaction type
#     if re.search(debit_keywords, text, re.IGNORECASE):
#         transaction_type = "Paid/Debited"
#     elif re.search(credit_keywords, text, re.IGNORECASE):
#         # If spam-related keywords are found, consider this a potential spam message
#         if re.search(spam_keywords, text, re.IGNORECASE):
#             return None, None, None  # Filter out the message
        
#         transaction_type = "Credited"

#     # Extract platform or service (e.g., Zomato, GPay, Bank)
#     platform_match = re.search(r'on\s([\w\s]+?)\s(charged|paid|via|transfer)', text, re.IGNORECASE)
#     if platform_match:
#         platform = platform_match.group(1).strip()

#     # Extract payment method (e.g., Simpl Pay, UPI via GPay)
#     payment_method_match = re.search(r'via\s([\w\s]+)', text, re.IGNORECASE)
#     if payment_method_match:
#         payment_method = payment_method_match.group(1).strip()

#     # Further validation for UPI or bank account mentions
#     if 'UPI' in text or 'bank' in text or 'A/c no' in text or 'XXXX' in text:
#         return transaction_type, platform, payment_method

#     return None, None, None  # Filter out if it doesn't mention a valid platform like UPI or bank

# # Apply the function to extract transaction details
# sms_data[['transaction_type', 'platform', 'payment_method']] = sms_data['text'].apply(
#     lambda x: pd.Series(analyze_transaction(x))
# )

# # Extract monetary amounts
# def extract_amount(text):
#     # Regex to extract Rs. or ₹ amounts
#     amounts = re.findall(r'(₹|Rs\.?)\s?(\d+[.,]?\d*)', text)
#     if amounts:
#         # Check if the extracted number is realistic (e.g., not a phone number)
#         amount = float(amounts[0][1].replace(',', ''))
#         if amount > 1:  # Ensure the amount is a reasonable value (not a phone number or random digits)
#             return amount
#     return None

# sms_data['amount'] = sms_data['text'].apply(extract_amount)

# # Remove rows without a transaction type or valid amount
# sms_data = sms_data[sms_data['transaction_type'].notnull() & sms_data['amount'].notnull()]

# # Filter only credits and legitimate transactions
# sms_data = sms_data[sms_data['transaction_type'] == 'Credited']

# # Create Debited and Credited columns
# sms_data['debited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Paid/Debited', 0)
# sms_data['credited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Credited', 0)

# # Calculate total amount (Credited)
# sms_data['total_amount'] = sms_data['credited_amount']

# # Extract day, month, year, and time from the 'updateAt' column
# sms_data['day'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.day
# sms_data['month'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.month
# sms_data['year'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.year
# sms_data['time'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.time

# # Drop the updatedAt column as it's no longer needed
# sms_data.drop(columns=['updateAt'], inplace=True)

# # Save the filtered financial credit report to a new CSV file
# output_path = 'Financial_Credit_Report.csv'
# sms_data.to_csv(output_path, index=False)

# print(f"Updated financial credit report saved to {output_path}")


# In[5]:


# import pandas as pd
# import re
# from datetime import datetime

# # File path to the CSV file
# file_path = "SMS-Data.csv"

# # Load the CSV file
# sms_data = pd.read_csv(file_path)

# # Ensure the 'text' column contains strings
# sms_data['text'] = sms_data['text'].fillna('').astype(str)

# # Function to classify transaction types and extract details
# def analyze_transaction(text):
#     # Initialize details
#     transaction_type = None
#     platform = None
#     payment_method = None
    
#     # Extended keywords for debit and credit transactions
#     debit_keywords = r'\b(paid|charged|debited|processed|withdrawn|deducted|spent|transferred|EMI|settled|fee|disbursed|purchase)\b'
#     credit_keywords = r'\b(credited|received|deposited|payment received|added|reimbursed|loan approved|refund|payment)\b'
#     spam_credit_keywords = r'\b(offer|avail|bonus|gift|win|reward|prize|lucky|exclusive|limited time|contest|promotion|claim|free|discount|unsecured loan|reward points|cashback|cash reward|surprise gift|redeem|voucher|free gift|congratulations|instant credit|loan sanctioned|apply now|eligibility)\b'

#     # Classify transaction type
#     if re.search(debit_keywords, text, re.IGNORECASE):
#         transaction_type = "Paid/Debited"
#     elif re.search(credit_keywords, text, re.IGNORECASE):
#         transaction_type = "Credited"

#     # Extract platform or service (e.g., Zomato, GPay, Bank)
#     platform_match = re.search(r'on\s([\w\s]+?)\s(charged|paid|via|transfer)', text, re.IGNORECASE)
#     if platform_match:
#         platform = platform_match.group(1).strip()

#     # Extract payment method (e.g., Simpl Pay, UPI via GPay)
#     payment_method_match = re.search(r'via\s([\w\s]+)', text, re.IGNORECASE)
#     if payment_method_match:
#         payment_method = payment_method_match.group(1).strip()

#     return transaction_type, platform, payment_method

# # Apply the function to extract transaction details
# sms_data[['transaction_type', 'platform', 'payment_method']] = sms_data['text'].apply(
#     lambda x: pd.Series(analyze_transaction(x))
# )

# # Extract monetary amounts
# def extract_amount(text):
#     # Regex to extract Rs. or ₹ amounts
#     amounts = re.findall(r'(₹|Rs\.?)\s?(\d+[.,]?\d*)', text)
#     if amounts:
#         # Check if the extracted number is realistic (e.g., not a phone number)
#         amount = float(amounts[0][1].replace(',', ''))
#         if amount > 1:  # Ensure the amount is a reasonable value (not a phone number or random digits)
#             return amount
#     return None

# sms_data['amount'] = sms_data['text'].apply(extract_amount)

# # Remove rows without a transaction type or valid amount
# sms_data = sms_data[sms_data['transaction_type'].notnull() & sms_data['amount'].notnull()]

# # Additional level of filtering for legitimate credit transactions (bank/UPI only)
# def is_legitimate_credit(row):
#     # Check if the transaction is a valid credit
#     if row['transaction_type'] == 'Credited':
#         # Look for mentions of bank/UPI in the platform or payment method
#         if re.search(r'(bank|UPI|A/c no|XXXX)', str(row['platform']), re.IGNORECASE) or re.search(r'(UPI|GPay|PhonePe|Paytm)', str(row['payment_method']), re.IGNORECASE):
#             return True
#     return False

# # Apply the filter for legitimate credits
# sms_data = sms_data[sms_data.apply(is_legitimate_credit, axis=1)]

# # Create Debited and Credited columns
# sms_data['debited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Paid/Debited', 0)
# sms_data['credited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Credited', 0)

# # Calculate total amount (Debited + Credited)
# sms_data['total_amount'] = sms_data['debited_amount'] + sms_data['credited_amount']

# # Extract day, month, year, and time from the 'updateAt' column
# sms_data['day'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.day
# sms_data['month'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.month
# sms_data['year'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.year
# sms_data['time'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.time

# # Drop the updatedAt column as it's no longer needed
# sms_data.drop(columns=['updateAt'], inplace=True)

# # Save the filtered financial credit report to a new CSV file
# output_path = 'Filtered_Financial_Credit_Report2.csv'
# sms_data.to_csv(output_path, index=False)

# print(f"Filtered financial credit report saved to {output_path}")


# In[6]:


import pandas as pd
import re
from datetime import datetime

# File path to the CSV file
file_path = "SMS-Data.csv"

# Load the CSV file
sms_data = pd.read_csv(file_path)

# Ensure the 'text' column contains strings
sms_data['text'] = sms_data['text'].fillna('').astype(str)

# Function to classify transaction types and extract details
def analyze_transaction(text):
    # Initialize details
    transaction_type = None
    platform = None
    payment_method = None
    
    # Extended keywords for debit and credit transactions
    debit_keywords = r'\b(paid|charged|debited|processed|withdrawn|deducted|spent|transferred|EMI|settled|fee|disbursed|purchase)\b'
    credit_keywords = r'\b(credited|received|refunded|reversed|deposited|added|reimbursed|awarded|bonus|loan approved|cashback|interest earned|payment received|gift)\b'
    spam_credit_keywords = r'\b(offer|avail|bonus|gift|win|reward|prize|lucky|exclusive|limited time|contest|promotion|claim|free|discount|unsecured loan|reward points|cashback|cash reward|surprise gift|redeem|voucher|free gift|congratulations|instant credit|loan sanctioned|apply now|eligibility)\b'

    # Classify transaction type
    if re.search(debit_keywords, text, re.IGNORECASE):
        transaction_type = "Paid/Debited"
    elif re.search(credit_keywords, text, re.IGNORECASE):
        transaction_type = "Credited"

    # Extract platform or service (e.g., Zomato)
    platform_match = re.search(r'on\s([\w\s]+?)\s(charged|paid|via)', text, re.IGNORECASE)
    if platform_match:
        platform = platform_match.group(1).strip()

    # Extract payment method (e.g., Simpl Pay)
    payment_method_match = re.search(r'via\s([\w\s]+)', text, re.IGNORECASE)
    if payment_method_match:
        payment_method = payment_method_match.group(1).strip()

    return transaction_type, platform, payment_method

# Apply the function to extract transaction details
sms_data[['transaction_type', 'platform', 'payment_method']] = sms_data['text'].apply(
    lambda x: pd.Series(analyze_transaction(x))
)

# Extract monetary amounts
def extract_amount(text):
    # Regex to extract Rs. or ₹ amounts
    amounts = re.findall(r'(₹|Rs\.?)\s?(\d+[.,]?\d*)', text)
    if amounts:
        # Check if the extracted number is realistic (e.g., not a phone number)
        amount = float(amounts[0][1].replace(',', ''))
        if amount > 1:  # Ensure the amount is a reasonable value (not a phone number or random digits)
            return amount
    return None

sms_data['amount'] = sms_data['text'].apply(extract_amount)

# Remove rows without a transaction type or valid amount
sms_data = sms_data[sms_data['transaction_type'].notnull() & sms_data['amount'].notnull()]

# Create Debited and Credited columns
sms_data['debited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Paid/Debited', 0)
sms_data['credited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Credited', 0)

# Calculate total amount (Debited + Credited)
sms_data['total_amount'] = sms_data['debited_amount'] + sms_data['credited_amount']

# Extract day, month, year, and time from the 'updatedAt' column
sms_data['day'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.day
sms_data['month'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.month
sms_data['year'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.year
sms_data['time'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.time

# Drop the updatedAt column as it's no longer needed
sms_data.drop(columns=['updateAt'], inplace=True)

# Function to check if the credit message is a spam
def is_spam_credit(text):
    # Regex to check for spam credit keywords
    spam_keywords = r'\b(offer|avail|bonus|gift|win|reward|prize|lucky|exclusive|limited time|contest|promotion|claim|free|discount|unsecured loan|reward points|cashback|cash reward|surprise gift|redeem|voucher|free gift|congratulations|instant credit|loan sanctioned|apply now|eligibility)\b'
    if re.search(spam_keywords, text, re.IGNORECASE):
        return True
    return False

# Determine final credit status based on spam detection
sms_data['final_credit'] = sms_data.apply(
    lambda row: False if row['transaction_type'] == 'Credited' and is_spam_credit(row['text']) else True,
    axis=1
)

# Save the updated CSV file
output_path = 'Reports_with_final_credit3.csv'
sms_data.to_csv(output_path, index=False)

print(f"Updated transaction reports saved to {output_path}")


# In[9]:


import pandas as pd
import re
from datetime import datetime

# File path to the CSV file
file_path = "SMS-Data.csv"

# Load the CSV file
sms_data = pd.read_csv(file_path)

# Ensure the 'text' column contains strings
sms_data['text'] = sms_data['text'].fillna('').astype(str)
sms_data['senderAddress'] = sms_data['senderAddress'].fillna('').astype(str)

# List of known banks (Example - you can expand this list)
bank_list = ['HDFC', 'ICICI', 'SBI', 'Axis Bank', 'PNB', 'Bank of India', 'Kotak Mahindra', 'IDFC Bank', 'Yes Bank', 'IndusInd Bank', 'RBL Bank']

# Function to classify transaction types and extract details
def analyze_transaction(text):
    # Initialize details
    transaction_type = None
    platform = None
    payment_method = None
    
    # Extended keywords for debit and credit transactions
    debit_keywords = r'\b(paid|charged|debited|processed|withdrawn|deducted|spent|transferred|EMI|settled|fee|disbursed|purchase)\b'
    credit_keywords = r'\b(credited|received|refunded|reversed|deposited|added|reimbursed|awarded|bonus|loan approved|cashback|interest earned|payment received|gift)\b'
    spam_credit_keywords = r'\b(offer|avail|bonus|gift|win|reward|prize|lucky|exclusive|limited time|contest|promotion|claim|free|discount|unsecured loan|reward points|cashback|cash reward|surprise gift|redeem|voucher|free gift|congratulations|instant credit|loan sanctioned|apply now|eligibility)\b'

    # Classify transaction type
    if re.search(debit_keywords, text, re.IGNORECASE):
        transaction_type = "Paid/Debited"
    elif re.search(credit_keywords, text, re.IGNORECASE):
        transaction_type = "Credited"

    # Extract platform or service (e.g., Zomato, HDFC, etc.)
    platform_match = re.search(r'(from|on)\s([\w\s]+?)\s(credited|charged|paid|via)', text, re.IGNORECASE)
    if platform_match:
        platform = platform_match.group(2).strip()

    # Extract payment method (e.g., Simpl Pay)
    payment_method_match = re.search(r'via\s([\w\s]+)', text, re.IGNORECASE)
    if payment_method_match:
        payment_method = payment_method_match.group(1).strip()

    return transaction_type, platform, payment_method

# Apply the function to extract transaction details
sms_data[['transaction_type', 'platform', 'payment_method']] = sms_data['text'].apply(
    lambda x: pd.Series(analyze_transaction(x))
)

# Extract monetary amounts
def extract_amount(text):
    # Regex to extract Rs. or ₹ amounts
    amounts = re.findall(r'(₹|Rs\.?)\s?(\d+[.,]?\d*)', text)
    if amounts:
        # Check if the extracted number is realistic (e.g., not a phone number)
        amount = float(amounts[0][1].replace(',', ''))
        if amount > 1:  # Ensure the amount is a reasonable value (not a phone number or random digits)
            return amount
    return None

sms_data['amount'] = sms_data['text'].apply(extract_amount)

# Remove rows without a transaction type or valid amount
sms_data = sms_data[sms_data['transaction_type'].notnull() & sms_data['amount'].notnull()]

# Create Debited and Credited columns
sms_data['debited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Paid/Debited', 0)
sms_data['credited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Credited', 0)

# Calculate total amount (Debited + Credited)
sms_data['total_amount'] = sms_data['debited_amount'] + sms_data['credited_amount']

# Extract day, month, year, and time from the 'updatedAt' column
sms_data['day'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.day
sms_data['month'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.month
sms_data['year'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.year
sms_data['time'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.time

# Drop the updatedAt column as it's no longer needed
sms_data.drop(columns=['updateAt'], inplace=True)

# Function to check if the credit message is a spam
def is_spam_credit(text):
    # Regex to check for spam credit keywords
    spam_keywords = r'\b(offer|avail|bonus|gift|win|reward|prize|lucky|exclusive|limited time|contest|promotion|claim|free|discount|unsecured loan|reward points|cashback|cash reward|surprise gift|redeem|voucher|free gift|congratulations|instant credit|loan sanctioned|apply now|eligibility)\b'
    if re.search(spam_keywords, text, re.IGNORECASE):
        return True
    return False

# Determine final credit status based on spam detection
sms_data['final_credit'] = sms_data.apply(
    lambda row: False if row['transaction_type'] == 'Credited' and is_spam_credit(row['text']) else True,
    axis=1
)

# Function to check if platform is a bank
def is_bank(platform):
    if platform:
        # Check if the platform contains any bank name
        for bank in bank_list:
            if bank.lower() in platform.lower():
                return True
    return False

# Create a new column 'platform_is_bank' that checks if the platform is a bank
sms_data['platform_is_bank'] = sms_data['senderAddress'].apply(is_bank)

# Save the updated CSV file
output_path = 'Reports_with_platform_check5.csv'
sms_data.to_csv(output_path, index=False)

print(f"Updated transaction reports saved to {output_path}")


# In[10]:


import pandas as pd
import re
from datetime import datetime

# File path to the CSV file
file_path = "SMS-Data.csv"

# Load the CSV file
sms_data = pd.read_csv(file_path)

# Ensure the 'text' column contains strings
sms_data['text'] = sms_data['text'].fillna('').astype(str)
sms_data['senderAddress'] = sms_data['senderAddress'].fillna('').astype(str)

# List of known banks (Example - you can expand this list)
bank_list = ['HDFC', 'ICICI', 'SBI', 'Axis Bank', 'PNB', 'Bank of India', 'Kotak Mahindra', 'IDFC Bank', 'Yes Bank', 'IndusInd Bank', 'RBL Bank']

# Function to classify transaction types and extract details
def analyze_transaction(text):
    # Initialize details
    transaction_type = None
    platform = None
    payment_method = None
    
    # Extended keywords for debit and credit transactions
    debit_keywords = r'\b(paid|charged|debited|processed|withdrawn|deducted|spent|transferred|EMI|settled|fee|disbursed|purchase)\b'
    credit_keywords = r'\b(credited|received|refunded|reversed|deposited|added|reimbursed|awarded|bonus|loan approved|cashback|interest earned|payment received|gift)\b'
    spam_credit_keywords = r'\b(offer|avail|bonus|gift|win|reward|prize|lucky|exclusive|limited time|contest|promotion|claim|free|discount|unsecured loan|reward points|cashback|cash reward|surprise gift|redeem|voucher|free gift|congratulations|instant credit|loan sanctioned|apply now|eligibility)\b'

    # Classify transaction type
    if re.search(debit_keywords, text, re.IGNORECASE):
        transaction_type = "Paid/Debited"
    elif re.search(credit_keywords, text, re.IGNORECASE):
        transaction_type = "Credited"

    # Extract platform or service (e.g., Zomato, HDFC, etc.)
    platform_match = re.search(r'(from|on)\s([\w\s]+?)\s(credited|charged|paid|via)', text, re.IGNORECASE)
    if platform_match:
        platform = platform_match.group(2).strip()

    # Extract payment method (e.g., Simpl Pay)
    payment_method_match = re.search(r'via\s([\w\s]+)', text, re.IGNORECASE)
    if payment_method_match:
        payment_method = payment_method_match.group(1).strip()

    return transaction_type, platform, payment_method

# Apply the function to extract transaction details
sms_data[['transaction_type', 'platform', 'payment_method']] = sms_data['text'].apply(
    lambda x: pd.Series(analyze_transaction(x))
)

# Extract monetary amounts
def extract_amount(text):
    # Regex to extract Rs. or ₹ amounts
    amounts = re.findall(r'(₹|Rs\.?)\s?(\d+[.,]?\d*)', text)
    if amounts:
        # Check if the extracted number is realistic (e.g., not a phone number)
        amount = float(amounts[0][1].replace(',', ''))
        if amount > 1:  # Ensure the amount is a reasonable value (not a phone number or random digits)
            return amount
    return None

sms_data['amount'] = sms_data['text'].apply(extract_amount)

# Remove rows without a transaction type or valid amount
sms_data = sms_data[sms_data['transaction_type'].notnull() & sms_data['amount'].notnull()]

# Create Debited and Credited columns
sms_data['debited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Paid/Debited', 0)
sms_data['credited_amount'] = sms_data['amount'].where(sms_data['transaction_type'] == 'Credited', 0)

# Calculate total amount (Debited + Credited)
sms_data['total_amount'] = sms_data['debited_amount'] + sms_data['credited_amount']

# Extract day, month, year, and time from the 'updatedAt' column
sms_data['day'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.day
sms_data['month'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.month
sms_data['year'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.year
sms_data['time'] = pd.to_datetime(sms_data['updateAt'], format='%a, %d %b %Y %H:%M:%S %Z').dt.time

# Drop the updatedAt column as it's no longer needed
sms_data.drop(columns=['updateAt'], inplace=True)

# Function to check if the credit message is a spam
def is_spam_credit(text):
    # Regex to check for spam credit keywords
    spam_keywords = r'\b(offer|avail|bonus|gift|win|reward|prize|lucky|exclusive|limited time|contest|promotion|claim|free|discount|unsecured loan|reward points|cashback|cash reward|surprise gift|redeem|voucher|free gift|congratulations|instant credit|loan sanctioned|apply now|eligibility)\b'
    if re.search(spam_keywords, text, re.IGNORECASE):
        return True
    return False

# Determine final credit status based on spam detection
sms_data['final_credit'] = sms_data.apply(
    lambda row: False if row['transaction_type'] == 'Credited' and is_spam_credit(row['text']) else True,
    axis=1
)

# Function to check if platform is a bank
def is_bank(platform):
    if platform:
        # Check if the platform contains any bank name
        for bank in bank_list:
            if bank.lower() in platform.lower():
                return True
    return False

# Create a new column 'platform_is_bank' that checks if the platform is a bank
sms_data['platform_is_bank'] = sms_data['senderAddress'].apply(is_bank)

# Update platform column based on platform_is_bank value
def update_platform(row):
    if row['platform_is_bank']:
        # If it's a bank, add bank-related information
        row['platform'] = f"{row['platform']} Bank Account" if row['platform'] else "Bank Account"
    else:
        # If it's not a bank, extract the main component of senderAddress
        sender_address_parts = row['senderAddress'].split(' ')
        row['platform'] = sender_address_parts[0] if sender_address_parts else row['platform']
    return row

# Apply the update_platform function to update the platform column
sms_data = sms_data.apply(update_platform, axis=1)

# Save the updated CSV file
output_path = 'Reports_with_updated_platform6.csv'
sms_data.to_csv(output_path, index=False)

print(f"Updated transaction reports saved to {output_path}")


# In[ ]:




