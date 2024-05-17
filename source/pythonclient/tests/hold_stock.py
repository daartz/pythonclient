from connection_port import *
from marketHours import *
from placeOrder import *
from portfolio import *

today = datetime.now().date()

orders = ['hold']

index = ['US9', 'ITALY', 'SPAIN', 'BELGIUM', 'GERMANY']

hold_stock =[]
country2 = []
buy_date = []
days = []
url = []
buy_price = []
close = []
actual_tx = []
actual = []


for country in index:
    print(country)

    csv_file_path = f'C:\\Users\\daart\\OneDrive\\PROREALTIME\\Signals\\{country} hold signals {today}.csv'

    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        continue

    # Read the CSV file
    df = read_csv_with_encoding_and_delimiter_attempts(csv_file_path)

    if df is None:
        continue

    # Convert the 'DATE' column to datetime and filter for today's date
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

    # Filter the DataFrame for today's date
    df_today = df[df['DATE'].dt.date == today]


    # Process orders
    for index, row in df_today.iterrows():
        date = row['DATE'].strftime("%Y-%m-%d")

        if date != str(today):
            continue


        stock = row['STOCK'].split('.')[0]
        hold_stock.append(stock)
        country2.append(country)
        buy_date.append(row['BUY DATE'])
        days.append((row['DAYS']))
        url.append(row['URL'])
        buy_price.append(row['BUY'])
        close.append(row['CLOSE'])
        actual_tx.append(row['ACTUAL %'])
        actual.append(row['ACTUAL_2000'])

        hold_data = pd.DataFrame({
            "COUNTRY": country2,
            "STOCK": hold_stock,
            "BUY DATE": buy_date,
            "BUY PRICE": buy_price,
            "CLOSE": close,
            "ACTUAL %": actual_tx,
            "ACTUAL 2000": actual,
            "DAYS": days,
            "URL": url
        })

    print(hold_data)


ports = ['4001','5001']

# Initialize columns for each port
for p in ports:
    hold_data[f'PORT_{p}'] = 'ABSENT'

# Update the hold_data DataFrame based on portfolio data
for p in ports:
    file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{p}.csv"

    data = pd.read_csv(file)

    for index, row in data.iterrows():
        exist = row['Symbol']

        if exist in hold_stock and row['UnrealizedPNL'] == '0.0':
            hold_data.loc[hold_data['STOCK'] == exist, f'PORT_{p}'] = 'PRESENT'

# Move the 'URL' column to the last position
columns = hold_data.columns.tolist()
columns.append(columns.pop(columns.index('URL')))
hold_data = hold_data[columns]

# Filter to keep only rows where at least one port has 'Absent'
filter_condition = hold_data[[f'PORT_{p}' for p in ports]].eq('ABSENT').any(axis=1)
filtered_hold_data = hold_data[filter_condition]

# Sort the filtered_hold_data by 'BUY DATE' and then by 'STOCK'
filtered_hold_data = filtered_hold_data.sort_values(by=['BUY DATE', 'STOCK'])

# Save the filtered_hold_data to a CSV file
output_csv_path = f'C:\\Users\\daart\\OneDrive\\PROREALTIME\\Signals\\filtered_hold_data_{today}.csv'
filtered_hold_data.to_csv(output_csv_path, index=False)

print(filtered_hold_data)
print(f"hold_data saved to {output_csv_path}")

html_data = '<p>Hold stock </p>' + filtered_hold_data.to_html()
send_mail_html("IBKR Hold Stock ", html_data)