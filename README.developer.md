# Corun - Hướng dẫn tạo Library

Hướng dẫn dành cho những ai muốn tạo libraries và scripts cho Corun.

## Cấu trúc thư mục

Corun quét thư mục `~/.corun/addons/` để tìm libraries và standalone scripts:

```
~/.corun/addons/
├── my_library/           # Library (thư mục có metadata.json)
│   ├── metadata.json
│   ├── command1.sh
│   └── command2.sh
└── standalone.sh         # Standalone script (file .sh trực tiếp)
```

**Hai loại scripts:**
- **Library**: Thư mục chứa nhiều commands + file `metadata.json`
- **Standalone**: File `.sh` đơn lẻ (không cần metadata)

## metadata.json Schema

File `metadata.json` mô tả thông tin library:

| Field | Bắt buộc | Kiểu | Mô tả |
|-------|----------|------|-------|
| `name` | ✅ | string | Tên hiển thị của library |
| `version` | ✅ | string | Phiên bản (khuyến nghị dùng semver) |
| `description` | ✅ | string | Mô tả ngắn gọn về library |
| `library_id` | ✅ | string | ID duy nhất (dùng trong CLI) |
| `author` | ❌ | string | Tên tác giả |
| `shells` | ❌ | array | Danh sách shells hỗ trợ (vd: `["bash", "zsh"]`) |
| `commands` | ❌ | array | Danh sách commands (tự động phát hiện nếu bỏ trống) |

### Ví dụ metadata.json tối thiểu

```json
{
  "name": "Git Utilities",
  "version": "1.0.0",
  "description": "Các lệnh git tiện ích",
  "library_id": "git-utils"
}
```

## Ví dụ 1: Library đơn giản

Tạo library quản lý git với 2 commands:

**Cấu trúc:**
```
~/.corun/addons/git-utils/
├── metadata.json
├── cleanup.sh
└── status.sh
```

**metadata.json:**
```json
{
  "name": "Git Utilities",
  "version": "1.0.0",
  "description": "Các lệnh git tiện ích",
  "library_id": "git-utils"
}
```

**cleanup.sh:**
```bash
#!/bin/bash
# Xóa branches đã merge

git branch --merged | grep -v "\*" | grep -v "main" | grep -v "master" | xargs -n 1 git branch -d
echo "✓ Cleaned up merged branches"
```

**status.sh:**
```bash
#!/bin/bash
# Hiển thị status đẹp hơn

git status --short --branch
```

**Sử dụng:**
```bash
corun git-utils cleanup
corun git-utils status
```

## Ví dụ 2: Library phức tạp

Library với nhiều tính năng và metadata đầy đủ:

**metadata.json:**
```json
{
  "name": "Docker Tools",
  "version": "2.1.0",
  "description": "Quản lý Docker containers và images",
  "library_id": "docker",
  "author": "DevOps Team",
  "shells": ["bash", "zsh"],
  "commands": ["cleanup", "stats", "logs", "prune"]
}
```

**cleanup.sh:**
```bash
#!/bin/bash
# Dọn dẹp containers và images không dùng

docker container prune -f
docker image prune -f
echo "✓ Docker cleanup completed"
```

**stats.sh:**
```bash
#!/bin/bash
# Hiển thị thống kê containers

docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## Ví dụ 3: Standalone script

Script đơn lẻ không cần metadata.json:

**~/.corun/addons/backup.sh:**
```bash
#!/bin/bash
# Script backup đơn giản

BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d)

if [ "$1" == "--full" ]; then
    tar -czf "$BACKUP_DIR/full-$DATE.tar.gz" ~/projects
    echo "✓ Full backup completed"
else
    tar -czf "$BACKUP_DIR/incremental-$DATE.tar.gz" ~/projects --newer-mtime="1 day ago"
    echo "✓ Incremental backup completed"
fi
```

**Sử dụng:**
```bash
corun backup
corun backup --full
```

## Best Practices

### Đặt tên

- **library_id**: Dùng kebab-case, ngắn gọn, dễ nhớ (vd: `git-utils`, `docker`, `backup`)
- **Command names**: Động từ mô tả hành động (vd: `cleanup`, `install`, `deploy`)

### Scripts

- **Shebang**: Luôn thêm `#!/bin/bash` (hoặc shell phù hợp) ở đầu file
- **Permissions**: Đảm bảo scripts có quyền execute: `chmod +x *.sh`
- **Help flag**: Nên hỗ trợ `--help` để hiển thị hướng dẫn sử dụng

### Tổ chức

- **1 library = 1 mục đích**: Tránh nhồi nhét quá nhiều commands không liên quan
- **Tên file = tên command**: File `cleanup.sh` → command `cleanup`

## Troubleshooting

### Library không hiển thị trong `corun library list`

**Nguyên nhân:** File `metadata.json` không hợp lệ hoặc thiếu fields bắt buộc

**Giải pháp:**
```bash
# Kiểm tra JSON hợp lệ
cat ~/.corun/addons/my_library/metadata.json | python -m json.tool

# Đảm bảo có đủ 4 fields bắt buộc: name, version, description, library_id
```

### Command not found

**Nguyên nhân:** Script không có quyền execute

**Giải pháp:**
```bash
chmod +x ~/.corun/addons/my_library/*.sh
```

### Conflict detected

**Nguyên nhân:** Trùng tên giữa library_id và standalone script

**Ví dụ:**
```
~/.corun/addons/
├── backup/              # library_id: backup
│   └── metadata.json
└── backup.sh           # standalone: backup
```

**Giải pháp:** Đổi tên một trong hai
```bash
# Option 1: Đổi tên standalone script
mv ~/.corun/addons/backup.sh ~/.corun/addons/backup-quick.sh

# Option 2: Đổi library_id trong metadata.json
# Sửa "library_id": "backup" → "library_id": "backup-tools"
```

## Chia sẻ Library

Bạn có thể chia sẻ library bằng cách:

1. **Đóng gói thư mục**
   ```bash
   tar -czf my-library.tar.gz ~/.corun/addons/my_library/
   ```

2. **Người khác cài đặt**
   ```bash
   corun library install ./my-library.tar.gz
   ```

## Tips nâng cao

### Sử dụng biến môi trường

Scripts có thể đọc biến môi trường:

```bash
#!/bin/bash
# deploy.sh

DEPLOY_ENV=${DEPLOY_ENV:-staging}
echo "Deploying to: $DEPLOY_ENV"
```

### Kết hợp với tools khác

```bash
#!/bin/bash
# analyze.sh - Sử dụng jq để parse JSON

curl -s https://api.example.com/data | jq '.results[] | {name, status}'
```

### Tab completion

Sau khi tạo library, cài đặt tab completion:

```bash
corun completion bash >> ~/.bashrc
# hoặc
corun completion zsh >> ~/.zshrc
```

## License

Xem [README.md](README.md) để biết thêm về Corun CLI.
