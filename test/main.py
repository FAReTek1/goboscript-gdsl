import pprint

import goboscript_gdsl as gdsl

with open("gdsl.txt") as f:
    data = f.read()

decoder = gdsl.Decoder(debug=False)
decoder.load(data)

parsed = decoder.parse()

pprint.pp(parsed.__dict__)
