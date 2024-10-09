import os
from dotenv import load_dotenv
from iota_sdk import Client, MnemonicSecretManager, AddressAndAmount
import nfc
from pyfiglet import Figlet
from termcolor import colored  # Import termcolor to add color to the text

# Function to display the banner with the text "QBII" in color
def show_banner():
    banner = Figlet(font='standard')
    colored_banner = colored(banner.renderText('Qbbi'), 'magenta')  # Add magenta color to the text
    print(colored_banner)

    print("Welcome to the IOTA x NFC transaction DEMO")

# Display the banner before loading the environment and starting the execution
show_banner()

# Load environment variables
load_dotenv()

# Configure the client using the IOTA node
node_url = os.environ.get('NODE_URL', 'https://api.testnet.iotaledger.net')
client = Client(nodes=[node_url])

# Define the destination address
destination_address = 'tst1qrpvft692as3cptmhrr93dl8p5d4y720mzusctsydnuqnw29l3yl6v5sk49'

# Connect to the NFC reader
clf = nfc.ContactlessFrontend('usb')

# Function to read the mnemonic from the NFC tag
def read_from_tag(tag):
    print("Tag detected:", tag)

    # Check for NDEF records
    if tag.ndef:
        # Read the content of the first record and use it as the mnemonic
        record = tag.ndef.records[0]
        mnemonic = record.text

        # Print "Mnemonic read" in green and the mnemonic value in white
        print(f"{colored('Mnemonic read:', 'green')} {colored(mnemonic, 'white')}")

        return mnemonic
    else:
        # Highlight "No NDEF records" in red and keep other details in white
        print(f"{colored('Error:', 'red')} {colored('No NDEF records on the tag.', 'white')}")
        return None

# Function to perform the transaction in IOTA using the mnemonic
def perform_transaction(mnemonic, amount):
    try:
        # Initialize the Secret Manager with the mnemonic
        secret_manager = MnemonicSecretManager(mnemonic)

        # Define the output using AddressAndAmount
        address_and_amount = AddressAndAmount(
            amount=amount,  # Use the input amount from the user
            address=destination_address  # Use the predefined destination address
        )

        # Create and send the block with the transaction
        block = client.build_and_post_block(
            secret_manager=secret_manager,
            output=address_and_amount,
            coin_type=4218  # Set the coin type for IOTA
        )

        # Check if block is a list or a dictionary
        if isinstance(block, list):
            block_id = block[0]  # Assuming that the block ID is the first element of the list
        elif isinstance(block, dict):
            block_id = block["block_id"]  # If it is a dictionary, get the block ID

        # Print "Block sent" in green and the block link in white
        print(f"{colored('Block sent:', 'green')} {colored(os.environ['EXPLORER_URL'] + '/block/' + block_id, 'white')}")

    except Exception as e:
        # Print the full "Error performing the transaction" in red and the exception in white
        print(f"{colored('Error performing the transaction:', 'red')} {colored(str(e), 'white')}")

# Main function to coordinate NFC reading and IOTA transaction
def main():
    try:
        amount = None

        # Loop until the user confirms the correct amount and address
        while True:
            # Ask the user to input the amount in IOTA
            user_input = input(colored("Please enter the amount in IOTA to be transferred: ", 'yellow'))
            
            # Validate that the input is a valid integer
            try:
                amount = int(user_input)
            except ValueError:
                print(f"{colored('Error:', 'red')} {colored('Please enter a valid numeric value.', 'white')}")
                continue

            # Calculate amount in Miota
            miota_amount = amount / 1_000_000

            # Print the amount in IOTA and Miota, and address for confirmation
            print(f"{colored('Amount entered:', 'green')} {colored(amount, 'white')} IOTA ({colored(miota_amount, 'cyan')} MIOTA)")
            print(f"{colored('Destination Address:', 'green')} {colored(destination_address, 'white')}")

            # Ask for confirmation
            confirmation = input(colored("Is the information correct? (y/n): ", 'cyan')).lower()

            if confirmation == 'y':
                break
            elif confirmation == 'n':
                print(colored("Please re-enter the amount.", 'yellow'))
            else:
                print(f"{colored('Error:', 'red')} {colored('Invalid input. Please enter y (yes) or n (no).', 'white')}")

        # Connect and wait for the card
        print(colored("Waiting for the NFC tag to be detected...", 'cyan'))
        clf.connect(rdwr={'on-connect': lambda tag: read_and_transact(tag, amount)})
    except Exception as e:
        # Print "Error" in red and the exception message in white
        print(f"{colored('Error:', 'red')} {colored(e, 'white')}")
    finally:
        # Close the connection with the NFC reader
        clf.close()

# Function to read and perform the transaction
def read_and_transact(tag, amount):
    # Read the mnemonic from the tag
    mnemonic = read_from_tag(tag)
    
    # If the mnemonic is valid, perform the transaction
    if mnemonic:
        print(colored("Performing the transaction with the read mnemonic...", 'cyan'))
        perform_transaction(mnemonic, amount)
    else:
        # Print "Error" in red and the additional message in white
        print(f"{colored('Error:', 'red')} {colored('Could not read a valid mnemonic from the tag.', 'white')}")

# Run the script
if __name__ == "__main__":
    main()
