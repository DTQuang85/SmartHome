Hệ Thống Điều Khiển Nhà Thông Minh Bằng Cử Chỉ với Bảo Mật PIN
📋 Tổng Quan Dự Án
Hệ thống điều khiển nhà thông minh dựa trên ESP32-S3 với tính năng nhận diện cử chỉ để điều khiển và bảo mật bằng mã PIN kèm thông báo qua email. Hệ thống bao gồm giao diện web để giám sát và điều khiển, đèn LED RGB báo trạng thái, động cơ servo điều khiển cửa và module relay điều khiển thiết bị điện.

✨ Tính Năng Chính
🔐 Hệ Thống Bảo Mật
Xác thực bằng mã PIN 4 số để truy cập hệ thống

Đèn LED RGB báo trạng thái: Đỏ (khóa) / Xanh lá (mở khóa)

Thông báo qua email cho:

Các lần mở khóa thành công

Các lần nhập sai mật khẩu (kèm mã PIN đã nhập)

Khóa bằng cử chỉ: Cử chỉ xoay ngược chiều kim đồng hồ để khóa hệ thống

🖐️ Điều Khiển Bằng Cử Chỉ (Cảm biến PAJ7620)
Khi hệ thống đang KHÓA:
LÊN/XUỐNG: Di chuyển trên bàn phím số ảo

TRÁI/PHẢI: Di chuyển ngang trên bàn phím số

TIẾN (NEAR): Chọn số hiện tại và nhập vào mã PIN

XOAY CÙNG CHIỀU KĐH: Xóa ký tự cuối cùng trong mã PIN

Khi hệ thống đã MỞ KHÓA:
TRÁI/PHẢI: Chuyển đổi giữa các thiết bị/phòng

LÊN: Bật thiết bị/phòng đang chọn

XUỐNG: Tắt thiết bị/phòng đang chọn

TIẾN (NEAR): Bật TẤT CẢ thiết bị

LÙI (FAR): Tắt TẤT CẢ thiết bị

XOAY NGƯỢC CHIỀU KĐH: Khóa hệ thống

🌐 Giao Diện Web (Phong cách iOS)
Giao diện hiện đại, tối ưu cho điện thoại

Hiển thị bàn phím số khi hệ thống khóa

Bảng điều khiển trực quan khi đã mở khóa:

Danh sách phòng và thiết bị được phân nhóm rõ ràng

Công tắc gạt (toggle) cho từng thiết bị/phòng

Nút ALL ON / ALL OFF

Nút LOCK SYSTEM

Cập nhật thời gian thực mỗi 500ms

Hiển thị cử chỉ hiện tại với biểu tượng trực quan

💡 Thiết Bị Điều Khiển
Đèn 1 (Relay, GPIO 35)

Quạt 1 (Relay, GPIO 7)

Đèn 2 (Relay, GPIO 37)

Quạt 2 (Relay, GPIO 6)

Cửa chính (Servo, GPIO 21)

🏠 Phòng (Nhóm Logic)
Phòng 1: Đèn 1 + Quạt 1

Phòng 2: Đèn 2 + Quạt 2

🔧 Phần Cứng Yêu Cầu
Vi điều khiển: ESP32-S3 (hoặc tương thích)

Cảm biến cử chỉ: PAJ7620 (I2C)

Đèn LED RGB: WS2812/Neopixel (GPIO 48)

Động cơ Servo: Điều khiển cửa (GPIO 21)

Module Relay: 4 relay (GPIO 35, 7, 37, 6)

Nguồn điện: Phù hợp cho ESP32 và các thiết bị

📦 Sơ Đồ Kết Nối
Thiết bị	GPIO	Ghi chú
Cảm biến PAJ7620 SCL	9	I2C Clock
Cảm biến PAJ7620 SDA	8	I2C Data
LED RGB (Neopixel)	48	Data
Servo	21	PWM
Relay Đèn 1	35	Active HIGH
Relay Quạt 1	7	Active HIGH
Relay Đèn 2	37	Active HIGH
Relay Quạt 2	6	Active HIGH
⚙️ Cài Đặt
1. Cấu hình WiFi
python
SSID = "B095"           # Tên WiFi
PASSWORD = "Vien230305@" # Mật khẩu WiFi
2. Cấu hình Email (Gmail)
python
SENDER_EMAIL = "letrivien004@gmail.com"
SENDER_PASSWORD = "qwytkfqpvvvjklqp"  # Mật khẩu ứng dụng Gmail
RECEIVER_EMAIL = "letrivien004@gmail.com"
3. Cấu hình Mã PIN
python
CORRECT_PIN = "2303"  # Mã PIN mặc định
📥 Hướng Dẫn Nạp Code
Cài đặt MicroPython lên ESP32-S3

