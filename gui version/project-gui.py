import socket
from time import ctime # library related to SNTP
from datetime import datetime # It shows the time information belong your system (I am keeping it to compare with SNTP)
import ntplib # for SNTP time synchronization
import ifaddr # library I found for listing the network interfaces and their IP addresses
import json # library for the "settings" section of program to read and write the settings
from tkinter import * # library for gui
import threading 

host = 'localhost'
PORT = 9991  
data_payload = 2048
client_socket = None
stop_event = threading.Event()
role = None  # in message saving function chat_save(), it specifies whether it is server or client(because I wrote the code in one python file)

# MACHINE INFORMATION MODULE
def machine_information(text_widget): # shows host name, IP addesses of open ports
    text_widget.delete(1.0, END) # clears the textbox before printing something different
    
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    text_widget.insert(END, f"Host name: {host_name}\n")
    text_widget.insert(END, f"IP address: {ip_address}\n\n")
    
    adapters = ifaddr.get_adapters() # lists the network interfaces and their IP addresses (by additional library)
    for adapter in adapters:
        text_widget.insert(END, f"IPs of network adapter {adapter.nice_name}\n")
        for ip in adapter.ips:
            text_widget.insert(END, f"   {ip.ip}/{ip.network_prefix}\n")

# SNTP TIME CHECK MODULE
def time_syn(text_widget): # gets the time information with SNTP
    text_widget.delete(1.0, END)  # clears the textbox before printing something different

    now = datetime.now() # shows your computers local time information
    text_widget.insert(END, f"In your local system, time is: {now}\n")

    ntp_client = ntplib.NTPClient() # SNTP time info
    response = ntp_client.request('pool.ntp.org')
    text_widget.insert(END, f"With SNTP, the actual time is: {ctime(response.tx_time)}\n")
    
# ECHO SERVER MODULE
def echo_server_thread(text_widget): # server side of the echo test part
    # Gets the settings from json file and sets them
    settings = get_settings()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, settings["SEND_BUF_SIZE"])
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, settings["RECV_BUF_SIZE"])
    sock.settimeout(settings["timeout"])
    sock.setblocking(settings["blocking"])
    
    server_address = (host, PORT) 
    text_widget.insert(END, f"Starting up echo server on {server_address[0]} port {server_address[1]}\n")
    sock.bind(server_address)
    text_widget.insert(END, "Waiting to receive message from client\n")
    try:
        data, address = sock.recvfrom(data_payload)
        if data:
            received_message = data.decode('utf-8')
            text_widget.insert(END, f"Received: {received_message}\n")
            sock.sendto(data, address)
            text_widget.insert(END, "Sent response to client, shutting down server.\n")
    except socket.error as e:
        text_widget.insert(END, f"Socket error: {e}\n")
    finally:
        sock.close()
        text_widget.insert(END, "Connection successful, data matches\n")

def echo_server(text_widget): # helper function. starts server thread 
    text_widget.delete(1.0, END) 
    thread = threading.Thread(target=echo_server_thread, args=(text_widget,))
    thread.start()

# ECHO CLIENT MODULE
def echo_client_thread(text_widget, entry_widget): # client side of the echo test part
    # Gets the settings from json file and sets them
    settings = get_settings()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, settings["SEND_BUF_SIZE"])
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, settings["RECV_BUF_SIZE"])
    sock.settimeout(settings["timeout"])
    sock.setblocking(settings["blocking"])
    
    server_address = (host, PORT)
    message = entry_widget.get()
    if not message:
        message = "Test message. This will be echoed"
    try:
        text_widget.insert(END, f"Sending: {message}\n")
        sent = sock.sendto(message.encode('utf-8'), server_address)
        data, server = sock.recvfrom(data_payload)
        received_message = data.decode('utf-8')
        text_widget.insert(END, f"Received: {received_message}\n")
    except socket.error as e:
        text_widget.insert(END, f"Socket error: {e}\n")
    finally:
        text_widget.insert(END, "Connection successful, data matches\n")
        sock.close()

def echo_client(text_widget, entry_widget): # helper function. starts client thread 
    text_widget.delete(1.0, END) 
    thread = threading.Thread(target=echo_client_thread, args=(text_widget, entry_widget))
    thread.start()
    
# SETTINGS MODULE
def get_settings(): # opens and reads the previous settings
    with open("settings.json", "r") as file: 
        return json.load(file)

def save_settings(setting): # gets the user input for settings and writes them into json file
    with open("settings.json", "w") as file:
        json.dump(setting, file, indent=4)

def show_settings(text_widget): # prints the settings on the text area(to prove user settings has been changed)
    try:
        settings = get_settings()
        text_widget.delete(1.0, END) # clears the textbox before printing something different
        text_widget.insert(END, "Current Socket Settings:\n")
        text_widget.insert(END, f"Timeout: {settings['timeout']} seconds\n")
        text_widget.insert(END, f"Blocking mode: {settings['blocking']} [0 is non-blocking / 1 is blocking]\n")
        text_widget.insert(END, f"Send buffer size: {settings['SEND_BUF_SIZE']}\n")
        text_widget.insert(END, f"Receive buffer size: {settings['RECV_BUF_SIZE']}\n")
    except (FileNotFoundError, ValueError) as e:
        text_widget.delete(1.0, END)
        text_widget.insert(END, str(e) + "\n")

