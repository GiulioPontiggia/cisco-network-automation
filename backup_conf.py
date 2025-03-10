# Import libraries
import os, shutil
import threading
import sys
import textwrap

from netmiko import ConnectHandler


def remove_old_conf_files(path):
    ''' Remove all configuration files if any '''
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.ispath(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'[-] Failed to delete {file_path}. Reason: {e}')

def write_backup(path, hostname, config):
    ''' Write configuration to file in the conf directory '''
    path = f"{path}{hostname}.conf"
    with open(path, "w") as file:
        print(f"[{hostname}] Configuration backup stored in {path}")
        file.write(config)

def connect_and_run_commands(host, user, psw, path):
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
            net_connect.send_command("terminal length 0")
            config = net_connect.send_command("show running")

            net_connect.disconnect()
            write_backup(path, hostname, config)
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

def backup_conf(user, psw, hosts):
    output_path = "output\\conf\\"
    remove_old_conf_files(output_path)

    threads = []
    for host in hosts:
        thread = threading.Thread(target=connect_and_run_commands, args=(host, user, psw, output_path))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print('[-] Configuration backup completed!')
