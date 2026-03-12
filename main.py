from machine import Pin, I2C, PWM
import time, socket, json, _thread, network
import ssl as ussl
import binascii

# =====================================================
# EMBEDDED UMAIL LIBRARY (NO INSTALLATION NEEDED)
# =====================================================
class SMTP:
    """Simple SMTP client embedded directly in code with improved SSL handling"""
    def __init__(self, server, port, username, password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.sock = None
        self.ssl_sock = None
        self.to_addr = None
        self.from_addr = username
        self.message = ""
    
    def _send(self, data):
        if isinstance(data, str):
            data = data.encode()
        if not data.endswith(b'\r\n'):
            data += b'\r\n'
        self.ssl_sock.write(data)
    
    def _recv(self):
        response = self.ssl_sock.readline()
        return response.decode().strip()
    
    def _recv_multiline(self):
        """Read multi-line SMTP responses (like EHLO after STARTTLS)"""
        lines = []
        while True:
            line = self.ssl_sock.readline().decode().strip()
            lines.append(line)
            # Stop when we get a line that doesn't start with "250-"
            if line and not line.startswith('250-'):
                break
        return '\n'.join(lines)
    
    def _cmd(self, cmd):
        self._send(cmd)
        return self._recv()
    
    def _cmd_multiline(self, cmd):
        """Send command and read multi-line response"""
        self._send(cmd)
        return self._recv_multiline()
    
    def connect(self):
        # Create plain socket first
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)  # Increase timeout
        
        # Get address and connect
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)
        
        # Read initial greeting from plain connection
        response = self.sock.recv(1024)
        print(f"Server greeting: {response.decode()[:50]}")
        
        # Send EHLO on plain connection
        self.sock.send(b'EHLO ESP32\r\n')
        response = self.sock.recv(1024)
        
        # Start TLS
        self.sock.send(b'STARTTLS\r\n')
        response = self.sock.recv(1024)
        print(f"STARTTLS response: {response.decode()[:50]}")
        
        # Wrap with SSL/TLS after STARTTLS
        try:
            import ssl
            self.ssl_sock = ssl.wrap_socket(self.sock, server_hostname=self.server)
        except:
            # Fallback for older MicroPython
            self.ssl_sock = ussl.wrap_socket(self.sock)
    
    def login(self):
        # Send EHLO again on secure connection (will get multi-line response)
        response = self._cmd_multiline('EHLO ESP32')
        print(f"EHLO response: {response[:100]}")
        
        # AUTH LOGIN
        self._cmd('AUTH LOGIN')
        
        # Send username (base64)
        username_b64 = binascii.b2a_base64(self.username.encode()).decode().strip()
        self._cmd(username_b64)
        
        # Send password (base64)
        password_b64 = binascii.b2a_base64(self.password.encode()).decode().strip()
        response = self._cmd(password_b64)
        
        if '235' not in response:
            raise Exception(f"Login failed: {response}")
    
    def to(self, addr):
        self.to_addr = addr
    
    def write(self, text):
        self.message += text
    
    def send(self):
        self.connect()
        self.login()
        self._cmd(f'MAIL FROM: <{self.from_addr}>')
        self._cmd(f'RCPT TO: <{self.to_addr}>')
        self._cmd('DATA')
        self._send(self.message)
        self._cmd('.')
    
    def quit(self):
        try:
            self._cmd('QUIT')
        except:
            pass
        try:
            if self.ssl_sock:
                self.ssl_sock.close()
        except:
            pass
        try:
            if self.sock:
                self.sock.close()
        except:
            pass

# =====================================================
# WIFI STA MODE
# =====================================================
SSID = "B095"
PASSWORD = "Vien230305@"

# =====================================================
# EMAIL CONFIGURATION
# =====================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "letrivien004@gmail.com"
SENDER_PASSWORD = "qwytkfqpvvvjklqp"  # App Password (spaces removed: eklwbwxwajbs)
RECEIVER_EMAIL = "letrivien004@gmail.com"

