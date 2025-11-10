import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle, Wedge
import matplotlib.transforms as transforms

class MotorcycleVisualization:
    def __init__(self):
        self.fig = plt.figure(figsize=(15, 10))
        self.setup_layout()
        
    def setup_layout(self):
        # Main motorcycle view
        self.ax_bike = plt.subplot2grid((3, 4), (0, 0), colspan=2, rowspan=2)
        self.ax_bike.set_xlim(-3, 3)
        self.ax_bike.set_ylim(-1, 3)
        self.ax_bike.set_aspect('equal')
        self.ax_bike.set_title('Motorcycle Stability Control - Live View', fontsize=14, fontweight='bold')
        self.ax_bike.axis('off')
        
        # Critical parameters
        self.ax_params = plt.subplot2grid((3, 4), (0, 2), colspan=2)
        self.ax_params.axis('off')
        
        # Rider inputs
        self.ax_inputs = plt.subplot2grid((3, 4), (1, 2))
        self.ax_inputs.set_title('Rider Inputs')
        self.ax_inputs.set_ylim(0, 100)
        
        # MSC interventions
        self.ax_msc = plt.subplot2grid((3, 4), (1, 3))
        self.ax_msc.set_title('MSC Interventions')
        self.ax_msc.set_ylim(0, 100)
        
        # Status messages
        self.ax_status = plt.subplot2grid((3, 4), (2, 0), colspan=4)
        self.ax_status.axis('off')
        
    def draw_motorcycle(self, lean_angle, speed, msc_active=False, risk_level=0):
        self.ax_bike.clear()
        self.ax_bike.set_xlim(-3, 3)
        self.ax_bike.set_ylim(-1, 3)
        self.ax_bike.set_aspect('equal')
        self.ax_bike.axis('off')
        
        # Transform for leaning
        base_transform = self.ax_bike.transData
        rotation = transforms.Affine2D().rotate_deg(lean_angle)
        transform = rotation + base_transform
        
        # Motorcycle body - color based on risk
        if risk_level > 0.7:
            body_color = 'red'
        elif risk_level > 0.4:
            body_color = 'orange'
        else:
            body_color = 'black'
            
        body = Rectangle((-0.1, 0.3), 0.2, 1.2, transform=transform, 
                        facecolor=body_color, alpha=0.8)
        self.ax_bike.add_patch(body)
        
        # Wheels
        front_wheel = Circle((-0.8, 0.3), 0.3, transform=transform, facecolor='black', alpha=0.7)
        rear_wheel = Circle((0.8, 0.3), 0.3, transform=transform, facecolor='black', alpha=0.7)
        self.ax_bike.add_patch(front_wheel)
        self.ax_bike.add_patch(rear_wheel)
        
        # Road surface
        self.ax_bike.axhline(y=0, color='gray', linewidth=3)
        
        # Speed indicator
        speed_color = 'red' if speed > 80 else 'orange' if speed > 60 else 'lightblue'
        self.ax_bike.text(-2.5, 2.5, f'Speed: {speed:.0f} km/h', fontsize=12, 
                         bbox=dict(facecolor=speed_color, alpha=0.7))
        
        # Lean angle indicator
        lean_color = 'red' if abs(lean_angle) > 40 else 'orange' if abs(lean_angle) > 30 else 'green'
        lean_indicator = Wedge((2, 2), 0.5, 90-lean_angle-10, 90-lean_angle+10, 
                              facecolor=lean_color, alpha=0.7)
        self.ax_bike.add_patch(lean_indicator)
        self.ax_bike.text(1.5, 1.5, f'Lean: {lean_angle:.0f}°', fontsize=10)
        
        # Risk indicator
        risk_x = 0
        risk_y = 2.2
        risk_width = 2.0
        risk_height = 0.2
        self.ax_bike.add_patch(Rectangle((risk_x, risk_y), risk_width, risk_height, 
                                       facecolor='white', edgecolor='black'))
        self.ax_bike.add_patch(Rectangle((risk_x, risk_y), risk_width * risk_level, risk_height, 
                                       facecolor=lean_color, alpha=0.8))
        self.ax_bike.text(risk_x + risk_width/2, risk_y + risk_height/2, 'RISK', 
                         ha='center', va='center', fontsize=10, fontweight='bold')
        
        # MSC status
        status_color = 'red' if msc_active else 'green'
        status_text = 'MSC ACTIVE!' if msc_active else 'Stable'
        self.ax_bike.text(0, 2.5, status_text, fontsize=14, fontweight='bold',
                         bbox=dict(facecolor=status_color, alpha=0.8), ha='center')

