
# SnakeMail

Email app for cock.li email addresses
## 🛠️ Requirements

Before installing, make sure you have these dependencies installed on your system:

-   **Python 3.10+**: The core language used to build the app.
    
-   **Tkinter**: Needed for the graphical pop-ups and UI elements.
    
    -   **Linux (Xubuntu/Ubuntu)**: `sudo apt install python3-tk`
        
    -   **Windows/Mac**: Usually comes with the standard Python installer.
        

## 🛡️ Privacy & Security

-   **Password Safety**: This app is designed for cock.li addresses.
    
-   **Config Files**: Never share your `.snakemail.config.json` file as it contains your login credentials.
    
-   **Research Use**: This tool was developed for documenting online group operations and secure communication.


## How to install

For **Linux** (Xubuntu/Ubuntu/Debian):

1.  **Download the script**:
    

Bash

```
wget https://raw.githubusercontent.com/beecausehoney/SnakeMail/main/snakemail.py

```

_OR_

Bash

```
curl -O https://raw.githubusercontent.com/beecausehoney/SnakeMail/main/snakemail.py

```

2.  **Make it a command**: Run these lines to move the file and give it permission to run:
    

Bash

```
sudo mv snakemail.py /usr/local/bin/snakemail
sudo chmod +x /usr/local/bin/snakemail

```

**Usage**: Just type `snakemail` in your terminal to start!

## Microsoft windows
There are two ways to install either

1. Simply download it
2. Run `Invoke-WebRequest -Uri "https://raw.githubusercontent.com/beecausehoney/SnakeMail/main/snakemail.py" -OutFile "snakemail.py"`then simply create a bat named "snakemail.bat" and insert `@echo off python "%~dp0snakemail.py" %*   
` 
## Mac Os
### **How to Install on macOS**

1.  **Open Terminal**: They can find this in Applications > Utilities or by searching with Spotlight (Cmd + Space).
    
2.  **Download the script**:
    
    
    
    ```
    curl -O https://raw.githubusercontent.com/beecausehoney/SnakeMail/main/snakemail.py
    
    ```
    
3.  **Make it a command**: Run these lines to move the file and give it permission to run:
    



```
    sudo mv snakemail.py /usr/local/bin/snakemail
    sudo chmod +x /usr/local/bin/snakemail
```

## Android
**How to install on Android:**

1.  Install **Termux** from F-Droid.
    
2.  Run these commands:
    



```
pkg update && pkg upgrade
pkg install python wget
wget https://raw.githubusercontent.com/beecausehoney/SnakeMail/main/snakemail.py
chmod +x snakemail.py

```

3.  To make it a command in Termux:
    



```
mv snakemail.py $PREFIX/bin/snakemail
```
## Chrome OS

 enable the **Linux (Beta)** feature in settings. Once enabled follow The Linux commands above **Linux/Xubuntu** instructions exactly.

