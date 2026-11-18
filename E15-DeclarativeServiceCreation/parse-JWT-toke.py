import base64
import json

JWT_FILE = "endpoint-client.jwt"

def decode_b64url(segment: str):
    padding = "=" * (-len(segment) % 4)
    decoded_bytes = base64.urlsafe_b64decode(segment + padding)
    return json.loads(decoded_bytes.decode("utf-8"))

def main():
    with open(JWT_FILE, "r", encoding="utf-8") as f:
        token = f.read().strip()

    parts = token.split(".")

    header = decode_b64url(parts[0])
    payload = decode_b64url(parts[1])

    print("\nRaw Decoded header JSON:")
    print(json.dumps(header, indent=2))
    print("\nRaw Decoded payload JSON:")
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()