class MSCController:
    def __init__(self):
        self.risk_threshold = 0.3
        self.max_lean = 45
        self.max_safe_speed_in_corner = 80
        
    def calculate_risk(self, speed, lean_angle, throttle, brake, dt):
        """Calculate dynamic risk level (0-1) based on multiple factors"""
        risk = 0.0
        
        # Speed risk (higher speed = higher risk)
        speed_risk = min(speed / 120.0, 1.0)
        risk += speed_risk * 0.3
        
        # Lean angle risk
        lean_risk = min(abs(lean_angle) / self.max_lean, 1.0)
        risk += lean_risk * 0.4
        
        # Combined braking + leaning risk (very dangerous)
        if brake > 0.2 and abs(lean_angle) > 20:
            combined_risk = (brake * 0.5) + (abs(lean_angle) / self.max_lean * 0.5)
            risk += combined_risk * 0.3
            
        # High throttle in corner risk
        if throttle > 50 and abs(lean_angle) > 25:
            throttle_risk = (throttle / 100.0) * (abs(lean_angle) / self.max_lean)
            risk += throttle_risk * 0.2
            
        return min(risk, 1.0)
    
    def calculate_interventions(self, risk, current_throttle, current_brake, speed, lean_angle):
        """Calculate throttle and brake limits based on risk level"""
        throttle_limit = 100
        brake_limit = 1.0
        
        if risk > self.risk_threshold:
            # Progressive intervention based on risk level
            intervention_strength = (risk - self.risk_threshold) / (1 - self.risk_threshold)
            
            # Limit throttle more aggressively at higher risk
            throttle_reduction = intervention_strength * 0.8  # Up to 80% reduction
            throttle_limit = current_throttle * (1 - throttle_reduction)
            
            # Limit braking based on lean angle (braking while leaned is dangerous)
            if abs(lean_angle) > 15:
                brake_reduction = intervention_strength * min(abs(lean_angle) / self.max_lean, 0.7)
                brake_limit = current_brake * (1 - brake_reduction)
                
            # Emergency intervention for extreme cases
            if risk > 0.8:
                throttle_limit = max(throttle_limit, 10)  # Minimum 10% throttle for control
                brake_limit = max(brake_limit, 0.1)  # Minimum braking for control
                
        return throttle_limit, brake_limit

def create_dynamic_scenario():
    """Create a realistic riding scenario with varied inputs"""
    time_steps = 400
    time = np.linspace(0, 40, time_steps)
    
    # Create varied speed profile
    speed = np.ones(time_steps) * 60
    # Acceleration phases
    speed[50:100] = np.linspace(60, 90, 50)
    speed[150:200] = np.linspace(60, 100, 50)
    # Braking phases
    speed[250:300] = np.linspace(80, 40, 50)
    speed[350:380] = np.linspace(70, 30, 30)
    
    # Add random speed variations
    for i in range(1, time_steps):
        speed[i] += np.random.normal(0, 1.5)
    speed = np.clip(speed, 10, 120)
    
    # Create realistic lean angle profile (cornering)
    lean = np.zeros(time_steps)
    # Corner 1: Gentle right curve
    lean[80:150] = np.linspace(0, -25, 70)
    lean[150:220] = np.linspace(-25, 0, 70)
    # Corner 2: Sharp left curve
    lean[230:280] = np.linspace(0, 35, 50)
    lean[280:330] = np.linspace(35, 0, 50)
    # Corner 3: S-curve
    lean[340:370] = np.linspace(0, -30, 30)
    lean[370:400] = np.linspace(-30, 20, 30)
    
    # Add random lean variations
    lean += np.random.normal(0, 2, time_steps)
    lean = np.clip(lean, -45, 45)
    
    # Create dynamic throttle inputs
    throttle = np.ones(time_steps) * 30
    # Acceleration bursts
    throttle[40:80] = np.linspace(30, 80, 40)
    throttle[140:180] = np.linspace(30, 90, 40)
    throttle[320:350] = np.linspace(30, 70, 30)
    # Add random throttle variations
    throttle += np.random.normal(0, 10, time_steps)
    throttle = np.clip(throttle, 0, 100)
    
    # Create realistic brake inputs
    brake = np.zeros(time_steps)
    # Emergency braking
    brake[100:120] = 0.8
    brake[295:310] = 0.9
    brake[375:390] = 0.7
    # Gentle braking
    brake[200:210] = 0.3
    brake[350:355] = 0.4
    # Add random brake variations
    brake += np.random.normal(0, 0.05, time_steps)
    brake = np.clip(brake, 0, 1)
    
    # Initialize MSC controller
    msc = MSCController()
    
    # Simulate MSC interventions
    msc_active = np.zeros(time_steps, dtype=bool)
    throttle_limited = np.zeros(time_steps)
    brake_limited = np.zeros(time_steps)
    risk_level = np.zeros(time_steps)
    
    for i in range(time_steps):
        # Calculate current risk
        current_risk = msc.calculate_risk(
            speed[i], lean[i], throttle[i], brake[i], 0.1
        )
        risk_level[i] = current_risk
        
        # Calculate MSC interventions
        throttle_limit, brake_limit = msc.calculate_interventions(
            current_risk, throttle[i], brake[i], speed[i], lean[i]
        )
        
        # Apply limits
        throttle_limited[i] = min(throttle[i], throttle_limit)
        brake_limited[i] = min(brake[i], brake_limit)
        
        # Check if MSC is actively intervening
        msc_active[i] = (throttle_limited[i] < throttle[i] - 1) or (brake_limited[i] < brake[i] - 0.05)
    
    return {
        'time': time,
        'speed': speed,
        'lean_angle': lean,
        'throttle_input': throttle,
        'throttle_output': throttle_limited,
        'brake_input': brake,
        'brake_output': brake_limited,
        'msc_active': msc_active,
        'risk_level': risk_level
    }

