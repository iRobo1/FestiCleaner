#!/usr/bin/env python3
"""
Fake Arduino Simulator - Generates realistic robot telemetry for testing
Sends data to the backend API without needing real hardware
"""

import json
import time
import random
import urllib.request
import urllib.error
from datetime import datetime
import argparse

class FakeArduino:
    """Simulates an Arduino UNO Q with realistic sensor data"""

    def __init__(self, api_url="http://localhost:8000", update_interval=1.0):
        self.api_url = api_url
        self.update_interval = update_interval
        self.battery = 95.0  # Start at 95%
        self.temperature = 22.0  # Celsius
        self.humidity = 58.0  # %RH (typical Mediterranean evening)
        self.position_x = 0.4
        self.position_y = 0.4
        self.time_elapsed = 0
        self.is_running = False
        # Boustrophedon sweep state for "normal" mode.
        self.sweep_dir_x = 1
        self.sweep_step_x = 0.75   # m per tick (≈ 1.5× the cleaning radius)
        self.sweep_row_step = 1.0  # m between rows
        self.sweep_min = 0.4
        self.sweep_max = 9.6

    def get_telemetry(self, mode="normal"):
        """Generate realistic sensor data based on mode"""

        # Simulate battery drain (0.25% per reading for visible demo progress)
        self.battery -= random.uniform(0.2, 0.3)
        self.battery = max(0, min(100, self.battery))

        # Simulate temperature variation (+/- 0.5°C drift)
        temp_drift = random.uniform(-0.5, 0.5)
        self.temperature += temp_drift
        self.temperature = max(15, min(35, self.temperature))

        # Simulate humidity (loosely anti-correlated with temperature drift).
        humidity_drift = random.uniform(-1.2, 1.2) - temp_drift * 0.6
        self.humidity += humidity_drift
        self.humidity = max(20, min(95, self.humidity))

        # Movement — depends on mode.
        if mode == "stationary":
            self.position_x = 5.0
            self.position_y = 5.0
        elif mode == "circular":
            angle = (self.time_elapsed / 100) * 2 * 3.14159
            self.position_x = 5.0 + 3 * __import__('math').cos(angle)
            self.position_y = 5.0 + 3 * __import__('math').sin(angle)
        else:
            # Boustrophedon sweep: lawnmower pattern across the whole floor.
            # Covers the 10×10 m area in ~130 ticks (~2 min @ 1 Hz) so the
            # tile reveal builds visibly throughout the demo.
            self.position_x += self.sweep_dir_x * self.sweep_step_x
            if self.position_x >= self.sweep_max:
                self.position_x = self.sweep_max
                self.sweep_dir_x = -1
                self.position_y += self.sweep_row_step
            elif self.position_x <= self.sweep_min:
                self.position_x = self.sweep_min
                self.sweep_dir_x = 1
                self.position_y += self.sweep_row_step
            if self.position_y >= self.sweep_max:
                # Reached the far end — loop back to the start.
                self.position_x = self.sweep_min
                self.position_y = self.sweep_min
                self.sweep_dir_x = 1
            # A little organic jitter so the path doesn't look perfectly mechanical.
            self.position_x += random.uniform(-0.08, 0.08)
            self.position_y += random.uniform(-0.08, 0.08)
            self.position_x = max(0, min(10, self.position_x))
            self.position_y = max(0, min(10, self.position_y))

        # Mode-specific battery/temperature adjustments.
        if mode == "low_battery":
            self.battery = max(0, self.battery - 1.0)
        elif mode == "hot":
            self.temperature = min(45, self.temperature + 0.5)
        elif mode == "cold":
            self.temperature = max(10, self.temperature - 0.5)

        return {
            "battery": round(self.battery, 2),
            "temperature": round(self.temperature, 2),
            "humidity": round(self.humidity, 2),
            "position": {
                "x": round(self.position_x, 2),
                "y": round(self.position_y, 2)
            }
        }

    def send_telemetry(self, telemetry):
        """Send telemetry data to the backend API (stdlib only — no requests dep)."""
        endpoint = f"{self.api_url}/api/robot/telemetry"
        body = json.dumps(telemetry).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                if 200 <= resp.status < 300:
                    return True, "OK"
                return False, f"HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return False, f"Connection refused (is backend running?): {e.reason}"
        except Exception as e:
            return False, str(e)

    def run(self, mode="normal", duration=None, verbose=True):
        """
        Run the simulator

        Args:
            mode: "normal", "low_battery", "hot", "cold", "stationary", "circular"
            duration: Seconds to run (None = infinite)
            verbose: Print updates to console
        """
        self.is_running = True
        start_time = time.time()

        if verbose:
            print(f"🤖 Starting Fake Arduino Simulator")
            print(f"   API: {self.api_url}")
            print(f"   Mode: {mode}")
            print(f"   Interval: {self.update_interval}s")
            print(f"   Duration: {'∞' if duration is None else f'{duration}s'}")
            print("=" * 60)

        iteration = 0

        try:
            while self.is_running:
                iteration += 1
                self.time_elapsed += self.update_interval

                # Check duration
                if duration and (time.time() - start_time) > duration:
                    break

                # Generate and send telemetry
                telemetry = self.get_telemetry(mode)
                success, message = self.send_telemetry(telemetry)

                # Display status
                status_icon = "✓" if success else "✗"
                timestamp = datetime.now().strftime("%H:%M:%S")

                if verbose:
                    print(
                        f"{status_icon} [{timestamp}] "
                        f"Battery: {telemetry['battery']:6.2f}% | "
                        f"Temp: {telemetry['temperature']:6.2f}°C | "
                        f"Pos: ({telemetry['position']['x']:6.2f}, {telemetry['position']['y']:6.2f}) | "
                        f"{message}"
                    )

                # Wait for next update
                time.sleep(self.update_interval)

        except KeyboardInterrupt:
            if verbose:
                print("\n⏸  Simulator stopped by user")
        finally:
            self.is_running = False
            if verbose:
                print(f"📊 Summary: {iteration} readings sent in {time.time() - start_time:.1f}s")

    def stop(self):
        """Stop the simulator"""
        self.is_running = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fake Arduino Simulator for testing the Robot Backend"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Update interval in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--mode",
        choices=["normal", "low_battery", "hot", "cold", "stationary", "circular"],
        default="normal",
        help="Simulation mode (default: normal)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Duration in seconds (default: infinite)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output"
    )

    args = parser.parse_args()

    # Create and run simulator
    arduino = FakeArduino(
        api_url=args.url,
        update_interval=args.interval
    )

    print(f"\n🚀 Fake Arduino Simulator Starting...\n")

    arduino.run(
        mode=args.mode,
        duration=args.duration,
        verbose=not args.quiet
    )
