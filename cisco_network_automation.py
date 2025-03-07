import os
import platform

from getpass import getpass
from textwrap import dedent
from sys import exit
from backup_conf import backup_conf

def get_credentials():
    print("[-] Insert credentials...")
    user = input("[*] Insert username: ")
    psw = getpass("[*] Insert password: ")
    return user, psw

def menu(clear_string):
    menu = dedent('''
        =======================================
        |              MAIN MENU              |
        =======================================
        | [1] Configuration backup            |
        | [2] Option 2                        |
        | [3] Option 3                        |
        | [4] Exit                            |
        =======================================
    ''')
    # Clear screen
    os.system(clear_string)
    # Print menu
    print(menu)

    # Get choice from the user
    choice = int(input("[*] Choose: "))
    return choice

def main():
    try:
        print("\n\n")
        clear_string = "cls" if platform.system() == "Windows" else "clear"
        user, psw = get_credentials()
        while True:
            choice = menu(clear_string)
            if choice == 1:
                # Perform configuration backup
                print("[-] Configuration backup started...")
                backup_conf(user, psw)
            elif choice == 2:
                None
            elif choice == 3:
                None
            elif choice == 4:
                # Exit script
                print("\n[-] Exiting...")
                exit()
            input("[*] Press Enter to continue... ")
    except KeyboardInterrupt:
        # Exit when Ctrl+C is pressed
        print("\n[-] Exiting...")
    except Exception as e:
        print(f"[-] An error occured: {e}")


if __name__ == '__main__':
    main()