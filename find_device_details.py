# Import libraries
import os
import textwrap
import threading
import sys

from dotenv import load_dotenv
from netmiko import ConnectHandler

def remove_items(test_list, item): 
    res = [i for i in test_list if i != item] 
    return res 

def write_output(logFile, output, hostname):
    with open(logFile, "a") as file:
        file.write(f"{hostname},{output}\n")

def get_version_model(net_connect, command):
    # Send command to device and takes output
    output = net_connect.send_command(command, max_loops = 2000)
    # Parse the output
    output = output.split(" ")
    output = remove_items(output, "")
    output = f"{output[3]},{output[4]}"

    return(output)


def connect_and_run_commands(host, user, psw, output_file):
    switch = {
            'device_type': 'cisco_ios',
            'ip': host,
            'username': user,
            'password': psw
        }          

    # Retry 3 times to connect to the device (when connected breaks the cycle)
    for tries in range(2):
        try:
            print(f"[-]/{host}/ connection, try: {tries + 1}")
            net_connect = ConnectHandler(**switch, conn_timeout=120)

            # Takes the prompt of the device and remove the #
            hostname = net_connect.find_prompt().replace("#", "")
            version = get_version_model(net_connect, 'show version | in \*')
            line = f"{version},{host}"

            # Writes the output to device's file
            write_output(output_file, line, hostname)
            net_connect.disconnect()
            break

        # Exit script if CTRL + C is pressed
        except KeyboardInterrupt:
            print("Exiting script")
            try:
                # Disconnect from the device if connected
                net_connect.disconnect()
            except:
                None
            sys.exit()

        # Print connection error if both tries failed
        except Exception as err:
            if (tries == 1):
                # Print the error indented
                indented_error = textwrap.indent(err, "\t\t") 
                print(f'[-]/{host}/ connection error: \n{indented_error}')
                sys.exit()

def find_devices_details(user, psw, hosts_list):
    output_file = "output\device_details.csv" 
    try:
        os.remove("output\device_details.csv")
    except:
        None
    
    # Write headers to file
    with open(output_file, "a") as file:
        file.write("Hostname,Model,Version,IP Address\n")

    threads = []
    for host in hosts_list:
        thread = threading.Thread(target=connect_and_run_commands, args=(host, user, psw, output_file))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("[-] Device information retrieval completed.")