def send_email(subject, message):
    """Send email notification via SMTP"""
    try:
        print(f"Sending email: {subject}")
        
        smtp = SMTP(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD)
        smtp.to(RECEIVER_EMAIL)
        smtp.write("From: Smart Home Security <{}>\n".format(SENDER_EMAIL))
        smtp.write("To: {}\n".format(RECEIVER_EMAIL))
        smtp.write("Subject: {}\n".format(subject))
        smtp.write("\n")
        smtp.write(message)
        smtp.send()
        smtp.quit()
        
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

try:
    network.WLAN(network.AP_IF).active(False)
except:
    pass

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting WiFi...")
t0 = time.time()
while not wlan.isconnected():
    if time.time() - t0 > 20:
        raise SystemExit("WIFI FAILED")
    time.sleep(0.5)

ESP_IP = wlan.ifconfig()[0]
print("WIFI OK - ESP32 IP:", ESP_IP)

# =====================================================
# RGB LED (WS2812 / NeoPixel)
# =====================================================
try:
    from neopixel import NeoPixel
    rgb_led = NeoPixel(Pin(48), 1)  # GPIO 48, 1 LED
    
    def set_rgb(r, g, b):
        rgb_led[0] = (r, g, b)
        rgb_led.write()
    
    # Khóa = Đỏ
    def rgb_locked():
        set_rgb(255, 0, 0)
    
    # Mở khóa = Xanh lá
    def rgb_unlocked():
        set_rgb(0, 255, 0)
    
    rgb_locked()
except:
    print("RGB LED not available, continuing without it")
    def set_rgb(r, g, b): pass
    def rgb_locked(): pass
    def rgb_unlocked(): pass

# =====================================================
# SECURITY SYSTEM
# =====================================================
CORRECT_PIN = "2303"
is_unlocked = False
entered_pin = ""

# =====================================================
# SERVO (ESP32-S3 PWM FIX)
# =====================================================
class Servo:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.min_us = 500
        self.max_us = 2500

    def _write_us(self, us):
        duty = int(us * 65535 / 20000)
        self.pwm.duty_u16(duty)

    def angle(self, deg):
        deg = max(0, min(180, deg))
        us = self.min_us + (self.max_us - self.min_us) * deg // 180
        self._write_us(us)

    def close(self):
        self.angle(0)

    def open_90(self):
        self.angle(90)

servo = Servo(21)
servo.close()

# =====================================================
# DEVICES
# =====================================================
devices = [
    {"name": "Light 1", "type": "relay", "pin": Pin(35, Pin.OUT), "active": 1, "state": 0},
    {"name": "Fan 1",   "type": "relay", "pin": Pin(7,  Pin.OUT), "active": 1, "state": 0},
    {"name": "Light 2", "type": "relay", "pin": Pin(37, Pin.OUT), "active": 1, "state": 0},
    {"name": "Fan 2",   "type": "relay", "pin": Pin(6,  Pin.OUT), "active": 1, "state": 0},
    {"name": "Main Door", "type": "servo", "state": 0},
]

# =====================================================
# ROOMS (LOGIC GROUP)
# =====================================================
rooms = [
    {"name": "Room 1", "members": ["Light 1", "Fan 1"], "state": 0},
    {"name": "Room 2", "members": ["Light 2", "Fan 2"], "state": 0},
]

# =====================================================
# HELPERS
# =====================================================
def get_device_index(name):
    for i, d in enumerate(devices):
        if d["name"] == name:
            return i
    return None

def device_on(i):
    if not is_unlocked:
        return
    d = devices[i]
    if d["type"] == "relay":
        d["pin"].value(d["active"])
        d["state"] = 1
    else:
        servo.open_90()
        d["state"] = 1

def device_off(i):
    if not is_unlocked:
        return
    d = devices[i]
    if d["type"] == "relay":
        d["pin"].value(1 - d["active"])
        d["state"] = 0
    else:
        servo.close()
        d["state"] = 0

def room_on(i):
    if not is_unlocked:
        return
    for name in rooms[i]["members"]:
        idx = get_device_index(name)
        if idx is not None:
            device_on(idx)
    rooms[i]["state"] = 1

