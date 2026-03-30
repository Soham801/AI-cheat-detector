
import urllib.request
import ssl
import os

url = "https://github.com/kurnianggoro/GSOC2017/raw/master/data/lbfmodel.yaml"
dest = "models/lbfmodel.yaml"

if not os.path.exists("models"):
    os.makedirs("models")

print(f"Downloading {url} to {dest}...")

# Disable SSL verification
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(url, context=ctx) as response, open(dest, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print("Download complete.")
except Exception as e:
    print(f"Download failed: {e}")
