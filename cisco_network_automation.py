import os
import platform

from getpass import getpass
from textwrap import dedent
from sys import exit
from backup_conf import backup_conf
from find_access_interfaces_vlan import find_access_int
from find_device_details import find_devices_details
from find_errdisable import find_err_disable

def get_hosts_list(file_path):
    '''return the list of hosts in the file'''
    with open(file_path,  'r') as f:
        hosts_list = f.read().splitlines()
        return hosts_list  

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
        | [2] Find errdisable interfaces      |
        | [3] Find device information         |
        | [4] Find access interfaces on vlan  |
        | [5] Find hubs                       |
        | [6] Find PoE interfaces             |
        | [7] Trace mac address               |
        | [8] Draw network                    |
        | [9] Send bulk commands              |
        | [10] Re-input credentials           |
        | [11] Exit                           |
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

        hosts = get_hosts_list('hosts.txt')

        while True:
            choice = menu(clear_string)
            if choice == 1:
                # Perform configuration backup
                print("[-] Configuration backup started...")
                backup_conf(user, psw, hosts)
            elif choice == 2:
                # Find errdisable interfaces
                print("[-] Searching for errdisable interfaces...")
                find_err_disable(user, psw, hosts)
            elif choice == 3:
                # Find devices details
                print("[-] Getting devices information...")
                find_devices_details(user, psw, hosts)
            elif choice == 4:
                # Find access interfaces on a vlan
                vlan = int(input("[*] Insert vlan ID: "))
                print("[-] Getting access interfaces...")
                find_access_int(user, psw, hosts, vlan)
            elif choice == 10:
                user, psw = get_credentials()
                print("[-] Credentials changed")
            elif choice == 11:
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