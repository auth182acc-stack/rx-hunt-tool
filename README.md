# RX Hunt - Advanced Roblox Group Reconnaissance Tool

RX Hunt เป็นเครื่องมือ Python ที่ใช้ในการรวบรวมข้อมูล (reconnaissance) ของกลุ่ม Roblox โดยเฉพาะอย่างยิ่งในการดึงข้อมูลผู้ใช้ที่อยู่ในบทบาทต่างๆ ภายในกลุ่ม เครื่องมือนี้ถูกออกแบบมาให้มีประสิทธิภาพและสามารถจัดการกับการจำกัดอัตรา (rate limiting) ของ API ของ Roblox ได้อย่างชาญฉลาด

## คุณสมบัติหลัก

*   **การดึงข้อมูลบทบาทและผู้ใช้**: ดึงข้อมูลบทบาททั้งหมดในกลุ่ม Roblox และผู้ใช้ที่เกี่ยวข้องกับแต่ละบทบาท
*   **การจัดการ Rate Limiting**: มีกลไกการลองใหม่ (retry) แบบ exponential backoff และการป้องกัน rate limiting เพื่อให้การดึงข้อมูลเป็นไปอย่างราบรื่น
*   **การแคชข้อมูลผู้ใช้**: แคชข้อมูลผู้ใช้ที่ดึงมาแล้วเพื่อลดจำนวนคำขอ API ซ้ำซ้อน
*   **การส่งออกข้อมูล**: บันทึกผลลัพธ์เป็นไฟล์ JSON และ CSV เพื่อการวิเคราะห์เพิ่มเติม
*   **ตัวเลือกการกรอง**: สามารถกรองข้อมูลตามชื่อบทบาทที่ต้องการได้
*   **การรองรับ Proxy**: สามารถกำหนดค่า proxy เพื่อใช้ในการส่งคำขอได้
*   **อินเทอร์เฟซที่ใช้งานง่าย**: แสดงผลด้วยสีสันและ ASCII art (สามารถปิดได้) พร้อมแถบความคืบหน้า (progress bar) สำหรับการดึงข้อมูลผู้ใช้

## การติดตั้ง

1.  **Clone repository**: 
    ```bash
    git clone https://github.com/auth182acc-stack/rx-hunt-tool.git
    cd rx-hunt-tool
    ```

2.  **สร้างและเปิดใช้งาน virtual environment (แนะนำ)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **ติดตั้ง dependencies**: 
    ```bash
    pip install -r requirements.txt
    ```
    (หมายเหตุ: ไฟล์ `requirements.txt` จะถูกสร้างขึ้นในขั้นตอนถัดไป)

## การใช้งาน

RX Hunt ต้องการ `GROUP_ID` ของกลุ่ม Roblox ที่คุณต้องการตรวจสอบ คุณสามารถระบุ `GROUP_ID` ได้สองวิธี:

1.  **ผ่าน Command-line argument**: ใช้ `--group-id` ตามด้วย ID ของกลุ่ม
2.  **ผ่าน Environment variable**: ตั้งค่าตัวแปรสภาพแวดล้อมชื่อ `GROUP_ID` ในไฟล์ `.env`

### ตัวอย่างการใช้งานพื้นฐาน

```bash
python rx-hunt-minify.py --group-id 1234567
```

### ตัวเลือก Command-line

| Argument           | Description                                                                 | Default Value       |
| :----------------- | :-------------------------------------------------------------------------- | :------------------ |
| `--group-id`       | Roblox Group ID (จำเป็นต้องระบุ)                                            | (ไม่มี)              |
| `--role <name>`    | กรองข้อมูลเฉพาะบทบาทที่มีชื่อที่ระบุ                                         | (ดึงข้อมูลทุกบทบาท) |
| `--quiet`          | แสดงเฉพาะสรุปผลลัพธ์เท่านั้น (ไม่แสดงรายชื่อผู้ใช้แต่ละคน)                  | `False`             |
| `--no-ascii`       | ปิดการแสดง ASCII art                                                        | `False`             |
| `--output <path>`  | กำหนดไดเรกทอรีสำหรับบันทึกไฟล์ผลลัพธ์                                       | `~/storage/shared`  |
| `--csv`            | บันทึกผลลัพธ์เป็นไฟล์ CSV นอกเหนือจาก JSON                                  | `False`             |
| `--verbose`        | เปิดใช้งานการบันทึกข้อมูลแบบละเอียด                                         | `False`             |
| `--fast`           | ปิดการแสดงสีและ ASCII art เพื่อการทำงานที่เร็วขึ้น                          | `False`             |
| `--proxy`          | ใช้ proxy สำหรับคำขอ (ต้องกำหนดค่าในไฟล์ `.env`)                            | `False`             |
| `--validate-only`  | ตรวจสอบ Group ID เท่านั้นแล้วออก                                            | `False`             |

### การกำหนดค่า Environment Variables

คุณสามารถสร้างไฟล์ `.env` ในไดเรกทอรีเดียวกับสคริปต์เพื่อกำหนดค่า `GROUP_ID` และการตั้งค่า proxy:

```dotenv
GROUP_ID=1234567
HTTP_PROXY=http://your_proxy_address:port
HTTPS_PROXY=http://your_proxy_address:port
```

## การพัฒนา

### Dependencies

*   `aiohttp`
*   `asyncio`
*   `argparse`
*   `python-dotenv`
*   `tqdm`
*   `rich`

คุณสามารถสร้างไฟล์ `requirements.txt` ได้โดยใช้คำสั่ง:

```bash
pip freeze > requirements.txt
```

## ข้อควรระวัง

*   การใช้งานเครื่องมือนี้อาจถูกจำกัดโดย API ของ Roblox หากมีการส่งคำขอมากเกินไป โปรดใช้งานอย่างระมัดระวัง
*   ตรวจสอบให้แน่ใจว่าคุณมีสิทธิ์ในการเข้าถึงข้อมูลกลุ่มที่คุณพยายามดึงมา

## ผู้พัฒนา

lxn.dev

