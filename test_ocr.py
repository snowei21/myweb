import easyocr
import re

reader = easyocr.Reader(['th','en'])
result = reader.readtext("pay_slip.jpg")

for r in result:
    print(r[1])

text = " ".join([r[1] for r in result])
amount = float(re.findall(r'\d+\.\d{2}', text)[0])
date_match = re.search(r'(\d{1,2})\s+([^\s]+)\s+(\d{2})', text)
day = int(date_match.group(1))
month = date_match.group(2)
year = int(date_match.group(3))

print(f'amount={amount}')
print(f'day={day} month={month} year={year}')

time_match = re.search(r'(\d{1,2}):(\d{2})', text)
hour = int(time_match.group(1))
minute = int(time_match.group(2))
print(f'hour={hour} minute={minute}')