def update_settings(text_widget, timeout_entry, blocking_entry, send_buf_entry, recv_buf_entry):
    # reads the user inputs and saves them into json file
    settings = get_settings()
    
    # here I check the input values, are inputs valid integers or invalid strings(seperately for each value)
    timeout = timeout_entry.get()
    if timeout:
        try:
            timeout_value = int(timeout)
            if timeout_value < 0:
                text_widget.delete(1.0, END)
                text_widget.insert(END, "Timeout cannot be negative\n")
                return
            settings["timeout"] = timeout_value
        except ValueError:
            text_widget.delete(1.0, END)
            text_widget.insert(END, "Timeout must be a valid integer\n")
            return
    
    blocking = blocking_entry.get()
    if blocking:
        try:
            blocking_value = int(blocking)
            if blocking_value not in [0, 1]:
                text_widget.delete(1.0, END)
                text_widget.insert(END, "Blocking mode must be 0 (non-blocking) or 1 (blocking)\n")
                return
            settings["blocking"] = blocking_value
        except ValueError:
            text_widget.delete(1.0, END)
            text_widget.insert(END, "Blocking must be an integer (0 or 1)\n")
            return
    
    send_buf = send_buf_entry.get()
    if send_buf:
        try:
            send_buf_value = int(send_buf)
            if send_buf_value < 0:
                text_widget.delete(1.0, END)
                text_widget.insert(END, "Send buffer size cannot be negative\n")
                return
            settings["SEND_BUF_SIZE"] = send_buf_value
        except ValueError:
            text_widget.delete(1.0, END)
            text_widget.insert(END, "Send buffer size must be a valid integer\n")
            return
    
    recv_buf = recv_buf_entry.get()
    if recv_buf:
        try:
            recv_buf_value = int(recv_buf)
            if recv_buf_value < 0:
                text_widget.delete(1.0, END)
                text_widget.insert(END, "Receive buffer size cannot be negative\n")
                return
            settings["RECV_BUF_SIZE"] = recv_buf_value
        except ValueError:
            text_widget.delete(1.0, END)
            text_widget.insert(END, "Receive buffer size must be a valid integer\n")
            return
    
    save_settings(settings)
    text_widget.delete(1.0, END)
    text_widget.insert(END, "Settings updated successfully!\n")
    show_settings(text_widget)

# CHAT MODULE
def chat_server_thread(text_widget, window): # chat module, server part
    global client_socket, stop_event, role
    settings = get_settings()
    send_buf_size = settings["SEND_BUF_SIZE"]
    recv_buf_size = settings["RECV_BUF_SIZE"]
    timeout = settings["timeout"]
    blocking = settings["blocking"]
    
    # socket creation and application of settings
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, send_buf_size)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, recv_buf_size)
    server.settimeout(timeout)
    server.setblocking(blocking)  
    
    server.bind((host, PORT))
    server.listen()
    
    text_widget.delete(1.0, END) 
    text_widget.insert(END, "Server is waiting for client to join\n")
    
    while True:
        if stop_event.is_set():
            server.close()
            return
        client, addr = server.accept()  
        break
    
    text_widget.insert(END, f"Connection: {addr}\n")
    client_socket = client
    role = "Server"   
    
    def receive_messages():
        while not stop_event.is_set():
            msg = client.recv(recv_buf_size).decode('utf-8') 
            if msg:
                if msg == "quit":
                    text_widget.insert(END, "Client has closed the connection. Chat is now terminated.\n")
                    client.send("quit".encode('utf-8')) 
                    stop_event.set()
                    break
                text_widget.insert(END, f"Client: {msg}\n")
        client.close()
        server.close()
        text_widget.insert(END, "Server connection has closed.\n")
    
    threading.Thread(target=receive_messages, daemon=True).start()

def chat_client_thread(text_widget, window): # chat module, client part
    global client_socket, stop_event, role
    settings = get_settings()
    send_buf_size = settings["SEND_BUF_SIZE"]
    recv_buf_size = settings["RECV_BUF_SIZE"]
    timeout = settings["timeout"]
    blocking = settings["blocking"]
    
    # creating socket and applying settings
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, send_buf_size)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, recv_buf_size)
    client.settimeout(timeout)
    client.setblocking(blocking)
    
    text_widget.delete(1.0, END) # clears the textbox before printing something different
    client.connect((host, PORT))  
    text_widget.insert(END, f"Connected to server: {host}:{PORT}\n")
    client_socket = client
    role = "Client"  
    
    def receive_messages():
        while not stop_event.is_set():
            msg = client.recv(recv_buf_size).decode('utf-8')  
            if msg:
                if msg == "quit":
                    text_widget.insert(END, "Server has closed the connection. Chat is now terminated.\n")
                    stop_event.set()
                    break
                text_widget.insert(END, f"Server: {msg}\n")
        client.close()
        text_widget.insert(END, "Client connection has closed.\n")
    
    threading.Thread(target=receive_messages, daemon=True).start()