def room_off(i):
    if not is_unlocked:
        return
    for name in rooms[i]["members"]:
        idx = get_device_index(name)
        if idx is not None:
            device_off(idx)
    rooms[i]["state"] = 0

def all_on():
    if not is_unlocked:
        return
    for i in range(len(devices)):
        device_on(i)
    for r in rooms:
        r["state"] = 1

def all_off():
    if not is_unlocked:
        return
    for i in range(len(devices)):
        device_off(i)
    for r in rooms:
        r["state"] = 0

all_off()

# =====================================================
# KEYPAD NAVIGATION
# =====================================================
# Keypad layout:
# [1] [2] [3]
# [4] [5] [6]
# [7] [8] [9]
# [*] [0] [#]
keypad_layout = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]

keypad_row = 0
keypad_col = 0

def get_current_key():
    return keypad_layout[keypad_row][keypad_col]

# =====================================================
# SELECTABLE LIST (CHỈ DÙNG KHI ĐÃ MỞ KHÓA)
# Thứ tự PHẢI khớp với UI display order!
# =====================================================
selectables = [
    {"type": "device", "name": "Main Door"},
    {"type": "room", "name": "Room 1"},
    {"type": "room", "name": "Room 2"},
    {"type": "device", "name": "Light 1"},
    {"type": "device", "name": "Fan 1"},
    {"type": "device", "name": "Light 2"},
    {"type": "device", "name": "Fan 2"},
]

selected = 0
current_gesture = "NONE"

# =====================================================
# PAJ7620 INIT
# =====================================================
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=100000)
PAJ_ADDR = 0x73

def write_reg(r, v):
    i2c.writeto_mem(PAJ_ADDR, r, bytes([v]))

def read_reg(r):
    return i2c.readfrom_mem(PAJ_ADDR, r, 1)[0]

if PAJ_ADDR not in i2c.scan():
    raise SystemExit("PAJ7620 NOT FOUND")

write_reg(0xFF, 0x00)
time.sleep_ms(50)

if read_reg(0x01) != 0x76 or read_reg(0x00) != 0x20:
    raise SystemExit("WRONG SENSOR")

init_regs = [
    (0xEF,0x00),(0x37,0x07),(0x38,0x17),(0x39,0x06),(0x42,0x01),
    (0x46,0x2D),(0x47,0x0F),(0x48,0x3C),(0x49,0x00),(0x4A,0x1E),
    (0x4C,0x20),(0x51,0x10),(0x5E,0x10),(0x60,0x27),(0x80,0x42),
    (0x81,0x44),(0x82,0x04),(0x8B,0x01),(0x90,0x06),(0x95,0x0A),
    (0x96,0x0C),(0x97,0x05),(0x9A,0x14),(0x9C,0x3F),(0xA5,0x19),
    (0xCC,0x19),(0xCD,0x0B),(0xCE,0x13),(0xCF,0x64),(0xD0,0x21),
    (0xEF,0x01),(0x02,0x0F),(0x03,0x10),(0x04,0x02),(0x25,0x01),
    (0x27,0x39),(0x28,0x7F),(0x29,0x08),(0x3E,0xFF),(0x5E,0x3D),
    (0x65,0x96),(0x67,0x97),(0x69,0xCD),(0x6A,0x01),(0x6D,0x2C),
    (0x6E,0x01),(0x72,0x01),(0x73,0x35),(0x77,0x01),(0xEF,0x00),
]
for r, v in init_regs:
    write_reg(r, v)
    time.sleep_ms(2)

# =====================================================
# GESTURE CODES
# =====================================================
G_UP, G_DOWN, G_RIGHT, G_LEFT, G_FORWARD, G_BACKWARD = 1,2,4,8,16,32
G_CLOCKWISE, G_ANTICLOCKWISE = 64, 128

# =====================================================
# WEB UI - MODERN iOS STYLE WITH SECURITY
# =====================================================
HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Secure Gesture Control</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
    color: #fff;
}

.container {
    max-width: 600px;
    margin: 0 auto;
}

