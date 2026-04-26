import time
import traceback
import requests # Ensure requests is installed: pip install requests

# Create a local state to store the latest values
real_robot_data = {
    "battery": 98.0,
    "temperature": 25.5,
    "humidity": 45.0,
    "position": {"x": 0.0, "y": 0.0}
}

try:
    print("Python: Booting up...")
    from arduino.app_utils import App, Bridge
    from arduino.app_bricks.web_ui import WebUI
    from arduino.app_bricks.video_objectdetection import VideoObjectDetection
    from datetime import datetime, UTC
    
    print("Python: Imports successful! Setting up Web UI...")
    ui = WebUI()
    
    print("Python: Setting up Camera...")
    detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)
    
    # Power state
    state = {"on": True}

    # --- HELPER FUNCTIONS ---

    def send_to_backend():
        """Helper to push the current real_robot_data to the dashboard"""
        try:
            # We use a short timeout so the robot doesn't freeze if the backend is down
            requests.post("http://localhost:8000/api/robot/telemetry", json=real_robot_data, timeout=0.5)
        except Exception as e:
            # We don't want to crash the whole robot just because the website is down
            print(f" Backend unreachable: {e}")

    def on_power(sid, on):
        state["on"] = bool(on)
        print(f"[festiclean] power → {'on' if state['on'] else 'off'}")
        power_val = 1 if state["on"] else 0
        Bridge.call("setPowerState", power_val)

    def print_cpp_step(step):
        print(f" [C++ BRAIN] JUST ENTERED STEP: {step}")

    def print_cpp_dist(dist):
        print(f" [DISTANCE] Target is : {dist} mm away.")

    def print_cpp_temp(temp):
        print(f" TEMPERATURE : {temp} °C.")
        val = round(temp, 1)
        # Update LOCAL Arduino Web UI
        ui.send_message("thermo_data", message={"temperature": val})
        # Update Global State for your colleague's dashboard
        real_robot_data["temperature"] = val
        send_to_backend()

    def print_cpp_humidity(humidity):
        print(f" HUMIDITY : {humidity} %.")
        val = round(humidity, 1)
        # Update LOCAL Arduino Web UI
        ui.send_message("thermo_data", message={"humidity": val})
        # Update Global State for your colleague's dashboard
        real_robot_data["humidity"] = val
        send_to_backend()

    def send_detections_to_ui(detections: dict):
        if not state["on"]:
            return 
        for key, values in detections.items():
            for value in values:
                if key in ["cup", "bottle", "bowl", "toilet"]:
                    bbox = value.get("bounding_box_xyxy")
                    if bbox and len(bbox) == 4:
                        obj_x = (bbox[0] + bbox[2]) / 2
                        obj_y = (bbox[1] + bbox[3]) / 2
                        
                        obj_id = 1 if key in ["cup", "bottle"] else 2
                        
                        print(f"[festiclean]  SEES: {key} | X: {int(obj_x)}")
                        Bridge.call("updateTarget", obj_id, int(obj_x), int(obj_y))
                
                # Send graphical detection to local UI
                entry = {
                    "content": key,
                    "confidence": value.get("confidence"),
                    "timestamp": datetime.now(UTC).isoformat()
                }
                ui.send_message("detection", message=entry)

    # --- REGISTRATION ---
    
    ui.on_message("power", on_power)
    ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))
    
    Bridge.provide("logStep", print_cpp_step)
    Bridge.provide("distanceTraget", print_cpp_dist)
    Bridge.provide("tempSensor", print_cpp_temp)
    Bridge.provide("humiditySensor", print_cpp_humidity)

    detection_stream.on_detect_all(send_detections_to_ui)
    
    print("Python: Everything initialized perfectly. Running App loop...")
    App.run()

except Exception as e:
    print("\n" + "="*40)
    print("🚨 PYTHON CRASHED! HERE IS THE ERROR:")
    traceback.print_exc()
    print("="*40 + "\n")
    time.sleep(60)