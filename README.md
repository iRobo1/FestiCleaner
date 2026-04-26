# FestiCleaner
![A photo of the FestiCleaner robot.](Thumbnail3.jpg)

Our FestiCleaner robot autonomously identifies, locates, and cleans trash in real-time, and presents data in an intuitive dashboard. Built using an Arduino Uno Q and recycled cardboard, jar lids, etc. The robot's primary use-case is to clean festivals after events.

## How to Run
1. Connect the robot and a computer to the same network (with appropriate device discovery settings). Firewalls, protected WiFi networks, etc. may cause issues. Self-hosting a hotspot on a phone should work.
2. Configure the Arduino Uno Q to automatically connect to the WiFi network. The following commands may be useful:<br>
Get the list of saved networks: <br>
`nmcli -t -f TYPE,UUID,NAME con` <br>
Delete a specific network. Use this ONLY on the main external network, like HackUPC or phone's hotspot: <br>
`sudo nmcli c delete <UUID>` <br>
Connect to a new network: <br>
`sudo nmcli dev wifi connect <WiFi-SSID> password <WiFi-password>`<br>
3. To start the robot, connect first the camera to the Arduino and then the battery.
4. With our hotspot, the dashboard can be accessed at [http://192.168.106.126:7000/](http://192.168.106.126:7000/).


## Project Description
### The vision 
Barcelona is known for its "festes majors", vibrant street festivals that turn neighborhoods into living art galleries. However, the aftermath often leaves plazas covered in plastic waste. FestiClean is a smart, autonomous rover designed to navigate the morning-after a street concert, identifying and collecting abandoned plastic cups and bottles to keep our city’s streets clean and sustainable. 

## How it Works 
FestiClean uses a multi-brain architecture to bridge the gap between low-level hardware and high-level AI: 
- Computer Vision (The Eyes): Using the on-board camera and an optimized COCO-SSD object detection model, the robot scans the environment in real-time. It ignores static furniture and bystanders, focusing specifically on bottles and cups. 
- Precision Navigation (The Brain): Once a target is spotted, the robot switches to a Pulse-Steering State Machine. It uses a Distance (ToF) sensor to approach the waste with millimeter precision, stopping exactly when the object is within reach of its custom-built gripper. 
- Environmental Monitoring (The Safety): Designed for the hot Mediterranean summer, the robot features a Thermo sensor. It monitors local temperature and humidity, sending live telemetry to the cloud. If the temperature gets too hot, the system alerts operators via the dashboard.

## The Tech Stack 
We built a full-stack robotics ecosystem from the ground up: 
- Hardware: Arduino Uno Q + Modulino Distance & Thermo Sensors + DC Motors + Servos. 
- Embedded Logic: C++ State Machine for high-speed motor control and sensor polling. 
- Edge AI & Bridge: A Python-based "Robot Brain" that runs Computer Vision and forwards data via HTTP POST. 
- Backend: A FastAPI server (Python) that manages a SQLite database and broadcasts live data via WebSockets. 
- Frontend: A high-performance React + Vite dashboard featuring a live video HUD, real-time telemetry gauges, and a remote "kill switch" for safety.

## Key Features 
- Autonomous Pick-and-Place: From "Search" mode to "Drop-off," the robot handles the entire waste lifecycle.
- Zone-Based Tracking: Advanced motor logic that overcomes physical friction through discrete time-pulse steering.
- Live Dashboard: Operators can monitor the FestiCleaner from a single interface, seeing exactly what the robot sees.
- Sustainability-First: Built to tackle the specific plastic-waste profile of urban street festivals. 



