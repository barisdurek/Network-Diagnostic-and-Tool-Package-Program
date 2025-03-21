import socket
from time import ctime, sleep # ctime for SNTP, sleep for better readability of the menus
from datetime import datetime # It shows the time information belong your system (I am keeping it to compare with SNTP)
import ntplib # for SNTP time synchronization
import ifaddr # library for listing the network interfaces and their IP addresses
import json # library for the "settings" section of program to save the data

host = 'localhost' 
PORT = 9991  
data_payload = 2048

# MACHINE INFORMATION MODULE
def machine_information(): 
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    print("Host name :", host_name)
    print("IP address: ", ip_address)
    
    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        print("IPs of network adapter " + adapter.nice_name)
        for ip in adapter.ips:
            print("   %s/%s" % (ip.ip, ip.network_prefix))
            
# SNTP TIME CHECK MODULE
def time_syn(): 
    now = datetime.now()
    print("In your local system, time is: ", now)

    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('pool.ntp.org')
    print("With SNTP, the actual time is: ", ctime(response.tx_time))
    
# ECHO TEST MODULE
def echo_test():  # menu function of echo test option  
    mode = str(input("Server[s]/Client[c]/([q] for main menu)?: "))
    if mode == "s":
        echo_server()
    elif mode == "c":
        echo_client()
    elif mode == "q":
        main_menu()
    else:
        print("Invalid input")
        echo_test()
        
def echo_server(): # helper function for server side of echo testing
    """A simple UDP echo server that closes after one message"""
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (host, PORT)
    print("Starting up echo server on %s port %s" % server_address)
    sock.bind(server_address)

    print("Waiting to receive message from client")
    data, address = sock.recvfrom(data_payload)  # gets the message
    if data:
        print("Received: %s" % data.decode('utf-8'))
        sock.sendto(data, address)  # sends back the message
        print("Sent response to client, shutting down server.")

    sock.close()
    print("Connection successful, data matches")

