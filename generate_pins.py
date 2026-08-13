import hashlib
import getpass

def hash_pin():
    print("--- PIN Hasher ---")
    user = input("Enter your username (e.g., Cris, Bea, Fer): ")
    pin = getpass.getpass(f"Enter a secret PIN for {user}: ")
    
    # Hash the PIN
    hashed = hashlib.sha256(pin.encode()).hexdigest()
    
    print("\n✅ Success!")
    print(f"Add the following line to your .streamlit/secrets.toml under the [pins] section:")
    print(f'{user} = "{hashed}"')
    
if __name__ == "__main__":
    hash_pin()
