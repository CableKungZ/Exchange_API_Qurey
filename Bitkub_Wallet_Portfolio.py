import requests
import hashlib
import hmac

# ขอ timestamp จาก Bitkub API
timestamp_url = 'https://api.bitkub.com/api/v3/servertime'
response = requests.get(timestamp_url)
timestamp = str(response.json())

# ข้อมูลสำหรับการส่งคำขอ POST
url = 'https://api.bitkub.com/api/v3/market/balances'
api_key = 'Your Bitkub Api Key *Read'
api_secret = 'Your Bitkub Secrect API KEY'

# สร้างข้อมูลที่จะถูก hash เพื่อสร้าง signature
message = f'{timestamp}POST/api/v3/market/balances'
signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()

# สร้างคำขอ POST
headers = {
    'Accept': 'application/json',
    'Content-type': 'application/json',
    'X-BTK-APIKEY': api_key,
    'X-BTK-TIMESTAMP': timestamp,
    'X-BTK-SIGN': signature
}

response = requests.post(url, headers=headers)

# ตรวจสอบการตอบกลับและแสดงผลลัพธ์ที่มี avilable หรือ reserved มากกว่า 0
if response.status_code == 200:
    balances = response.json()['result']
    total_thb_value = 0  # รวมมูลค่าทั้งหมดใน THB
    for asset, data in balances.items():
        if data['available'] > 0 or data['reserved'] > 0:
            total = data['available'] + data['reserved']
            if asset == "THB":
                total_thb_value += total
            else:
                # เรียกใช้ API เพื่อดึงข้อมูลมูลค่าคู่เหรียญ
                ticker_url = 'https://api.bitkub.com/api/market/ticker'
                ticker_response = requests.get(ticker_url)
                
                if ticker_response.status_code == 200:
                    ticker_data = ticker_response.json()
                    thb_asset = f"THB_{asset}"  # สร้างชื่อของคู่เหรียญ THB
                    if thb_asset in ticker_data:
                        total_value = ticker_data[thb_asset]['last'] * total
                        total_thb_value += total_value
                        print(f"{thb_asset}: Available - {data['available']}, Reserved - {data['reserved']}, Total - {total}, Value - {total_value} THB")
                    else:
                        print(f"No ticker data available for {thb_asset}")
                else:
                    print("Failed to fetch ticker data.")
    
    print(f"Total THB value: {total_thb_value} THB")
else:
    print("Failed to fetch balances.")
