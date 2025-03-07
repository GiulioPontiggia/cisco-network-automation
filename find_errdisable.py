# Import libraries
import os
import threading
import textwrap
import sys

from netmiko import ConnectHandler  

def write_output(logFile, out_list, hostname):
    with open(logFile, "a") as file:
        for entry in out_list:
            file.write(f"[{hostname}] {entry}")

def connect_and_run_commands(host, user, psw):
    switch = {
            'device_type': 'cisco_ios',
            'ip': host,
            'username': user,
            'password': psw
        }          
    command = "show int status | include err"

    # Retry 3 times to connect to the device (when connected breaks the cycle)
    for tries in range(2):
        try:
            print(f"[-]/{host}/ connection, try: {tries + 1}")
            net_connect = ConnectHandler(**switch, conn_timeout=120)

            # Takes the prompt of the device and remove the #
            hostname = net_connect.find_prompt().replace("#", "")
            out_list = list()
            
            # Send command to device and takes output
            output = net_connect.send_command(command, max_loops = 2000)
            # Append output to output list (it will be written in the output file)
            output_row = output.replace('\n', '')
            if output_row != '':
                out_list.append(f"\n{output_row}\n")

            # Writes the output to device's file
            logFile = "output\errdisable_interfaces.txt" 
            if out_list != []:
                write_output(logFile, out_list, hostname)
            else:
                write_output(logFile, ["no errdisable interfaces"], hostname)
            net_connect.disconnect()
            break

        # Exit script if CTRL + C is pressed
        except KeyboardInterrupt:
            print("\n[-] Exiting script")
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

def find_err_disable(user, psw, hosts):
    
    try:
        os.remove("output\errdisable_interfaces.txt")
    except:
        None

    threads = []
    for host in hosts:
        thread = threading.Thread(target=connect_and_run_commands, args=(host, user, psw))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    
    print('[-] Search for errdisable interfaces completed!')
