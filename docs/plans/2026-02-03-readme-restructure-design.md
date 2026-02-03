# Design: Tái cấu trúc README

## Mục tiêu

Tách README thành 2 file phục vụ 2 đối tượng khác nhau:
- **README.md** → Người dùng cuối (cài đặt + sử dụng)
- **README.developer.md** → Người tạo library/addon

## README.md (Người dùng cuối)

### Cấu trúc

```
# Corun

> Chạy shell scripts dễ dàng từ terminal

## Cài đặt
## Bắt đầu nhanh (3 lệnh cơ bản)
## Quick Reference (bảng tóm tắt)
## Tạo Library? → Link đến README.developer.md
```

### Nội dung chi tiết

**Cài đặt:**
- `pip install -e .` (development)
- `pipx install corun` (production - coming soon)

**Bắt đầu nhanh:**
- `corun library list` - Xem libraries có sẵn
- `corun <library> <command>` - Chạy lệnh từ library
- `corun <script>` - Chạy standalone script

**Quick Reference (bảng):**
| Lệnh | Mô tả |
|------|-------|
| `corun --help` | Xem trợ giúp |
| `corun -v` | Xem version |
| `corun library list` | Danh sách libraries |
| `corun library info <id>` | Chi tiết library |
| `corun library install <path>` | Cài library |
| `corun library remove <id>` | Gỡ library |
| `corun completion [shell]` | Cài đặt tab completion |

---

## README.developer.md (Người tạo Library)

### Cấu trúc

```
# Corun - Hướng dẫn tạo Library

## Cấu trúc thư mục
## metadata.json Schema
## Ví dụ 1: Library đơn giản
## Ví dụ 2: Library phức tạp
## Ví dụ 3: Standalone script
## Best Practices
## Troubleshooting
```

### Nội dung chi tiết

**Cấu trúc thư mục:**
```
~/.corun/addons/
├── my_lib/              # Library (có metadata.json)
│   ├── metadata.json
│   ├── cmd1.sh
│   └── cmd2.sh
└── standalone.sh        # Standalone script
```

**metadata.json Schema:**
| Field | Bắt buộc | Mô tả |
|-------|----------|-------|
| `name` | ✅ | Tên hiển thị |
| `version` | ✅ | Phiên bản (semver) |
| `description` | ✅ | Mô tả ngắn |
| `library_id` | ✅ | ID duy nhất (dùng trong CLI) |
| `author` | ❌ | Tên tác giả |
| `shells` | ❌ | Shells hỗ trợ (bash, zsh, fish) |
| `commands` | ❌ | Danh sách commands (auto-detect nếu không có) |

**Ví dụ 1 - Library đơn giản:**
```json
{
  "name": "Git Utils",
  "version": "1.0.0",
  "description": "Các lệnh git tiện ích",
  "library_id": "git-utils"
}
```

**Ví dụ 2 - Library phức tạp:**
```json
{
  "name": "Docker Tools",
  "version": "2.1.0",
  "description": "Quản lý Docker containers",
  "library_id": "docker",
  "author": "DevOps Team",
  "shells": ["bash", "zsh"],
  "commands": ["cleanup", "stats", "logs"]
}
```

**Ví dụ 3 - Standalone script:**
- Chỉ cần đặt file `.sh` trực tiếp vào `~/.corun/addons/`
- Không cần metadata.json
- Tên file = tên command

**Best Practices:**
- Đặt tên library_id ngắn gọn, dùng kebab-case
- Mỗi script nên có shebang (`#!/bin/bash`)
- Thêm `--help` flag cho mỗi script

**Troubleshooting:**
- "Library không hiển thị" → Kiểm tra metadata.json hợp lệ
- "Command not found" → Kiểm tra file có quyền execute (`chmod +x`)
- "Conflict detected" → Đổi tên library_id hoặc standalone script

---

## Checklist triển khai

- [ ] Viết README.md mới
- [ ] Tạo README.developer.md
- [ ] Commit changes