.header {
    text-align: center;
    margin-bottom: 30px;
}

.header h1 {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 10px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.security-indicator {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    text-align: center;
}

.security-status {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    border-radius: 30px;
    font-size: 16px;
    font-weight: 600;
}

.security-status.locked {
    background: rgba(255, 59, 48, 0.3);
    border: 2px solid #ff3b30;
}

.security-status.unlocked {
    background: rgba(52, 199, 89, 0.3);
    border: 2px solid #34c759;
}

.led-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    animation: pulse-led 1.5s infinite;
}

.led-indicator.red {
    background: #ff3b30;
    box-shadow: 0 0 10px #ff3b30;
}

.led-indicator.green {
    background: #34c759;
    box-shadow: 0 0 10px #34c759;
}

@keyframes pulse-led {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* KEYPAD SCREEN */
.keypad-container {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.pin-display {
    background: rgba(0,0,0,0.3);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    text-align: center;
    min-height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.pin-dots {
    display: flex;
    gap: 15px;
    justify-content: center;
}

.pin-dot {
    width: 15px;
    height: 15px;
    border-radius: 50%;
    background: rgba(255,255,255,0.3);
    border: 2px solid rgba(255,255,255,0.5);
}

.pin-dot.filled {
    background: #fff;
    border-color: #fff;
}

.keypad-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 15px;
}

.keypad-key {
    aspect-ratio: 1;
    background: rgba(255,255,255,0.2);
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 3px solid transparent;
}

.keypad-key:active {
    transform: scale(0.95);
    background: rgba(255,255,255,0.3);
}

.keypad-key.selected {
    border-color: #fff;
    background: rgba(255,255,255,0.3);
    animation: pulse-key 1s infinite;
}

.keypad-key.special {
    background: rgba(255, 59, 48, 0.3);
    color: #ff3b30;
    font-size: 32px;
}

@keyframes pulse-key {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

.keypad-instruction {
    text-align: center;
    font-size: 13px;
    opacity: 0.8;
    line-height: 1.4;
}

/* CONTROL PANEL (SHOWN WHEN UNLOCKED) */
.control-panel {
    display: none;
}

.control-panel.visible {
    display: block;
}

.status-bar {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
}

.status-label {
    font-size: 14px;
    opacity: 0.9;
    font-weight: 500;
}

.status-value {
    font-size: 16px;
    font-weight: 600;
    background: rgba(255,255,255,0.2);
    padding: 5px 15px;
    border-radius: 12px;
}

/* IMPROVED ITEMS LAYOUT */
.items-container {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.section-header {
    font-size: 14px;
    font-weight: 600;
    opacity: 0.7;
    margin-bottom: 15px;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 0 5px;
}

.section-divider {
    height: 1px;
    background: rgba(255,255,255,0.2);
    margin: 20px 0;
}

.item-card {
    background: rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.item-card:last-child {
    margin-bottom: 0;
}

.item-card.selected {
    border-color: #fff;
    background: rgba(255,255,255,0.2);
    box-shadow: 0 4px 20px rgba(255,255,255,0.2);
}

.item-card.door {
    background: rgba(100, 200, 255, 0.15);
    border-left: 4px solid rgba(100, 200, 255, 0.5);
}

.item-card.door.selected {
    border-color: #64c8ff;
    background: rgba(100, 200, 255, 0.25);
}

.item-card.room {
    background: rgba(255,215,0,0.15);
    border-left: 4px solid rgba(255,215,0,0.5);
}

.item-card.room.selected {
    border-color: #ffd700;
    background: rgba(255,215,0,0.25);
}

.item-info {
    display: flex;
    align-items: center;
    gap: 15px;
    flex: 1;
}

.item-icon {
    width: 45px;
    height: 45px;
    background: rgba(255,255,255,0.2);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
}

.item-card.door .item-icon {
    background: rgba(100, 200, 255, 0.3);
}

.item-card.room .item-icon {
    background: rgba(255,215,0,0.3);
}

.item-details {
    flex: 1;
    min-width: 0;
}

.item-name {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 2px;
}

.item-type {
    font-size: 12px;
    opacity: 0.7;
}

.toggle-switch {
    position: relative;
    width: 51px;
    height: 31px;
    cursor: pointer;
    flex-shrink: 0;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(120,120,128,0.32);
    transition: 0.3s;
    border-radius: 31px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 27px;
    width: 27px;
    left: 2px;
    bottom: 2px;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

input:checked + .slider {
    background-color: #34c759;
}

input:checked + .slider:before {
    transform: translateX(20px);
}

.control-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin-bottom: 15px;
}

.btn {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: none;
    color: #fff;
    padding: 18px;
    border-radius: 16px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.btn:active {
    transform: scale(0.95);
    background: rgba(255,255,255,0.25);
}

.btn.on {
    background: linear-gradient(135deg, #34c759 0%, #30d158 100%);
}

.btn.off {
    background: linear-gradient(135deg, #ff3b30 0%, #ff453a 100%);
}

.btn.lock {
    background: linear-gradient(135deg, #ff9500 0%, #ffb340 100%);
    grid-column: 1 / -1;
}

.gesture-display {
    text-align: center;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 30px;
    margin-top: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.gesture-icon {
    font-size: 48px;
    margin-bottom: 10px;
}

.gesture-text {
    font-size: 24px;
    font-weight: 600;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.selected-indicator {
    animation: pulse 1.5s infinite;
}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🔐 Secure Smart Home</h1>
    </div>

    <div class="security-indicator">
        <div class="security-status locked" id="securityStatus">
            <div class="led-indicator red" id="ledIndicator"></div>
            <span id="lockStatus">LOCKED</span>
        </div>
    </div>

    <!-- KEYPAD (SHOWN WHEN LOCKED) -->
    <div class="keypad-container" id="keypadContainer">
        <div class="pin-display">
            <div class="pin-dots" id="pinDots"></div>
        </div>
        
        <div class="keypad-grid" id="keypadGrid"></div>
    </div>

    <!-- CONTROL PANEL (SHOWN WHEN UNLOCKED) -->
    <div class="control-panel" id="controlPanel">
        <div class="status-bar">
            <div class="status-item">
                <span class="status-label">Selected</span>
                <span class="status-value" id="selectedItem">-</span>
            </div>
        </div>

        <div class="items-container">
            <!-- Main Door Section -->
            <div class="section-header">🚪 Main Access</div>
            <div id="doorSection"></div>
            
            <div class="section-divider"></div>
            
            <!-- Rooms Section -->
            <div class="section-header">🏠 Rooms</div>
            <div id="roomsSection"></div>
            
            <div class="section-divider"></div>
            
            <!-- Individual Devices Section -->
            <div class="section-header">💡 Individual Controls</div>
            <div id="devicesSection"></div>
        </div>

        <div class="control-buttons">
            <button class="btn on" onclick="allOn()">⚡ ALL ON</button>
            <button class="btn off" onclick="allOff()">🔌 ALL OFF</button>
            <button class="btn lock" onclick="lockSystem()">🔒 LOCK SYSTEM</button>
        </div>

        <div class="gesture-display">
            <div class="gesture-icon" id="gestureIcon">👋</div>
            <div class="gesture-text" id="gestureText">Ready</div>
        </div>
    </div>
</div>

<script>
const gestureIcons = {
    'NONE': '👋',
    'LEFT': '👈',
    'RIGHT': '👉',
    'UP': '👆',
    'DOWN': '👇',
    'NEAR': '🤏',
    'FAR': '✋',
    'CLOCKWISE': '🔄',
    'ANTICLOCKWISE': '🔃'
};

const itemIcons = {
    'Main Door': '🚪',
    'Room 1': '🏠',
    'Room 2': '🏠',
    'Light 1': '💡',
    'Fan 1': '🌀',
    'Light 2': '💡',
    'Fan 2': '🌀'
};

// Organized display order
const displaySections = {
    door: [
        {type: 'device', name: 'Main Door'}
    ],
    rooms: [
        {type: 'room', name: 'Room 1'},
        {type: 'room', name: 'Room 2'}
    ],
    devices: [
        {type: 'device', name: 'Light 1'},
        {type: 'device', name: 'Fan 1'},
        {type: 'device', name: 'Light 2'},
        {type: 'device', name: 'Fan 2'}
    ]
};

const keypadLayout = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
];

function renderKeypad(selectedRow, selectedCol) {
    let html = '';
    keypadLayout.forEach((row, r) => {
        row.forEach((key, c) => {
            const isSelected = (r === selectedRow && c === selectedCol);
            const isSpecial = (key === '*' || key === '#');
            const selectedClass = isSelected ? 'selected' : '';
            const specialClass = isSpecial ? 'special' : '';
            html += `<div class="keypad-key ${selectedClass} ${specialClass}">${key}</div>`;
        });
    });
    document.getElementById('keypadGrid').innerHTML = html;
}

function renderPinDots(pinLength) {
    let html = '';
    for (let i = 0; i < 4; i++) {
        const filled = i < pinLength ? 'filled' : '';
        html += `<div class="pin-dot ${filled}"></div>`;
    }
    document.getElementById('pinDots').innerHTML = html;
}

function toggleItem(type, name) {
    fetch(`/toggle/${type}/${name}`).then(() => updateStatus());
}

function allOn() {
    fetch('/allon').then(() => updateStatus());
}

function allOff() {
    fetch('/alloff').then(() => updateStatus());
}

function lockSystem() {
    fetch('/lock').then(() => updateStatus());
}

function getItemState(data, type, name) {
    if (type === 'device') {
        const device = data.devices.find(d => d.name === name);
        return device ? device.state : 0;
    } else {
        const room = data.rooms.find(r => r.name === name);
        return room ? room.state : 0;
    }
}

function isItemSelected(data, type, name) {
    return data.selected_type === type && data.selected_name === name;
}

function createItemCard(item, data) {
    const icon = itemIcons[item.name] || '📱';
    const selected = isItemSelected(data, item.type, item.name);
    const state = getItemState(data, item.type, item.name);
    const checked = state ? 'checked' : '';
    const selectedClass = selected ? 'selected' : '';
    
    let typeClass = '';
    let typeLabel = '';
    if (item.name === 'Main Door') {
        typeClass = 'door';
        typeLabel = 'Access Control';
    } else if (item.type === 'room') {
        typeClass = 'room';
        typeLabel = 'Room Control';
    } else {
        typeClass = 'device';
        typeLabel = 'Device';
    }
    
    return `
        <div class="item-card ${selectedClass} ${typeClass}">
            <div class="item-info">
                <div class="item-icon ${selected ? 'selected-indicator' : ''}">${icon}</div>
                <div class="item-details">
                    <div class="item-name">${item.name}</div>
                    <div class="item-type">${typeLabel}</div>
                </div>
            </div>
            <label class="toggle-switch">
                <input type="checkbox" ${checked} onchange="toggleItem('${item.type}', '${item.name}')">
                <span class="slider"></span>
            </label>
        </div>
    `;
}

function updateStatus() {
    fetch('/status')
        .then(r => r.json())
        .then(data => {
            const isUnlocked = data.unlocked;
            const securityStatus = document.getElementById('securityStatus');
            const ledIndicator = document.getElementById('ledIndicator');
            const lockStatus = document.getElementById('lockStatus');
            const keypadContainer = document.getElementById('keypadContainer');
            const controlPanel = document.getElementById('controlPanel');
            
            if (isUnlocked) {
                securityStatus.classList.remove('locked');
                securityStatus.classList.add('unlocked');
                ledIndicator.classList.remove('red');
                ledIndicator.classList.add('green');
                lockStatus.textContent = 'UNLOCKED';
                keypadContainer.style.display = 'none';
                controlPanel.classList.add('visible');
                
                // Update selected item
                document.getElementById('selectedItem').textContent = data.selected;
                
                // Update gesture
                document.getElementById('gestureIcon').textContent = gestureIcons[data.gesture] || '👋';
                document.getElementById('gestureText').textContent = data.gesture;
                
                // Render sections separately
                let doorHtml = '';
                displaySections.door.forEach(item => {
                    doorHtml += createItemCard(item, data);
                });
                document.getElementById('doorSection').innerHTML = doorHtml;
                
                let roomsHtml = '';
                displaySections.rooms.forEach(item => {
                    roomsHtml += createItemCard(item, data);
                });
                document.getElementById('roomsSection').innerHTML = roomsHtml;
                
                let devicesHtml = '';
                displaySections.devices.forEach(item => {
                    devicesHtml += createItemCard(item, data);
                });
                document.getElementById('devicesSection').innerHTML = devicesHtml;
                
            } else {
                securityStatus.classList.add('locked');
                securityStatus.classList.remove('unlocked');
                ledIndicator.classList.add('red');
                ledIndicator.classList.remove('green');
                lockStatus.textContent = 'LOCKED';
                keypadContainer.style.display = 'block';
                controlPanel.classList.remove('visible');
                
                // Update keypad
                renderKeypad(data.keypad_row, data.keypad_col);
                renderPinDots(data.pin_length);
            }
        });
}

// Update every 500ms
setInterval(updateStatus, 500);
updateStatus();
</script>
</body>
</html>"""

def web_server():
    s = socket.socket()
    s.bind(('', 80))
    s.listen(1)
    print("WEB UI READY")
    while True:
        c,_ = s.accept()
        r = c.recv(1024).decode()

        if "/status" in r:
            global is_unlocked, entered_pin, keypad_row, keypad_col, selected, current_gesture
            
            sel = selectables[selected]
            data = {
                "unlocked": is_unlocked,
                "pin_length": len(entered_pin),
                "keypad_row": keypad_row,
                "keypad_col": keypad_col,
                "selected": sel["name"],
                "selected_type": sel["type"],
                "selected_name": sel["name"],
                "gesture": current_gesture,
                "devices": [
                    {"name":d["name"], "state":d["state"]}
                    for d in devices
                ],
                "rooms": [
                    {"name":rm["name"], "state":rm["state"]}
                    for rm in rooms
                ]
            }
            c.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            c.send(json.dumps(data))

        elif "/toggle/" in r:
            if is_unlocked:
                try:
                    parts = r.split("/toggle/")[1].split()
                    if len(parts) > 0:
                        path = parts[0]
                        if "/" in path:
                            item_type, item_name = path.split("/", 1)
                            item_name = item_name.replace("%20", " ")
                            
                            if item_type == "device":
                                idx = get_device_index(item_name)
                                if idx is not None:
                                    if devices[idx]["state"] == 0:
                                        device_on(idx)
                                    else:
                                        device_off(idx)
                            
                            elif item_type == "room":
                                room_idx = 0 if item_name == "Room 1" else 1
                                if rooms[room_idx]["state"] == 0:
                                    room_on(room_idx)
                                else:
                                    room_off(room_idx)
                except:
                    pass
            c.send("HTTP/1.1 200 OK\r\n\r\n")

        elif "/allon" in r:
            if is_unlocked:
                all_on()
            c.send("HTTP/1.1 200 OK\r\n\r\n")

        elif "/alloff" in r:
            if is_unlocked:
                all_off()
            c.send("HTTP/1.1 200 OK\r\n\r\n")

        elif "/lock" in r:
            is_unlocked = False
            entered_pin = ""
            rgb_locked()
            c.send("HTTP/1.1 200 OK\r\n\r\n")

        else:
            c.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            c.send(HTML)
        c.close()

_thread.start_new_thread(web_server, ())

# =====================================================
# MAIN LOOP - SECURITY LAYER + GESTURE CONTROL
# =====================================================
last = 0
while True:
    g = (read_reg(0x44) << 8) | read_reg(0x43)
    now = time.ticks_ms()

    if g and time.ticks_diff(now, last) > 600:
        
        if not is_unlocked:
            # ===== KEYPAD MODE (LOCKED) =====
            if g == G_UP:
                keypad_row = (keypad_row - 1) % 4
                current_gesture = "UP"
                
            elif g == G_DOWN:
                keypad_row = (keypad_row + 1) % 4
                current_gesture = "DOWN"
                
            elif g == G_LEFT:
                # Vuốt trái → Di chuyển phải trên UI
                keypad_col = (keypad_col + 1) % 3
                current_gesture = "LEFT"
                
            elif g == G_RIGHT:
                # Vuốt phải → Di chuyển trái trên UI
                keypad_col = (keypad_col - 1) % 3
                current_gesture = "RIGHT"
                
            elif g == G_FORWARD:
                # NEAR = Chọn số
                key = get_current_key()
                if key.isdigit() and len(entered_pin) < 4:
                    entered_pin += key
                    print(f"Entered: {entered_pin}")
                    
                    # Kiểm tra PIN
                    if len(entered_pin) == 4:
                        if entered_pin == CORRECT_PIN:
                            is_unlocked = True
                            rgb_unlocked()
                            print("✅ UNLOCKED!")
                            
                            # Send success email notification
                            _thread.start_new_thread(send_email, (
                                "🏠 Smart Home Unlocked",
                                "✅ Your home has been successfully unlocked.\n\n"
                                "Status: Access Granted\n\n"
                                "If this wasn't you, please check your system immediately."
                            ))
                        else:
                            print("❌ WRONG PIN")
                            
                            # Send security alert email
                            _thread.start_new_thread(send_email, (
                                "🔐 Security Alert - Wrong Password Attempt",
                                "🔐 Security Alert!\n\n"
                                "⚠️ Someone just entered an incorrect password on your Smart Home system.\n\n"
                                "Entered PIN: {}\n"
                                "Status: Access Denied\n\n"
                                "Please verify who attempted to access your system.".format(
                                    entered_pin
                                )
                            ))
                            
                            # Nhấp nháy đỏ
                            for _ in range(3):
                                set_rgb(255, 0, 0)
                                time.sleep(0.2)
                                set_rgb(0, 0, 0)
                                time.sleep(0.2)
                            rgb_locked()
                        entered_pin = ""
                current_gesture = "NEAR"
                
            elif g == G_CLOCKWISE:
                # CLOCKWISE = Xóa ký tự cuối
                if len(entered_pin) > 0:
                    entered_pin = entered_pin[:-1]
                    print(f"Deleted (Clockwise), now: {entered_pin}")
                current_gesture = "CLOCKWISE"
        
        else:
            # ===== CONTROL MODE (UNLOCKED) - GIỮ NGUYÊN LOGIC CŨ =====
            if g == G_LEFT:
                selected = (selected - 1) % len(selectables)
                current_gesture = "LEFT"

            elif g == G_RIGHT:
                selected = (selected + 1) % len(selectables)
                current_gesture = "RIGHT"

            elif g == G_UP:
                sel = selectables[selected]
                if sel["type"] == "device":
                    idx = get_device_index(sel["name"])
                    if idx is not None:
                        device_on(idx)
                else:
                    room_idx = 0 if sel["name"] == "Room 1" else 1
                    room_on(room_idx)
                current_gesture = "UP"

            elif g == G_DOWN:
                sel = selectables[selected]
                if sel["type"] == "device":
                    idx = get_device_index(sel["name"])
                    if idx is not None:
                        device_off(idx)
                else:
                    room_idx = 0 if sel["name"] == "Room 1" else 1
                    room_off(room_idx)
                current_gesture = "DOWN"

            elif g == G_FORWARD:
                all_on()
                current_gesture = "NEAR"

            elif g == G_BACKWARD:
                all_off()
                current_gesture = "FAR"
            
            elif g == G_ANTICLOCKWISE:
                # ANTICLOCKWISE = Lock system (quay ngược chiều kim đồng hồ)
                is_unlocked = False
                entered_pin = ""
                rgb_locked()
                print("🔒 System locked via ANTICLOCKWISE gesture")
                current_gesture = "ANTICLOCKWISE"

        last = now
    time.sleep(0.05)
