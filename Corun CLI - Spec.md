# Đặc tả Tính năng - Corun CLI

> **Functional Specification Document**
>
> Version: 0.0.1
> Last Updated: 2025-10-09
> Language: Tiếng Việt

---

## 📑 MỤC LỤC

1. [Tổng quan](#1-tổng-quan)
2. [Tính năng chính](#2-tính-năng-chính)
3. [Giao diện người dùng](#3-giao-diện-người-dùng)
4. [Cấu trúc dữ liệu](#4-cấu-trúc-dữ-liệu)
5. [Hành vi hệ thống](#5-hành-vi-hệ-thống)
6. [Roadmap](#6-roadmap)

---

## 1. TỔNG QUAN

### 1.1. Mục đích

**Corun** - Viết tắt của **Command Runner** - là công cụ command-line giúp người dùng:
- Chạy scripts thông qua giao diện CLI thân thiện
- Tổ chức và quản lý shell scripts theo thư viện
- Chia sẻ scripts với cộng đồng
- Cài đặt và sử dụng scripts từ cộng đồng

### 1.2. Người dùng mục tiêu

- **Developers**: Tự động hóa công việc hàng ngày
- **DevOps/SysAdmins**: Quản lý scripts deployment, monitoring
- **Power Users**: Tổ chức automation scripts cá nhân
- **Community**: Chia sẻ và sử dụng scripts hữu ích

### 1.3. Use Cases

**Use Case 1: Quản lý Homebrew Packages**
```
User muốn xem danh sách Homebrew packages đã cài
→ Chạy: corun brew package
→ Hiển thị danh sách packages với thông tin chi tiết
```

**Use Case 2: System Information**
```
User muốn kiểm tra CPU info
→ Chạy: corun info cpu
→ Hiển thị thông tin CPU với color-coded output
```

**Use Case 3: Quick Deployment**
```
User có deployment script thường dùng
→ Copy vào ~/.corun/addons/deploy.sh
→ Chạy: corun deploy
→ Script execute deployment
```

### 1.4. Phạm vi

**Trong phạm vi (v0.0.1):**
- ✅ Quản lý shell scripts (.sh files)
- ✅ Tổ chức theo libraries
- ✅ User addons (~/.corun/addons/)
- ✅ Standalone scripts
- ✅ Library management (install/remove/list)
- ✅ Shell autocomplete
- ✅ macOS support

**Ngoài phạm vi (v0.0.1):**

- ❌ Project-level addons (./addons/)
- ❌ Script editor/IDE integration
- ❌ Online marketplace
- ❌ Dependency management
- ❌ Linux/Windows support

---

## 2. TÍNH NĂNG CHÍNH

### 2.1. Dynamic Command Generation

**Mô tả:**
Hệ thống tự động tạo CLI commands dựa trên cấu trúc thư mục và shell scripts trong `~/.corun/addons/`.

**Cách hoạt động:**

```
Cấu trúc trong ~/.corun/addons/      →    CLI Commands
──────────────────────────────────────────────────────────────
app_list/                                 corun app_list
├── metadata.json                         ├── --help
├── ls.sh                           →     ├── ls
└── size.sh                         →     └── size

sys_info/                                 corun sys_info
├── metadata.json                         ├── --help
├── cpu.sh                          →     ├── cpu
└── mem.sh                          →     └── mem

deploy.sh                           →     corun deploy
backup.sh                           →     corun backup
```

**Quy tắc mapping:**

| Cấu trúc                                      | Kết quả           | Ví dụ                          |
| --------------------------------------------- | ----------------- | ------------------------------ |
| Folder trong `~/.corun/addons/`               | Command group     | `app_list/` → `corun app_list` |
| File `.sh` trong folder                       | Sub-command       | `ls.sh` → `corun app_list ls`  |
| File `.sh` trực tiếp trong `~/.corun/addons/` | Top-level command | `deploy.sh` → `corun deploy`   |

**Đặc điểm:**
- Tên giữ nguyên (không chuyển đổi: `app_list` không thành `app-list`)
- Chỉ file `.sh` được nhận diện
- Folder không có `.sh` files → bỏ qua
- Thêm/xóa file → Command tự động cập nhật (sau restart)

### 2.2. Library Management

**Mô tả:**
Quản lý các thư viện scripts - cài đặt, gỡ bỏ, xem thông tin.

#### 2.2.1. List Libraries

**Command:**
```bash
corun library list
```

**Output mẫu:**
```
Installed libraries:
  • App List (v1.0.0) - Application management tools
    Commands: ls, size
    ID: app_list

  • System Info (v1.0.0) - System information commands
    Commands: cpu, mem
    ID: info

  • Homebrew Ultis (v1.0.0) - Homebrew utilities
    Commands: package, export, install
    ID: brew
```

#### 2.2.2. Library Info

**Command:**
```bash
corun library info <library_id>
```

**Output mẫu:**
```
Library: Homebrew Ultis
Version: 1.0.0
Author: Community Contributor
Description: Custom Homebrew formulae for productivity and development.
Supported shells: bash, zsh
Commands: package, export, install
Path: /Users/username/.corun/addons/brew
```

#### 2.2.3. Install Library

**Command:**
```bash
corun library install /path/to/library [--id <custom_id>]
```

**Behavior:**

- Install vào `~/.corun/addons/`
- Nếu library đã tồn tại → hỏi confirm overwrite
- Tự động set executable permission cho `.sh` files
- Validate structure trước khi install

**Ví dụ:**
```bash
# Install với ID từ metadata.json
corun library install ~/Downloads/network-tools

# Install với custom ID
corun library install ~/Downloads/my-scripts --id my-tools
```

#### 2.2.4. Remove Library

**Command:**
```bash
corun library remove <library_id>
```

**Behavior:**
- Xóa library từ `~/.corun/addons/`
- Yêu cầu confirm trước khi xóa
- Hiển thị danh sách commands sẽ bị mất

#### 2.2.5. Create Library Template

**Command:**
```bash
corun library create <id> "<name>" "<description>"
```

**Output:**
Tạo thư mục `~/.corun/addons/<id>/` với:
- `metadata.json` (pre-filled)
- `example.sh` (template script)

**Ví dụ:**
```bash
corun library create network-tools "Network Tools" "Network utility commands"

# Tạo:
# ~/.corun/addons/network-tools/
# ├── metadata.json
# └── example.sh
```

### 2.3. Addons Location

**Single location:**
Corun chỉ hoạt động với **user scope** - tất cả addons trong:

```
~/.corun/addons/
```

**Đặc điểm:**
- Chỉ một location duy nhất
- Scripts của user hiện tại
- Không cần quyền admin
- Tự động tạo khi cần
- Không phụ thuộc current working directory

**Corun KHÔNG đọc từ:**
- ❌ `./addons/` (current folder)
- ❌ Project-specific directories
- ❌ System-wide locations

**Use cases:**
- Personal automation scripts
- Development tools
- System utilities
- Custom workflows
- Experimental scripts

**Sharing scripts:**
Nếu muốn share với team:
1. Export library: `corun library export my-tools ~/shared/`
2. Team install: `corun library install ~/shared/my-tools`

(Tương lai: Marketplace cho việc share dễ dàng hơn)

### 2.4. Standalone Scripts

**Định nghĩa:**
Shell script độc lập đặt trực tiếp trong `~/.corun/addons/`, không thuộc library nào.

**Ví dụ:**
```
~/.corun/addons/
├── deploy.sh          ← Standalone
├── backup.sh          ← Standalone
├── app_list/          ← Library
│   └── ls.sh
└── brew/              ← Library
    └── package.sh
```

**Commands:**
```bash
corun deploy           # Standalone
corun backup           # Standalone
corun app_list ls      # Library command
corun brew package     # Library command
```

**Khi nào dùng standalone:**
- ✅ Script đơn giản, một mục đích
- ✅ Quick automation tasks
- ✅ Prototype nhanh
- ✅ Scripts không liên quan nhau

**Khi nào dùng library:**
- ✅ Nhiều scripts liên quan
- ✅ Cần metadata/documentation
- ✅ Muốn share với community
- ✅ Scripts cần phân nhóm

### 2.5. Priority System

**Khi có xung đột tên:**

```
Priority (Cao → Thấp):
──────────────────────────────
1. Library Commands           [Cao nhất]
2. Standalone Scripts         [Thấp hơn]
```

**Ví dụ:**

Giả sử có:
- `~/.corun/addons/tools/hello.sh` (Library command)
- `~/.corun/addons/hello.sh` (Standalone)

Khi chạy `corun hello` → Conflict!

**Behavior:**
- Nếu `corun tools hello` exists → Standalone `hello.sh` bị ignore
- Warning message hiển thị conflict
- Khuyến nghị rename hoặc move vào library

**Best practice:**
- Đặt tên unique cho standalone scripts
- Hoặc organize vào libraries

### 2.6. Shell Autocomplete

**Shells hỗ trợ:**
- Bash (>= 4.0)
- Zsh (>= 5.0)
- Fish (>= 3.0)

**Setup:**
```bash
# Auto-detect shell
corun completion

# Hoặc chọn shell cụ thể
corun completion bash
corun completion zsh
corun completion fish
```

**Autocomplete features:**

| Level              | Support  | Ví dụ                                            |
| ------------------ | -------- | ------------------------------------------------ |
| Top-level commands | ✅ v0.0.1 | `corun <TAB>` → library, completion, app_list... |
| Library management | ✅ v0.0.1 | `corun library <TAB>` → list, info, install...   |
| Library IDs        | ✅ v0.0.1 | `corun library info <TAB>` → app_list, brew...   |
| Sub-commands       | 📋 TODO   | `corun brew <TAB>` → package, export, install    |
| Flags              | 📋 TODO   | `corun library install --<TAB>` → --id           |

---

## 3. GIAO DIỆN NGƯỜI DÙNG

### 3.1. CLI Commands Overview

**Command structure:**
```
corun [global-options] <command> [command-options] [arguments]
```

**Global options:**
- `--help` - Hiển thị help
- `--version` - Hiển thị version

### 3.2. Built-in Commands

#### Help
```bash
corun --help
```
Hiển thị danh sách commands và groups.

#### Version
```bash
corun --version
```
Hiển thị version của Corun.

#### Completion
```bash
corun completion [bash|zsh|fish]
```
Hiển thị hướng dẫn setup autocomplete.

#### Library Management
```bash
corun library list
corun library info <library_id>
corun library install <path> [--id <id>]
corun library remove <library_id>
corun library create <id> "<name>" "<description>"
```

### 3.3. Dynamic Commands

**Library commands:**
```bash
corun <group> <command> [arguments...]

# Ví dụ:
corun app_list ls
corun app_list ls -la
corun info cpu
corun brew package --help
```

**Standalone commands:**
```bash
corun <script> [arguments...]

# Ví dụ:
corun deploy
corun deploy --env production
corun backup -f /path/to/backup
```

**Argument passing:**
- Scripts nhận **tất cả arguments** từ CLI
- Flags preserved: `-f`, `--verbose`, `--help`
- Script tự parse arguments
- Không có ràng buộc format

### 3.4. Help Messages

**Command help:**
```bash
corun <group> --help
```
Hiển thị:
- Mô tả group (từ metadata.json)
- Danh sách sub-commands
- Usage examples

### 3.5. Error Messages

**User-friendly errors:**

**Script không executable:**
```
Error: Script not executable
File: ~/.corun/addons/deploy.sh

To fix, run:
  chmod +x ~/.corun/addons/deploy.sh
```

**Invalid metadata:**
```
Error: Invalid metadata.json
Library: ~/.corun/addons/my-lib
Problem: Missing required field 'library_id'

Please fix the metadata.json file.
```

**Command not found:**
```
Error: Command not found
You entered: corun app_list invalid

Available commands in 'app_list':
  - ls
  - size

Run 'corun app_list --help' for more info.
```

---

## 4. CẤU TRÚC DỮ LIỆU

### 4.1. Thư mục Addons

**User Addons (duy nhất):**
```
~/.corun/addons/
├── <library_name>/       # Library directory
│   ├── metadata.json     # Library metadata (optional)
│   ├── script1.sh        # Shell script
│   └── script2.sh
└── standalone.sh         # Standalone script
```

**Ví dụ thực tế:**
```
~/.corun/addons/
├── app_list/
│   ├── metadata.json
│   ├── ls.sh
│   └── size.sh
├── brew/
│   ├── metadata.json
│   ├── package.sh
│   ├── export.sh
│   └── install.sh
├── info/
│   ├── metadata.json
│   ├── cpu.sh
│   └── mem.sh
├── deploy.sh            # Standalone
└── backup.sh            # Standalone
```

### 4.2. Metadata Format

**File:** `metadata.json` (Optional)

**Schema:**
```json
{
  "name": "string (required)",
  "version": "string (required)",
  "author": "string (optional)",
  "description": "string (required)",
  "library_id": "string (required)",
  "shells": ["array (optional)"],
  "commands": ["array (required)"]
}
```

**Field Descriptions:**

| Field         | Required | Mô tả                      | Ví dụ                         |
| ------------- | -------- | -------------------------- | ----------------------------- |
| `name`        | ✅        | Tên hiển thị               | "Homebrew Ultis"              |
| `version`     | ✅        | Version (semver)           | "1.0.0"                       |
| `author`      | ❌        | Tác giả                    | "Community Contributor"       |
| `description` | ✅        | Mô tả ngắn                 | "Custom Homebrew formulae..." |
| `library_id`  | ✅        | ID dùng cho CLI            | "brew"                        |
| `shells`      | ❌        | Shells support (docs only) | ["bash", "zsh"]               |
| `commands`    | ✅        | Danh sách commands         | ["package", "export"]         |

**Ví dụ thực tế:**
```json
{
  "name": "Homebrew Ultis",
  "version": "1.0.0",
  "author": "Community Contributor",
  "description": "Custom Homebrew formulae for productivity and development.",
  "library_id": "brew",
  "shells": ["bash", "zsh"],
  "commands": ["package", "export", "install"]
}
```

**Validation:**

**Khi metadata.json TỒN TẠI:**
- Phải là valid JSON
- Phải có required fields
- Invalid → **Blocking error**

**Khi metadata.json KHÔNG TỒN TẠI:**
- Auto-generate:
  - `library_id` = folder name
  - `commands` = tất cả `.sh` files

### 4.3. Shell Script Requirements

**Yêu cầu:**
```bash
#!/bin/bash
# hoặc
#!/bin/zsh

# Script content
```

**Checklist:**
- ✅ Shebang line
- ✅ Executable: `chmod +x`
- ✅ Extension: `.sh`

**Exit codes:**
- `0` - Success
- `1-255` - Error

**Behavior:**
- Corun pass-through exit code
- Không modify stdout/stderr
- Cho phép interactive input

---

## 5. HÀNH VI HỆ THỐNG

### 5.1. Khởi động

**Khi chạy `corun`:**

1. Scan `~/.corun/addons/`
   - Đọc folder structure
   - Load metadata.json (nếu có)
   - Register commands

2. Sẵn sàng nhận command

**Lưu ý:**
- Không phụ thuộc current working directory
- Có thể chạy từ bất kỳ đâu
- Chỉ đọc từ `~/.corun/addons/`

### 5.2. Command Execution

**Flow:**
```
User: corun brew package --help
   ↓
1. Parse command
   - Group: brew
   - Command: package
   - Args: ["--help"]
   ↓
2. Tìm script
   - Path: ~/.corun/addons/brew/package.sh
   ↓
3. Validate
   - Exists? ✓
   - Executable? ✓
   ↓
4. Execute
   - Pass args: ["--help"]
   - Output → terminal
   ↓
5. Return exit code
```

### 5.3. Library Installation

**Flow:**
```
User: corun library install /path/to/src --id my-lib
   ↓
1. Validate source
   - Path exists? ✓
   - Is directory? ✓
   ↓
2. Validate structure
   - metadata.json valid? ✓
   - Has .sh files? ✓
   ↓
3. Check conflicts
   - Already exists?
   - → Confirm overwrite
   ↓
4. Copy to ~/.corun/addons/my-lib/
   ↓
5. chmod +x *.sh
   ↓
6. Success
```

---

## 6. ROADMAP

### 6.1. Current (v0.0.1)

**Implemented:**
- ✅ Dynamic command generation
- ✅ Library management
- ✅ User addons (~/.corun/addons/)
- ✅ Standalone scripts
- ✅ Shell autocomplete (basic)
- ✅ macOS support

**Limitations:**
- ❌ Chỉ user scope (không có project scope)
- ❌ Chỉ macOS
- ❌ Autocomplete basic
- ❌ Chưa có marketplace

### 6.2. Short-term (Q1-Q2 2025)

**v0.1.0 - Linux Support**
- Full Linux compatibility
- Cross-platform scripts

**v0.2.0 - Enhanced Autocomplete**
- Sub-command completion
- Flag completion

**v0.3.0 - Remote Install**
- Install từ GitHub URL
- Version pinning

### 6.3. Medium-term (Q3 2025 - Q2 2026)

**v0.4.0 - Marketplace**
- Central marketplace
- Search/browse
- Ratings

**v0.5.0 - Team Sharing**
- Export libraries
- Import từ URL
- Team repositories

**v1.0.0 - Stable**
- Production-ready
- Complete docs
- Backward compatibility

### 6.4. Long-term (v2.0.0+)

**Future:**
- Project scope support (optional)
- Plugin system
- Web UI marketplace
- Cloud sync
- Multi-language scripts

---

## PHỤ LỤC

### A. Thuật ngữ

| Thuật ngữ             | Định nghĩa                       |
| --------------------- | -------------------------------- |
| **Addon**             | Shell script hoặc library        |
| **Library**           | Nhóm scripts + metadata          |
| **Standalone Script** | Script không thuộc library       |
| **library_id**        | CLI command group identifier     |
| **User Addons**       | Scripts trong `~/.corun/addons/` |
| **Metadata**          | File `metadata.json`             |

### B. FAQ

**Q: Tại sao chỉ user scope, không có project scope?**

A: v0.0.1 focus vào đơn giản hóa. Project scope sẽ có trong tương lai (v2.0+) như optional feature.

**Q: Làm sao share scripts với team?**

A:
1. Export library sang thư mục shared
2. Team install từ thư mục đó
3. Tương lai: Marketplace/team repositories

**Q: Có thể dùng cả user và project addons không?**

A: Không trong v0.0.1. Tính năng này trong roadmap dài hạn.

**Q: Làm sao backup addons?**

A: Copy toàn bộ `~/.corun/addons/` sang backup location.

**Q: Scripts có thể interactive không?**

A: Có. Scripts nhận stdin bình thường.

---

**Version:** 1.0
**Updated:** 2025-10-09
**Status:** Draft
**Maintainer:** Corun Community