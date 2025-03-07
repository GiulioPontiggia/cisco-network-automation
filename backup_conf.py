# Import libraries
import os, shutil
import threading
import sys
import textwrap

from netmiko import ConnectHandler


def get_hosts_list(file_path):
    '''return the list of hosts in the file'''
    with open(file_path,  'r') as f:
        hosts_list = f.read().splitlines()
        return hosts_list    

def remove_old_conf_files(dir):
    ''' Remove all configuration files if any '''
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'[-] Failed to delete {file_path}. Reason: {e}')

def write_backup(dir, hostname, config):
    ''' Write configuration to file in the conf directory '''
    path = f"{dir}\{hostname}.conf"
    with open(path, "w") as file:
        print(f"[{hostname}] Configuration backup stored in {path}")
        file.write(config)

def connect_and_run_commands(host, user, psw):
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
            write_backup("conf", hostname, config)
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

def backup_conf(user, psw):
    
    hosts_file = 'hosts.txt'

    hosts_list = get_hosts_list(hosts_file)
    
    remove_old_conf_files('conf')

    threads = []
    for host in hosts_list:
        thread = threading.Thread(target=connect_and_run_commands, args=(host, user, psw))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(f'[-] Configuration backup completed!')
