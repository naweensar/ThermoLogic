import serial
import time
import cantera as ct  # Ensure 'cantera' is correctly installed

# Replace 'COM3' with the correct port for your Arduino
arduino_port = "COM3"
baud_rate = 9600

initial_run = True

p1d = 0
p2d = 0
t1d = 0
t2d = 0
effd = 0 
# Initialize the WaterWithTransport object
w = ct.Water()

# Connect to the Arduino
ser = serial.Serial(arduino_port, baud_rate, timeout=1)
time.sleep(2)  # Allow time for the connection to initialize

try:
    while True:
        if ser.in_waiting > 0:
            # Read a line of data from the serial port
            line = ser.readline().decode('utf-8').strip()
            
            # Skip non-numeric or debug messages
            if not any(char.isdigit() for char in line):
                print(f"Non-numeric data received: {line}")
                continue

            # Split the comma-separated string into individual values
            try:
                p1, p2, t1, t2 = map(float, line.split(","))
                print(f"Pressure 1 (Pa): {p1}")
                print(f"Pressure 2 (Pa): {p2}")
                print(f"Temperature 1 (°k): {t1}")
                print(f"Temperature 2 (°k): {t2}")
                print("-" * 40)

                w.TP = t1, p1+101325  # Ensure the attribute name 'TP' exists in WaterWithTransport
                h1 = w.h
                s2s = w.s
                Q2s = 1.0
                w.PQ = p2+101325, Q2s
                h2s = w.h
                w.TP = t2, p2
                h2 = w.h
                
                print(h1)
                print(h2s)
                print(h2)
                
                eff = -1*(h1 - h2)/(h1 - h2s)  # Adjust as needed
                uniterg = (h1 - h2) * eff

                if (initial_run):
                    p1d = p1
                    p2d = p2
                    t1d = t1
                    t2d = t2
                    effd = eff
                    initial_run = False

                # Perform calculations using the data
                
               
                
                if(effd<0.93 and not initial_run):
                    t1d+=t1d*0.02*(0.93-effd)
                    p1d+=p1d*0.02*(0.93-effd)
                    p2d-=p2d*0.02*(0.93-effd)
                    
                w.TP = t1d,p1d
                h1d = w.h
                s2s = w.s
                Q2s = 1.0
                w.PQ = p2d+101325, Q2s
                h2sd = w.h
                w.TP = t2d, p2d
                h2d = w.h
                effd = -1*(h1d - h2d)/(h1d - h2sd)
                
                print(f"Efficiency: {eff}")
                print(f"Unit Energy: {uniterg}")
                print(f"Efficiency fix: {effd}")
                print(f"Unit Energy: {(h1d-h2d)*effd}")
                

            except ValueError as e:
                print("Error parsing data:", e)

finally:
    ser.close()
