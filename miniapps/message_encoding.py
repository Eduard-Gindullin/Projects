# Кодирование сообщения
import base64

def encode_data(data):
    encoded = base64.b64encode(data.encode())
    return encoded

print (encode_data("ABC"))

def decode_data(encode_data):
    decoded = base64.b64decode(encode_data.decode())
    return decoded

def main():
    data = "ABC"

    encoded_data = encode_data(data)
    print(encoded_data)

    decoded_data = decode_data(encoded_data)
    print(decoded_data)

main()