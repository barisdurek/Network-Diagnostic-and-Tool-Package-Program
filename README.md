# Network Diagnostic and Tool Package Program
* It developed on Windows environment with Python.
* There are two versions of the program. Firstly it developed to run on terminal environment. Then a GUI designed and the terminal version adapted to this GUI version.
* In GUI version, there is no seperate error management module. If there is an error or exception case, program throws error immediately.(terminal version does not have error management system.)
* Note: If you try to run the code in Visual Studio Code, usually it gives error because of reading settings.json, so I recommend you to run the code on your computer's terminal.

### Required libraries before using
```
pip install ntplib
```
* for SNTP time synchronization. (already between the program files but recommended to download anyway.)
  
```
pip install ifaddr
```
* for listing the network interfaces and their IP addresses. <br>
[github repo link of the library](https://github.com/ifaddr/ifaddr ) <br>

### Program Details
* The purpose of this program is to get a hands-on experience in basic socket programming, network diagnostics, time synchronization, and error management. In the program, small applications (such as machine information extraction, echo testing, SNTP client, socket settings, and error  management), which are developed separately, integrated to create a comprehensive network diagnostic tool.

### Program Structure and Modules
The program consists of the following four main modules:

* Machine Information Module :
This module gives local machine’s hostname, IP address, network interfaces, and related information.

* Echo Test Module :
Performs basic connection tests by setting up a simple echo client/server structure.
User selects if its client or server.
On the server side, creates a socket and listen on a specified port.
On the client side, connects to the server and receive the same data that was sent.
Compares the sent and received data.
Display the connection test result on the screen.

* SNTP Time Synchronization Module :
Retrieves the current time from an SNTP (Simple Network Time Protocol) server on the Internet.
Also shows your local computer's time information to compare with the SNTP.

* Simple Chat Module :
Provides a basic chat environment for the user.
Allow the user to choose whether to run in server or client mode.
Establishes the connection. 
Transfers strings over the established connection and display them on the screen.
Displays chat messages on the screen and saves them to file messages.txt.

* Settings Module :
Allows the users to change and display socket timeout, buffer size, blocking/non-blocking mode settings.
Settings part work with settings.json file. It reads the settings from json and if user change them, writes back to json file.

### How to run the program?
* Just run the Python file on terminal. For Python 3.13:
```
py project-gui.py
py project-terminal.py
```
* Or:
```
python project-gui.py
python project-terminal.py
```
* (Depends on your Python version and terminal. You can check your version on cmd with python --version. Also it may change in Visual Studio Code terminal)
### And here it is:<br>
* Terminal version<br>
![Ekran görüntüsü 2025-04-22 170244](https://github.com/user-attachments/assets/093c5919-9e46-4468-ad7e-4a42c44bc4db)
* GUI version<br>
![Ekran görüntüsü 2025-03-24 124542](https://github.com/user-attachments/assets/caa7e616-3c74-47e1-9664-18dac2142552)
