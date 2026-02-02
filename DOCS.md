# Corun CLI - Documentation

> **Command Runner** - Công cụ CLI quản lý và chạy shell scripts

---

## 📦 Cài đặt

```bash
# Development
pip install -e .

# Production
pipx install corun
```

---

## 🚀 Quick Start

```bash
# Xem help
corun --help

# Chạy library command
corun <library_id> <command> [args...]

# Chạy standalone script
corun <script_name> [args...]
```

---

## 📁 Cấu trúc Addons

Tất cả scripts được lưu tại `~/.corun/addons/`:

```
~/.corun/addons/
├── my_lib/               # Library
│   ├── metadata.json     # Thông tin library
│   ├── cmd1.sh          # Command 1
│   └── cmd2.sh          # Command 2
├── another_lib/
│   └── hello.sh
└── standalone.sh         # Standalone script
```

---

## 🔧 Quản lý Libraries

| Command | Mô tả |
|---------|-------|
| `corun library list` | Liệt kê tất cả libraries |
| `corun library info <id>` | Xem chi tiết library |
| `corun library create <id>` | Tạo library mới |
| `corun library install <path>` | Cài library từ folder |
| `corun library remove <id>` | Xóa library |

### Tạo Library mới

```bash
# Interactive mode
corun library create

# Quick mode
corun library create my-tools --name "My Tools" --description "Dev tools"
```

---

## ⌨️ Shell Autocomplete

```bash
# Xem hướng dẫn cài đặt
corun completion

# Cài đặt completion
corun --install-completion zsh   # hoặc bash, fish
```

---

## 📝 Metadata Format

File `metadata.json` trong mỗi library:

```json
{
  "name": "My Library",
  "version": "1.0.0",
  "description": "Mô tả ngắn",
  "library_id": "my_lib",
  "author": "Your Name",
  "shells": ["bash", "zsh"],
  "commands": ["cmd1", "cmd2"]
}
```

**Lưu ý:** Nếu không có `metadata.json`, Corun sẽ tự động:
- `library_id` = tên folder
- `commands` = tất cả file `.sh`

---

## 📋 Ví dụ sử dụng

### 1. Chạy command từ library

```bash
# Syntax: corun <library_id> <command> [args...]
corun brew package
corun info cpu
corun app_list ls -la
```

### 2. Chạy standalone script

```bash
# Syntax: corun <script_name> [args...]
corun deploy
corun backup --verbose
```

### 3. Tạo library mới

```bash
# Tạo library
corun library create network-tools

# Kết quả
~/.corun/addons/network-tools/
├── metadata.json
└── example.sh
```

---

## ⚠️ Priority System

Khi có conflict giữa Library và Standalone cùng tên:

```
Priority (Cao → Thấp):
1. Library Commands      [Cao nhất]
2. Standalone Scripts    [Thấp hơn]
```

**Ví dụ:**
- Có `~/.corun/addons/tools/` (library)
- Có `~/.corun/addons/tools.sh` (standalone)

→ `corun tools` sẽ chạy library, standalone bị bỏ qua + hiển thị warning.

---

## 📐 Kiến trúc Code

```
src/corun/
├── __init__.py      # Package init
├── main.py          # Entry point + CLI
├── models.py        # Data models (Library, Command, Metadata)
├── scanner.py       # Scan ~/.corun/addons/
├── executor.py      # Execute shell scripts
├── completion.py    # Shell autocomplete
└── library/
    └── commands.py  # Library management commands
```

---

## ✅ Version History

| Version | Features |
|---------|----------|
| v0.0.1 | Core CLI, Library management |
| v0.0.2 | `library create`, Shell autocomplete |
| v0.0.3 | Priority System for conflicts |

---

## 📚 Tài liệu tham khảo

- [Corun CLI - Spec.md](./Corun%20CLI%20-%20Spec.md) - Đặc tả chi tiết đầy đủ
- [README.md](./README.md) - Quick reference

---

## 📄 License

MIT