Tải code lên thiết bị (main.py)

Kết nối phần cứng theo sơ đồ trên

Khởi động lại ESP32

Truy cập giao diện web: Mở trình duyệt và nhập địa chỉ IP của ESP32 (hiển thị trong serial console)

🎮 Cách Sử Dụng
1. Mở khóa hệ thống
Di chuyển trên bàn phím số bằng cử chỉ LÊN/XUỐNG/TRÁI/PHẢI

Dùng cử chỉ TIẾN để chọn số

Nhập đúng mã PIN 4 số để mở khóa (đèn chuyển từ đỏ → xanh)

2. Điều khiển thiết bị (sau khi mở khóa)
Dùng cử chỉ TRÁI/PHẢI để chọn thiết bị/phòng

Dùng cử chỉ LÊN để bật, XUỐNG để tắt

Dùng cử chỉ TIẾN để bật tất cả, LÙI để tắt tất cả

Dùng cử chỉ XOAY NGƯỢC CHIỀU KĐH để khóa lại

3. Sử dụng giao diện web
Khi khóa: Bàn phím số ảo, nhập PIN trực tiếp trên web

Khi mở khóa: Bảng điều khiển với các công tắc gạt

Nhấn nút ALL ON / ALL OFF để điều khiển nhanh

Nhấn LOCK SYSTEM để khóa từ xa

📧 Email Notifications
Hệ thống gửi email thông báo trong các trường hợp:

Mở khóa thành công: "🏠 Smart Home Unlocked"

Nhập sai mật khẩu: "🔐 Security Alert - Wrong Password Attempt" (kèm mã PIN đã nhập)

🔍 Xử Lý Sự Cố Thường Gặp
Không tìm thấy cảm biến PAJ7620

Kiểm tra kết nối I2C (SCL/SDA)

Đảm bảo địa chỉ I2C đúng (0x73)

Không kết nối được WiFi

Kiểm tra SSID và mật khẩu

Đảm bảo tín hiệu WiFi đủ mạnh

Không gửi được email

Kiểm tra mật khẩu ứng dụng Gmail (không phải mật khẩu tài khoản)

Đảm bảo đã bật "Less secure app access" hoặc tạo App Password

Servo không hoạt động

Kiểm tra nguồn điện (servo cần dòng cao)

Đảm bảo chân GPIO đúng (21)

Relay không chuyển trạng thái

Kiểm tra logic active HIGH/LOW

Đo điện áp chân điều khiển

📊 Luồng Hoạt Động
text
Khởi động
    ↓
Kết nối WiFi
    ↓
Khởi tạo cảm biến & thiết bị
    ↓
Web server chạy (thread riêng)
    ↓
Vòng lặp chính:
    ↓
Đọc cử chỉ từ PAJ7620
    ↓
─── Nếu KHÓA ───→ Xử lý điều hướng bàn phím & nhập PIN
│                   ↓
│               Đúng PIN? → Gửi email thông báo → Mở khóa
│                   ↓
│               Sai PIN? → Gửi email cảnh báo
│
─── Nếu MỞ KHÓA ─→ Xử lý điều khiển thiết bị theo cử chỉ
                    ↓
                Cập nhật trạng thái thiết bị
                    ↓
                Giao diện web cập nhật real-time
📝 Ghi Chú
Mã PIN mặc định là 2303 (có thể thay đổi trong code)

Email sử dụng SMTP Gmail với STARTTLS (port 587)

Hệ thống tự động khóa khi khởi động lại

Giao diện web tự động cập nhật mỗi 500ms

🚀 Mở Rộng
Bạn có thể dễ dàng mở rộng hệ thống bằng cách:

Thêm thiết bị mới vào mảng devices

Thêm phòng mới vào mảng rooms

Tùy chỉnh layout keypad

Thêm các hành động cho cử chỉ mới

⚠️ Bảo Mật
Không chia sẻ mã PIN hoặc mật khẩu email

Nên đổi mã PIN mặc định

Sử dụng mật khẩu ứng dụng (App Password) cho Gmail

Đảm bảo mạng WiFi được bảo mật