def animate_ride(scenario_data):
    viz = MotorcycleVisualization()
    msc = MSCController()
    
    def update(frame):
        # Clear dynamic axes
        viz.ax_params.clear()
        viz.ax_inputs.clear()
        viz.ax_msc.clear()
        viz.ax_status.clear()
        viz.ax_params.axis('off')
        viz.ax_status.axis('off')
        
        current_data = {key: values[frame] for key, values in scenario_data.items()}
        
        # Calculate current risk for visualization
        current_risk = msc.calculate_risk(
            current_data['speed'], 
            current_data['lean_angle'],
            current_data['throttle_input'],
            current_data['brake_input'],
            0.1
        )
        
        # Draw motorcycle with risk-based coloring
        viz.draw_motorcycle(
            lean_angle=current_data['lean_angle'],
            speed=current_data['speed'],
            msc_active=scenario_data['msc_active'][frame],
            risk_level=current_risk
        )
        
        # Parameters display
        viz.ax_params.text(0.1, 0.9, 'CRITICAL PARAMETERS', fontsize=16, fontweight='bold', 
                          transform=viz.ax_params.transAxes)
        viz.ax_params.text(0.1, 0.7, f"Speed: {current_data['speed']:.0f} km/h", fontsize=12,
                          transform=viz.ax_params.transAxes)
        viz.ax_params.text(0.1, 0.6, f"Lean Angle: {current_data['lean_angle']:.0f}°", fontsize=12,
                          transform=viz.ax_params.transAxes)
        viz.ax_params.text(0.1, 0.5, f"Risk Level: {current_risk:.2f}", fontsize=12,
                          color='red' if current_risk > 0.5 else 'orange' if current_risk > 0.3 else 'green',
                          transform=viz.ax_params.transAxes)
        
        # Rider inputs bar chart
        inputs = ['Throttle', 'Brake']
        input_values = [current_data['throttle_input'], current_data['brake_input'] * 100]
        output_values = [current_data['throttle_output'], current_data['brake_output'] * 100]
        
        x_pos = np.arange(len(inputs))
        bar_width = 0.35
        
        bars1 = viz.ax_inputs.bar(x_pos - bar_width/2, input_values, bar_width, 
                                 color=['green', 'red'], alpha=0.7, label='Rider Input')
        bars2 = viz.ax_inputs.bar(x_pos + bar_width/2, output_values, bar_width,
                                 color=['lightgreen', 'pink'], alpha=0.7, label='After MSC')
        
        viz.ax_inputs.set_xticks(x_pos)
        viz.ax_inputs.set_xticklabels(inputs)
        viz.ax_inputs.set_ylim(0, 100)
        viz.ax_inputs.set_ylabel('Input %')
        viz.ax_inputs.legend()
        viz.ax_inputs.grid(True, alpha=0.3)
        
        # MSC interventions
        interventions = ['Throttle\nLimit', 'Brake\nLimit']
        intervention_strength = [
            max(0, (current_data['throttle_input'] - current_data['throttle_output']) / current_data['throttle_input'] * 100) if current_data['throttle_input'] > 0 else 0,
            max(0, (current_data['brake_input'] - current_data['brake_output']) / current_data['brake_input'] * 100) if current_data['brake_input'] > 0 else 0
        ]
        
        intervention_colors = ['orange' if strength > 0 else 'gray' for strength in intervention_strength]
        bars = viz.ax_msc.bar(interventions, intervention_strength, color=intervention_colors, alpha=0.7)
        viz.ax_msc.set_ylim(0, 100)
        viz.ax_msc.set_ylabel('Reduction %')
        viz.ax_msc.grid(True, alpha=0.3)
        
        # Status messages
        if scenario_data['msc_active'][frame]:
            reasons = []
            if current_data['throttle_output'] < current_data['throttle_input']:
                reasons.append("throttle reduction")
            if current_data['brake_output'] < current_data['brake_input']:
                reasons.append("brake modulation")
                
            status_msg = f"⚠️ MSC ACTIVE: {', '.join(reasons)} for stability!"
            viz.ax_status.text(0.05, 0.7, status_msg, fontsize=14, color='red', fontweight='bold',
                              transform=viz.ax_status.transAxes)
            
            if current_risk > 0.7:
                viz.ax_status.text(0.05, 0.4, "HIGH RISK: Extreme intervention required!", fontsize=12, color='darkred',
                                  transform=viz.ax_status.transAxes)
            elif current_risk > 0.4:
                viz.ax_status.text(0.05, 0.4, "MEDIUM RISK: Moderate intervention", fontsize=12, color='orange',
                                  transform=viz.ax_status.transAxes)
        else:
            viz.ax_status.text(0.05, 0.7, "✅ Riding stable - MSC monitoring", fontsize=14, color='green',
                              transform=viz.ax_status.transAxes)
            if current_risk > 0.2:
                viz.ax_status.text(0.05, 0.4, "⚠️ Caution: Risk level increasing", fontsize=12, color='orange',
                                  transform=viz.ax_status.transAxes)
        
        viz.ax_status.text(0.05, 0.1, f"Time: {scenario_data['time'][frame]:.1f}s", fontsize=10,
                          transform=viz.ax_status.transAxes)
        
        plt.tight_layout()
    
    anim = animation.FuncAnimation(viz.fig, update, frames=len(scenario_data['time']), 
                                  interval=100, repeat=True)
    return anim