def echo_client(): # helper function for client side of echo testing
    """A simple UDP echo client"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    server_address = (host, PORT)
    message = "Test message. This will be echoed"
    
    try:
        print("Sending: %s" % message)
        sent = sock.sendto(message.encode('utf-8'), server_address) # send the message to the server
        
        data, server = sock.recvfrom(data_payload) # receive the echoed message
        print("Received: %s" % data.decode('utf-8'))
        
    except socket.error as e:
        print("Socket error: %s" % e)
    finally:
        print("Connection successful, data matches")
        sock.close()

# CHAT MODULE     
def chat(): # menu function of chat option
    mode = str(input("Client[c]/Server[s]/([q] for main menu)?: "))
    if mode == "s":
        chat_server()
        main_menu()
    elif mode == "c":
        chat_client()
        main_menu()
    elif mode == "q":
        main_menu()   
    else:
        print("Invalid input")
        chat()
        
def chat_server(): # server side
    setting = get_settings() # first we get the settings from settings.json with function get_settings
    send_buf_size = setting["SEND_BUF_SIZE"]
    recv_buf_size = setting["RECV_BUF_SIZE"]
    timeout = setting["timeout"]
    blocking = setting["blocking"]
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # here we set the settings
    server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, send_buf_size)  
    server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, recv_buf_size)  
    server.settimeout(timeout)  
    server.setblocking(blocking) 
        
    server.bind((host, PORT))
    server.listen()

    print("Server is waiting for client to join")

    client, addr = server.accept()
    
    print(f"Connection: {addr}")
    print("\nSend the message 'quit' to finish the chat")

    while True:
        msg = client.recv(recv_buf_size).decode('utf-8')
        if msg == "quit":
            print("Client has closed the connection")
            client.send("quit".encode('utf-8'))  # also send the message 'quit' to let other side to know
            break

        print("Client:", msg)
        chat_save("Client", msg)  # saves the msg of client to the file
        
        response = input("Server: ")
        client.send(response.encode('utf-8'))

        if response == "quit":
            print("Server closing")
            break
        
        chat_save("Server", response)
                        
    client.close()
    server.close()
    print("Connection has closed")
    
def chat_client():
    setting = get_settings()
    send_buf_size = setting["SEND_BUF_SIZE"]
    recv_buf_size = setting["RECV_BUF_SIZE"]
    timeout = setting["timeout"]
    blocking = setting["blocking"]
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, send_buf_size)  
    client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, recv_buf_size) 
    client.settimeout(timeout) 
    client.setblocking(blocking)  

    client.connect((host, PORT))
    
    print(f"Connected the server: {host}:{PORT}")
    print("\nSend the message 'quit' to finish the chat")


    while True:
        msg = input("Client: ")
        client.send(msg.encode('utf-8'))

        if msg == "quit":
            print("Client closing...")
            break  

        response = client.recv(recv_buf_size).decode('utf-8')
        if response.lower() == "quit":
            print("Server closed the connection")
            break  

        print("Server:", response)

    client.close()
    print("Connection closed")
    
def chat_save(sender, message): # Written for sender side of chat section. Saves the both client and server messages into the file "message.txt"(Creates if there is no)
    with open("messages.txt", "a") as log_file: # tried to open the file in "w" mode, but every time it deletes everythink and just writes mesagge "quit", therefore we opening it in append mode
        log_file.write(f"{sender}: {message}\n")

# SETTINGS MODULE
def settings(): # menu function of the module. Also displays the previous settings
    setting = get_settings()
    sleep(.5)
    print("\nTimeout: ", setting["timeout"], "second")
    print("Blocking mode: ", setting["blocking"], "[0 is non-blocking / 1 is blocking]")
    print("Send buffer size: ", setting["SEND_BUF_SIZE"])
    print("Receive buffer size: ",  setting["RECV_BUF_SIZE"])
    sleep(.5)
    print("\n1-Timeout\n2-Blocking mode\n3-Send buffer size\n4-Receive buffer size") 
    sleep(.5)
    change = str(input("\nWhich setting do you want to change (q for main menu): "))

    if change == "1":
        change_timeout()
    elif change == "2":
        change_blocking_mode()
    elif change == "3":
        change_send_buffer()
    elif change == "4":
        change_recv_buffer()
    elif change == "q":
        main_menu()
    else:
        print("Wrong input")
        settings()

def get_settings(): # helper function. reads the json and gets the settings
    with open("settings.json", "r") as file:
        setting = json.load(file)
    return setting

def save_settings(setting): # helper function. writes and saves the changes into json
    with open("settings.json", "w") as file:
        json.dump(setting, file, indent=4)
    print("Change is saved")
    
def change_blocking_mode():
    setting = get_settings()
    blocking_mode = setting["blocking"] # gets used value from json
    print("Blocking mode was ", blocking_mode)
    new_blocking = int(input("What do you want to set[0 is non-blocking / 1 is blocking]: "))
    setting["blocking"] = new_blocking
    save_settings(setting)  # saves to json
    settings()

def change_send_buffer():
    setting = get_settings()
    send_buf_size = setting["SEND_BUF_SIZE"] # gets used value from json
    print("Send buffer size was ", send_buf_size)
    new_send_buf_size = int(input("What do you want to set: "))
    setting["SEND_BUF_SIZE"] = int(new_send_buf_size)
    save_settings(setting)  # saves to json
    settings()
    
def change_recv_buffer():
    setting = get_settings()
    recv_buf_size = setting["RECV_BUF_SIZE"] # gets used value from json
    print("Receive buffer size was ", recv_buf_size)
    new_recv_buf_size = int(input("What do you want to set: "))
    setting["RECV_BUF_SIZE"] = int(new_recv_buf_size)
    save_settings(setting)  # saves to json
    settings()

def change_timeout():
    setting = get_settings()
    timeout = setting["timeout"] # gets used value from json
    print("Timeout was ", timeout, "seconds")
    new_timeout = int(input("What do you want to set: "))
    setting["timeout"] = int(new_timeout)
    save_settings(setting)  # saves to json
    settings()

def main_menu(): # main menu of the program
    while True:
        sleep(.5)
        print("\n1-Machine Information\n2-Echo Test\n3-SNTP Time Check\n4-Socket Settings\n5-Chat\n(q for quit)\n")
        sleep(.5)
        selection = input("Select mode: ")
        if selection == "1": 
            machine_information()
        elif selection == "2":
            echo_test()
        elif selection == "3":
            time_syn()
        elif selection == "4":
            settings()
        elif selection == "5":
            chat()
        elif selection == "q":
            exit()   
        else:
            print("Wrong input")
        
if __name__ == '__main__':
    main_menu()