def chat_save(sender, message): # saves the messages into the file messages.txt
    with open("messages.txt", "a") as log_file:
        log_file.write(f"{sender}: {message}\n")

def send_message(text_widget, entry_widget): # for the sender of chat module
    global client_socket, stop_event, role
    if client_socket:
        msg = entry_widget.get()
        if msg:
            client_socket.send(msg.encode('utf-8'))
            text_widget.insert(END, f"You: {msg}\n")
            sender = role
            chat_save(sender, msg)
            entry_widget.delete(0, END)

def quit_chat(text_widget): # function that ends the chat by quit
    global client_socket, stop_event, role
    if client_socket:
        client_socket.send("quit".encode('utf-8'))
        text_widget.insert(END, "You have closed the chat. Connection terminated.\n")
        stop_event.set()
        client_socket.close()
        client_socket = None
        role = None 

# GUI MODULE with the library tkinter 
def gui():
    window = Tk()
    menubar = Menu(window)
    window.geometry("800x500") # sets the window size
    window.title("Network Diagnostic and Tool Package")

    window.config(menu=menubar)
    menubar.add_cascade(label="Machine Information", command=lambda: machine_information(text))

    echo_menu = Menu(menubar, tearoff=0) # tearoff 0 otherwise dropdown menu looks ugly
    menubar.add_cascade(label="Echo test", menu=echo_menu) # to make it dropdown 
    echo_menu.add_command(label="Server", command=lambda: echo_server(text))
    echo_menu.add_command(label="Client", command=lambda: echo_client(text, message_entry))    

    menubar.add_cascade(label="SNTP Time Check", command=lambda: time_syn(text))

    chat_menu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Chat", menu=chat_menu)
    chat_menu.add_command(label="Server", command=lambda: [stop_event.clear(), chat_server_thread(text, window)])
    chat_menu.add_command(label="Client", command=lambda: [stop_event.clear(), chat_client_thread(text, window)])
            
    text = Text(window, height=25, width=95)  # textbox
    text.pack(pady=10)  
    
    # frame and entry for settings section 
    settings_frame = Frame(window)
    settings_frame.pack(pady=5)

    settings = get_settings() # gets the settings from settings.json and displays 

    Label(settings_frame, text="Timeout:").pack(side=LEFT, padx=5)
    timeout_entry = Entry(settings_frame, width=10)
    timeout_entry.insert(0, settings["timeout"])  # timeout
    timeout_entry.pack(side=LEFT, padx=5)

    Label(settings_frame, text="Blocking:").pack(side=LEFT, padx=5)
    blocking_entry = Entry(settings_frame, width=10)
    blocking_entry.insert(0, settings["blocking"])  # blocking
    blocking_entry.pack(side=LEFT, padx=5)

    Label(settings_frame, text="Send Buffer:").pack(side=LEFT, padx=5)
    send_buf_entry = Entry(settings_frame, width=10)
    send_buf_entry.insert(0, settings["SEND_BUF_SIZE"])  #  send buffer
    send_buf_entry.pack(side=LEFT, padx=5)

    Label(settings_frame, text="Receive Buffer:").pack(side=LEFT, padx=5)
    recv_buf_entry = Entry(settings_frame, width=10)
    recv_buf_entry.insert(0, settings["RECV_BUF_SIZE"])  # receive buffer
    recv_buf_entry.pack(side=LEFT, padx=5)

    update_button = Button(
        settings_frame, 
        text="Update Settings", 
        command=lambda: update_settings(text, timeout_entry, blocking_entry, send_buf_entry, recv_buf_entry),
        bg="green", 
        fg="white", 
        font=("Arial", 10, "bold"), 
        padx=10, 
        pady=5
    ) # update settings button
    update_button.pack(side=LEFT, padx=5)

    # frame and entry for message entry section
    message_frame = Frame(window)
    message_frame.pack(pady=5)
    
    message_label = Label(message_frame, text="Message:")
    message_label.pack(side=LEFT, padx=5)
    
    message_entry = Entry(message_frame, width=50)
    message_entry.pack(side=LEFT, padx=5)
    
    send_button = Button(
        message_frame,
        text="Send",
        command=lambda: send_message(text, message_entry),
        bg="blue",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=10,
        pady=5
    ) # send button
    send_button.pack(side=LEFT, padx=5)
    
    quit_button = Button(
        message_frame,
        text="Quit",
        command=lambda: quit_chat(text),
        bg="red", 
        fg="white",
        font=("Arial", 10, "bold"),
        padx=10,
        pady=5
    ) # quit button to end chat
    quit_button.pack(side=LEFT, padx=5)
        
    window.mainloop()
    
if __name__ == '__main__':
    gui()