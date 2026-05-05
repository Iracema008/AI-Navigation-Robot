# AI-Navigation-Robot

A Raspberry Pi 4 robot that navigates a warehouse grid using AI search algorithms.

## Hardware
- Raspberry Pi 4
- L298N Motor Controllers
- 2 DC Motors
- Ultrasonic Sensor
- tcrt_5000
- tcs_34725
- 7.4v Li-ion Battery, Portable Charger for Pi,  5v

## Running the Program

### 1. Clone Repo
    git clone https://github.com/Iracema008/AI-Navigation-Robot.git

### 2. Create Virtual Environment
    python3 -m venv r_venv
    
### 3. Activate Environment
    source r_venv/bin/activate

### 4. Install Dependencies
    pip install-r requirements.txt

### 5. Run Program
    python3 main.py

# Running the Simulator (Any Computer)

### 1. Clone Repo
    git clone https://github.com/Iracema008/AI-Navigation-Robot.git
    cd AI-Navigation-Robot

### 2. Create Virtual Environment
    python3 -m venv r_venv
    source r_venv/bin/activate

### 3. Install Dependencies
    pip install flask

### 4. Run Simulator
    python3 simulator.py

### 5. Open in Browser
    http://localhost:5050

### Simulator Controls
- Select pickup nodes using the checkboxes
- Click edges on the graph to mark them as blocked (obstacles)
- Press Start to run SA + A* and watch the robot navigate
- Press Reset to clear and start over