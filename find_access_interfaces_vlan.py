# Import libraries
import os
import textwrap
import threading
import shutil
import sys

from netmiko import ConnectHandler

def remove_items(test_list, item): 
    res = [i for i in test_list if i != item] 
    return res 

def write_to_file(path, output, host, hostname):
    with open(path, 'a') as fLog:
        # Writes the IP of the device at the beginning of the file
        fLog.write(f"[-]{hostname}/{host}/\n")
        # Write the output 
        fLog.write(f"{output}")

def connect_and_run_commands(host, user, psw, command, output_dir):
    switch = {
            'device_type': 'cisco_ios',
            'ip': host,
            'username': user,
            'password': psw
        }          

    # Retry 2 times to connect to the device (when connected breaks the cycle)
    for tries in range(2):
        try:
            print(f"[-]/{host}/ connection, try: {tries + 1}")
            net_connect = ConnectHandler(**switch, conn_timeout=120)

            # Takes the prompt of the device and remove the #
            hostname = net_connect.find_prompt().replace("#", "")
                        
            # Send command to device and takes output
            output = net_connect.send_command(command, max_loops = 2000)

            if output != "":
                output_lines = output.split("\n")
                cleared_output = list()

                for line in output_lines:
                    cleared_output.append(remove_items(line.split(" "), "")[0])

                # Writes the output to device's file
                write_to_file(f"{output_dir}/{hostname}.txt", 
                              '\n'.join(cleared_output), 
                              host, 
                              hostname)
           
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

def find_access_int(user, psw, hosts, vlan):

    output_dir = "output/access_interfaces"
    command = f"show int status | in conne.*{vlan}"

    # Remove each file in the directory
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.ispath(file_path):
                shutil.rmtree(file_path)
        except:
            None
    
    threads = []
    for host in hosts:
        thread = threading.Thread(target=connect_and_run_commands, args=(host, user, psw, command, output_dir))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(f"[-] Access interfaces on vlan {vlan} found.")
