import random
import time
import matplotlib.pyplot as plt

class EnhancedCruiseControl:
    def __init__(self):
        self.cruise_speed = float(input("ENTER INITIAL CRUISE SPEED (KM/HR): "))
        self.current_lane = random.randint(1, 3)
        self.current_speed = self.cruise_speed
        self.step_counter = 0
        self.obstacle = {'exists': False, 'speed': None, 'duration': 0}
        self.lane_change_cooldown = 0
        self.obstacle_cooldown = 0
        
        # safety parameters
        self.safety_distance = 200  # 200m safety threshold
        self.radar_range = 250      # 250m detection range
        
        # Data storage
        self.time_steps = []
        self.speed_history = []
        self.obstacle_history = []
        self.lane_history = []
        self.gear_history = []

    def run_simulation(self):
        print(f"\nInitialized in Lane {self.current_lane} | Target Speed: {self.cruise_speed} km/h")
        print(f"Safety Distance: {self.safety_distance}m | Radar Range: {self.radar_range}m")
        print("Simulation starting...\n")
        
        for _ in range(500):
            self.step_counter += 1
            self._update_obstacle()
            self._simulate_step()
            self._store_data()
            time.sleep(0.01)
            self._maintain_speed_limits()
            self._update_timers()
        
        self.plot_results()

    def _calculate_gear(self):
        speed = self.current_speed
        if speed < 20: return 1
        elif 20 <= speed < 40: return 2
        elif 40 <= speed < 60: return 3
        elif 60 <= speed < 80: return 4
        else: return 5

    def _update_obstacle(self):
        if self.obstacle_cooldown <= 0 and not self.obstacle['exists']:
            scenario = random.choices(
                ['slower', 'free', 'faster'],
                weights=[4, 2, 2],
                k=1
            )[0]
            
            if scenario == 'free': return
                
            #  ±60 km/h obstacle range
            min_speed = max(60, self.current_speed - 60)
            max_speed = min(150, self.current_speed + 60)
            
            self.obstacle['speed'] = random.randint(
                int(min_speed) if scenario == 'slower' else int(self.current_speed),
                int(self.current_speed) if scenario == 'slower' else int(max_speed)
            )
            
            self.obstacle['exists'] = True
            self.obstacle['duration'] = random.randint(5, 15)
            self.obstacle_cooldown = 10
            print(f"New obstacle: {self.obstacle['speed']} km/h (Safety: {self.safety_distance}m)")

    def _simulate_step(self):
        if self.obstacle['exists']:
            if self.obstacle['duration'] <= 0:
                print(f"Step {self.step_counter}: Obstacle cleared")
                self.obstacle['exists'] = False
                return
                
            if self.current_speed > self.obstacle['speed']:
                self._handle_slower_obstacle()
            elif self.current_speed < self.obstacle['speed']:
                print(f"Step {self.step_counter}: Faster obstacle ({self.obstacle['speed']} km/h)")
                if random.random() < 0.3:
                    print(f"Step {self.step_counter}: Overtaking initiated")
                    self.obstacle['exists'] = False
            else:
                self._attempt_lane_change()
        else:
            self._maintain_cruise_speed()

    def _maintain_cruise_speed(self):
        if self.current_speed < self.cruise_speed:
            self.current_speed = min(self.cruise_speed, self.current_speed + 5)
            print(f"Step {self.step_counter}: Accelerating to {self.current_speed} km/h")
        else:
            print(f"Step {self.step_counter}: Maintaining {self.current_speed} km/h")

    def _handle_slower_obstacle(self):
        self.current_speed = max(self.obstacle['speed'], self.current_speed - 5)
        action = "Decelerating" if self.current_speed > self.obstacle['speed'] else "Speed matched"
        print(f"Step {self.step_counter}: {action} to {self.current_speed} km/h")

    def _attempt_lane_change(self):
        if random.random() < 0.5:
            new_lane = self._get_available_lane()
            if new_lane:
                print(f"Step {self.step_counter}: Switching to Lane {new_lane}")
                self.current_lane = new_lane
                self.obstacle['exists'] = False
                self.lane_change_cooldown = 5
            else:
                print(f"Step {self.step_counter}: Lanes blocked")
        else:
            print(f"Step {self.step_counter}: Lane change aborted")

    def _get_available_lane(self):
        lanes = []
        if self.current_lane == 1: lanes.append(2)
        elif self.current_lane == 2: lanes.extend([1, 3])
        else: lanes.append(2)
        return random.choice(lanes) if lanes else None

    def _maintain_speed_limits(self):
        self.current_speed = max(60, min(150, self.current_speed))

    def _update_timers(self):
        if self.obstacle['exists']: self.obstacle['duration'] -= 1
        if self.obstacle_cooldown > 0: self.obstacle_cooldown -= 1
        if self.lane_change_cooldown > 0: self.lane_change_cooldown -= 1

    def _store_data(self):
        self.time_steps.append(self.step_counter * 0.1)
        self.speed_history.append(self.current_speed)
        self.lane_history.append(self.current_lane)
        self.obstacle_history.append(self.obstacle['speed'] if self.obstacle['exists'] else None)
        self.gear_history.append(self._calculate_gear())

    def plot_results(self):
        plt.figure(figsize=(12, 10))
        
        # Speed plot
        plt.subplot(4, 1, 1)
        plt.plot(self.time_steps, self.speed_history, 'b-', label='Actual Speed')
        plt.axhline(y=self.cruise_speed, color='r', linestyle='--', label='Target')
        plt.ylabel('Speed (km/h)')
        plt.title('Speed Profile')
        plt.legend()
        plt.grid(True)
        
        # Obstacle plot
        plt.subplot(4, 1, 2)
        obstacle_times = [t for t, obs in zip(self.time_steps, self.obstacle_history) if obs]
        obstacle_speeds = [obs for obs in self.obstacle_history if obs]
        if obstacle_speeds:
            plt.scatter(obstacle_times, obstacle_speeds, c='orange', marker='x', label='Obstacles')
            plt.ylim(min(obstacle_speeds)-10, max(obstacle_speeds)+10)
        plt.ylabel('Obstacle Speed')
        plt.legend()
        plt.grid(True)
        
        # Gear plot
        plt.subplot(4, 1, 3)
        plt.step(self.time_steps, self.gear_history, where='post', color='purple')
        plt.ylabel('Gear')
        plt.yticks([1,2,3,4,5], ['1st','2nd','3rd','4th','5th'])
        plt.grid(True)
        
        # Lane plot
        plt.subplot(4, 1, 4)
        plt.step(self.time_steps, self.lane_history, where='post', color='g')
        plt.ylabel('Lane')
        plt.yticks([1,2,3], ['Left','Center','Right'])
        plt.xlabel('Time (seconds)')
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    print("=== CRUISE CONTROL SIMULATION ===")
    simulator = EnhancedCruiseControl()
    simulator.run_simulation()
    print("\nSimulation completed successfully!")
