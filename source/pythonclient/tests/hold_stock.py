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

        hold_data = pd.DataFrame()

        hold_data["COUNTRY"] = country2
        hold_data["STOCK"] = hold_stock
        hold_data["BUY DATE"] = buy_date
        hold_data["DAYS"] = days
        hold_data["URL"] = url

        print(hold_data)


    port = ['4001','5001']

    for p in port:

        file = f"C:\\TWS API\\source\\pythonclient\\tests\\Data\\portfolio_{p}.csv"

        # data = read_csv_with_encoding_and_delimiter_attempts(file)
        data = pd.read_csv(file)

        for index, row in data.iterrows():
            exist = row['Symbol']

            if exist in hold_stock:
                print("OK")
            else:
                print("KO")