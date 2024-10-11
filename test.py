import re
texts = ["6565 OC 11", "6585", "OC 11"]

full_pattern = r'\b\d{4}\s[A-Z]{2}\s\d{2}\b'
h1_pattern = r'\b\d{4}\b'
h2_pattern = r'\b[A-Z]{2}\s\d{2}\b'

for text in texts:
    h2=h1=""
    match = re.search(full_pattern, text)
    if match:
            #print("Format recognized:", match.group())
        license_no = match.group()
        break
    else:
        match2 = re.search(h1_pattern, text)
        match3 = re.search(h2_pattern, text)
        if match2:
            h1 = match2.group()

        elif match3:
            h2 = match3.group()
        license_no = h1 + ' ' + h2

print(license_no)