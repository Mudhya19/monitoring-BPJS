# import hashlib
# import random
# import base64
# import urllib.parse  # Updated import for Python 3
# import hmac

# data = "17934"
# secretkey = "4bSCEE3F6B"

# # Convert the key and data to bytes
# signature = hmac.new(secretkey.encode(), msg=data.encode(), digestmod=hashlib.sha256).digest()

# # Base64 encode the signature
# encodedSignature = base64.b64encode(signature).decode().replace('\n', '')

# # URL encode the encoded signature
# # encodedSignature = urllib.parse.quote(encodedSignature)  # Updated for Python 3

# print("Voila! A Signature: " + encodedSignature)


# streamlit_app.py

import streamlit as st

# Initialize connection.
conn = st.connection('mysql', type='sql')

# Perform query.
df = conn.query('SELECT * from pasien', ttl=600)

# Print results.
for row in df.itertuples():
    st.write(f"{row.name} has a :{row.pet}:")
