# HackUPC-2026

## Notes about Arduino Uno Q

IP4 addresses assigned by different networks to the Arduino Uno Q: <br>
http://localhost:7000/ (laptop's hotspot) <br>
http://192.168.106.126:7000/ (phone's hotspot - currently only working one with camera) <br>
http://10.5.247.75:7000/ (hackupc's network) <br>

To change the network that the Arduino Uno Q will connect to: <br>
Get the list of saved networks: <br>
`nmcli -t -f TYPE,UUID,NAME con` <br>
Delete a specific network. Use this ONLY on the main external network, like HackUPC or phone's hotspot: <br>
`sudo nmcli c delete <UUID>` <br>
Connect to a new network: <br>
`sudo nmcli dev wifi connect <WiFi-SSID> password <WiFi-password>`

Arduino Uno Q's password: 123456789

The Arduino Uno Q's camera cannot be connected while the Arduino is connected to the laptop (only one USB connection can be used at a time).
