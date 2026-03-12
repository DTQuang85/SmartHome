# 🏠 Hệ Thống Nhà Thông Minh Điều Khiển Bằng Cử Chỉ

## 📋 Giới thiệu

Dự án xây dựng hệ thống **Smart Home sử dụng ESP32-S3** cho phép điều khiển thiết bị bằng **cử chỉ tay** kết hợp **xác thực bằng mã PIN**.
Hệ thống có giao diện web để giám sát và điều khiển, đồng thời gửi **thông báo email khi có sự kiện bảo mật**.

---

# ✨ Tính năng chính

## 🔐 Hệ thống bảo mật

* Xác thực bằng **mã PIN 4 số**
* Đèn **LED RGB báo trạng thái**

  * 🔴 Đỏ: hệ thống khóa
  * 🟢 Xanh lá: hệ thống đã mở khóa
* Gửi **email thông báo**

  * Khi mở khóa thành công
  * Khi nhập sai mật khẩu (kèm mã PIN đã nhập)
* Cử chỉ **xoay ngược chiều kim đồng hồ** để khóa lại hệ thống

---

# 🖐️ Điều khiển bằng cử chỉ

Sử dụng **cảm biến PAJ7620** để nhận diện cử chỉ.

## Khi hệ thống đang khóa

* ⬆️⬇️ : Di chuyển trên bàn phím số ảo
* ⬅️➡️ : Di chuyển ngang bàn phím
* ✋ Near : Chọn số hiện tại
* 🔄 Xoay cùng chiều KĐH : Xóa ký tự cuối

## Khi hệ thống đã mở khóa

* ⬅️➡️ : Chuyển thiết bị / phòng
* ⬆️ : Bật thiết bị
* ⬇️ : Tắt thiết bị
* ✋ Near : Bật tất cả thiết bị
* ✋ Far : Tắt tất cả thiết bị
* 🔄 Xoay ngược KĐH : Khóa hệ thống

---

# 🌐 Giao diện Web

Giao diện web được thiết kế **tối ưu cho điện thoại (phong cách iOS)**.

Chức năng:

* Bàn phím số khi hệ thống khóa
* Bảng điều khiển thiết bị khi đã mở khóa
* Công tắc bật/tắt thiết bị
* Nút **ALL ON / ALL OFF**
* Nút **LOCK SYSTEM**
* Hiển thị cử chỉ đang nhận diện
* Cập nhật trạng thái **real-time mỗi 500ms**

---

# 💡 Thiết bị điều khiển

| Thiết bị  | GPIO |
| --------- | ---- |
| Đèn 1     | 35   |
| Quạt 1    | 7    |
| Đèn 2     | 37   |
| Quạt 2    | 6    |
| Servo cửa | 21   |

---

# 🏠 Phòng (nhóm thiết bị)

**Phòng 1**

* Đèn 1
* Quạt 1

**Phòng 2**

* Đèn 2
* Quạt 2

---

# 🔧 Phần cứng sử dụng

* ESP32-S3
* Cảm biến cử chỉ **PAJ7620**
* LED RGB **WS2812 / Neopixel**
* Servo điều khiển cửa
* Module Relay 4 kênh

---

# 📦 Sơ đồ kết nối

| Thiết bị    | GPIO         |
| ----------- | ------------ |
| PAJ7620 SCL | 9            |
| PAJ7620 SDA | 8            |
| LED RGB     | 48           |
| Servo       | 21           |
| Relay       | 35, 7, 37, 6 |

---

# ⚙️ Cấu hình

## WiFi

```python
SSID = "B095"
PASSWORD = "Vien230305@"
```

## Email

```python
SENDER_EMAIL = "example@gmail.com"
SENDER_PASSWORD = "app_password"
RECEIVER_EMAIL = "example@gmail.com"
```

## Mã PIN

```python
CORRECT_PIN = "2303"
```

---

# 📥 Cài đặt

1. Cài **MicroPython cho ESP32-S3**
2. Upload file `main.py`
3. Kết nối phần cứng theo sơ đồ
4. Khởi động lại ESP32
5. Truy cập web bằng **địa chỉ IP của ESP32**

---

# 🎮 Cách sử dụng

### Mở khóa

1. Di chuyển trên bàn phím bằng cử chỉ
2. Dùng cử chỉ **Near** để chọn số
3. Nhập đúng PIN để mở khóa

### Điều khiển thiết bị

* ⬅️➡️ : chọn thiết bị
* ⬆️ : bật
* ⬇️ : tắt

### Điều khiển qua web

* Toggle từng thiết bị
* ALL ON / ALL OFF
* LOCK SYSTEM

---

# 📧 Email Notification

Hệ thống gửi email khi:

* 🏠 **Smart Home Unlocked**
* 🔐 **Security Alert – Wrong Password Attempt**

---

# 🔍 Xử lý lỗi

**Không nhận cảm biến**

* Kiểm tra I2C
* Kiểm tra địa chỉ 0x73

**Không kết nối WiFi**

* Kiểm tra SSID
* Kiểm tra tín hiệu mạng

**Không gửi email**

* Sử dụng Gmail App Password

---

# 🚀 Hướng phát triển

* Thêm thiết bị mới
* Thêm phòng mới
* Tùy chỉnh layout keypad
* Thêm các cử chỉ điều khiển mới

---

# ⚠️ Lưu ý bảo mật

* Không chia sẻ mã PIN
* Không công khai mật khẩu email
* Nên đổi PIN mặc định
* Sử dụng **App Password cho Gmail**

---

# 👨‍💻 Tác giả

DTQuang85