def plot_performance_summary(scenario_data):
    """Enhanced performance summary with risk analysis"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Speed, Lean and Risk
    ax1.plot(scenario_data['time'], scenario_data['speed'], 'b-', linewidth=2, label='Speed')
    ax1.set_ylabel('Speed (km/h)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_ylim(0, 130)
    ax1.grid(True, alpha=0.3)
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(scenario_data['time'], scenario_data['lean_angle'], 'r-', linewidth=2, label='Lean Angle')
    ax1_twin.fill_between(scenario_data['time'], 0, scenario_data['risk_level'] * 100, 
                         alpha=0.3, color='orange', label='Risk Level')
    ax1_twin.set_ylabel('Lean Angle (°) / Risk (%)', color='r')
    ax1_twin.tick_params(axis='y', labelcolor='r')
    ax1_twin.set_ylim(-50, 100)
    
    ax1.set_title('Speed, Lean Angle & Risk Level')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    # Plot 2: MSC Interventions
    ax2.plot(scenario_data['time'], scenario_data['msc_active'].astype(float) * 50, 'r-', 
             linewidth=3, label='MSC Active')
    ax2.fill_between(scenario_data['time'], 0, scenario_data['msc_active'].astype(float) * 50, 
                    alpha=0.3, color='red', label='Intervention Period')
    ax2.set_ylim(0, 60)
    ax2.set_ylabel('MSC Status')
    ax2.set_xlabel('Time (s)')
    ax2.set_title('MSC Interventions Timeline')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Throttle Control
    ax3.plot(scenario_data['time'], scenario_data['throttle_input'], 'g-', linewidth=2, 
             label='Rider Throttle', alpha=0.7)
    ax3.plot(scenario_data['time'], scenario_data['throttle_output'], 'r--', linewidth=2, 
             label='MSC Throttle', alpha=0.9)
    ax3.fill_between(scenario_data['time'], 
                    scenario_data['throttle_output'], 
                    scenario_data['throttle_input'],
                    where=(scenario_data['throttle_input'] > scenario_data['throttle_output']),
                    alpha=0.3, color='red', label='Throttle Reduction')
    ax3.set_ylabel('Throttle %')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylim(0, 100)
    ax3.set_title('Throttle Control: Rider vs MSC')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Brake Control
    ax4.plot(scenario_data['time'], scenario_data['brake_input'] * 100, 'b-', linewidth=2, 
             label='Rider Brake', alpha=0.7)
    ax4.plot(scenario_data['time'], scenario_data['brake_output'] * 100, 'r--', linewidth=2, 
             label='MSC Brake', alpha=0.9)
    ax4.fill_between(scenario_data['time'], 
                    scenario_data['brake_output'] * 100, 
                    scenario_data['brake_input'] * 100,
                    where=(scenario_data['brake_input'] > scenario_data['brake_output']),
                    alpha=0.3, color='red', label='Brake Reduction')
    ax4.set_ylabel('Brake %')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylim(0, 100)
    ax4.set_title('Brake Control: Rider vs MSC')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Enhanced performance statistics
    total_interventions = np.sum(scenario_data['msc_active'])
    high_risk_time = np.sum(scenario_data['risk_level'] > 0.7) * 0.1
    medium_risk_time = np.sum(scenario_data['risk_level'] > 0.4) * 0.1
    
    total_throttle_reduction = np.sum(np.maximum(0, scenario_data['throttle_input'] - scenario_data['throttle_output']))
    total_brake_reduction = np.sum(np.maximum(0, scenario_data['brake_input'] - scenario_data['brake_output']))
    
    print("\n" + "="*60)
    print("ENHANCED MSC PERFORMANCE SUMMARY")
    print("="*60)
    print(f"Total riding time: {scenario_data['time'][-1]:.1f} seconds")
    print(f"MSC interventions: {total_interventions} events")
    print(f"High risk situations: {np.sum(scenario_data['risk_level'] > 0.7)}")
    print(f"Maximum risk level: {np.max(scenario_data['risk_level']):.2f}")
    print(f"Average risk level: {np.mean(scenario_data['risk_level']):.2f}")
    print(f"\nTotal throttle reduction: {total_throttle_reduction:.0f}%·s")
    print(f"Total brake reduction: {total_brake_reduction:.2f}·s")
    print(f"Maximum lean angle: {np.max(np.abs(scenario_data['lean_angle'])):.1f}°")
    print(f"Maximum speed: {np.max(scenario_data['speed']):.0f} km/h")
    
    safety_score = 100 - (high_risk_time / scenario_data['time'][-1] * 100)
    intervention_efficiency = 100 - (total_interventions / len(scenario_data['time']) * 100)
    
    print(f"\nSafety Score: {safety_score:.1f}%")
    print(f"Intervention Efficiency: {intervention_efficiency:.1f}%")
    
    if safety_score > 85:
        print("🎯 EXCELLENT: MSC effectively maintained safety!")
    elif safety_score > 70:
        print("✅ GOOD: MSC provided adequate protection")
    else:
        print("⚠️ NEEDS IMPROVEMENT: Consider more aggressive interventions")

# Generate and run the enhanced simulation
print("Creating Enhanced Motorcycle Stability Control Simulation...")
print("This simulation features:")
print("• Dynamic throttle and brake inputs")
print("• Realistic cornering scenarios") 
print("• Risk-based MSC interventions")
print("• Progressive throttle and brake limiting")

scenario = create_dynamic_scenario()

print("\nStarting Animation - Watch for MSC interventions when:")
print("• Risk level increases (orange/red risk bar)")
print("• Braking while leaned over")
print("• High speed in corners")
print("• Aggressive acceleration in turns")

# Create animation
anim = animate_ride(scenario)

# After animation, show performance summary
plt.show()

print("\nGenerating Enhanced Performance Summary...")
plot_performance_summary(scenario)
