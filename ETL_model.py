import pandas as pd
import sqlite3

# we will use pandas library to read the excel and convert them into data frames
def extract_data(file_path):
    try:
        data = pd.read_excel(file_path, engine='openpyxl')
        return data
    except Exception as e:
        print("Error reading",file_path,e)
        return None

# Paths to the files
file_a = 'order_region_a.xlsx'
file_b = 'order_region_b.xlsx'

# Extract data
data_a = extract_data(file_a)
data_b = extract_data(file_b)

# Display the first few rows to verify extraction
print(data_a.head())
print(data_b.head())

# we will transform the data as per the business rules that is we will add the region column if it's coming from data_a it will be A and B if it's from data B
# we will add the total sales by multiplying quantity and itemprice
# we will remove any duplicated of orderId if found
def transform_data(df, region):
    df['region'] = region
    # Calculate total_sales
    df['total_sales'] = df['QuantityOrdered'] * df['ItemPrice']
    df = df.drop_duplicates(subset='OrderId')
    return df

# once the data is combined we will remove the duplicates by keeping only the first occurance of the orderid and removing the second
def remove_duplicates(combined_data):
    combined_data = combined_data.drop_duplicates(subset='OrderId', keep='first')
    return combined_data

transformed_data_a = transform_data(data_a, 'A')
transformed_data_b = transform_data(data_b, 'B')

# we will use the concat function of pandas to combine the two data frames generated
combined_data = pd.concat([transformed_data_a, transformed_data_b], ignore_index=True)
combined_data = remove_duplicates(combined_data)

# checking if the transformed data is fine
print(combined_data.head())

# now we will create a sqlite connection to create the table and add the data
conn = sqlite3.connect('sales_data.db')
cursor = conn.cursor()

# create table query as per the question
create_table_query = '''
CREATE TABLE IF NOT EXISTS sales_data (
    OrderId TEXT PRIMARY KEY,
    OrderItemId TEXT,
    QuantityOrdered INTEGER,
    ItemPrice REAL,
    PromotionDiscount REAL,
    total_sales REAL,
    region TEXT
)
'''
cursor.execute(create_table_query)
conn.commit()

# now we will insert the data in the table if the same data exists we will replace it
combined_data.to_sql('sales_data', conn, if_exists='replace', index=False)

conn.close()