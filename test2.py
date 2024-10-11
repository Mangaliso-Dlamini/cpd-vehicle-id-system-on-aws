import re

texts = ["10652DC 22","6565OC 11", "10585", "OC 11"]

full_patterns = [r'\b\d{3}\s[A-Z]{2}\s\d{2}\b', r'\b\d{4}\s[A-Z]{2}\s\d{2}\b', r'\b\d{5}\s[A-Z]{2}\s\d{2}\b']
h1_patterns = [r'\b\d{3}\b', r'\b\d{4}\b', r'\b\d{5}\b']
h2_pattern = r'\b[A-Z]{2}\s\d{2}\b'

license_no = None
temp = None

for text in texts:
    for full_pattern in full_patterns:
        match = re.search(full_pattern, text)
        if match:
            license_no = match.group()
            print("Full format recognized:", license_no)
            break

    if license_no:
        break
    else:
          # Define temp here
        for h1_pattern in h1_patterns:
            #if temp:
                #break
            match_h1 = re.search(h1_pattern, text)
            if match_h1:
                temp = match_h1.group()  # Update temp if a match is found
                print("1st part format recognized:", temp)
                break  # Break out of the loop once a match is found
        match_h2 = re.search(h2_pattern, text)
        h2 = match_h2.group() if match_h2 else None
        if temp and h2:
            license_no = temp + ' ' + h2
            print("2nd part format recognized:", h2)
            break
        else:
            print("No recognized format in:", text)
            license_no = None

print("Final license number:", license_no)
