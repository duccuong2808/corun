# Corun

> Chạy shell scripts dễ dàng từ terminal

Corun giúp bạn lưu trữ và chạy lại các shell scripts như các lệnh CLI.
Đặt scripts vào `~/.corun/addons/` và gọi chúng từ bất kỳ đâu.
## Cài đặt

```bash
# Development
pip install -e .

# Production (coming soon)
pipx install corun
```

## Bắt đầu nhanh

```bash
# Xem danh sách libraries và scripts có sẵn
corun library list

# Chạy lệnh từ library
corun <library_id> <command> [args...]

# Chạy standalone script
corun <script_name> [args...]
```

### Ví dụ

```bash
# Giả sử bạn có library "git-utils" với command "cleanup"
corun git-utils cleanup

# Giả sử bạn có standalone script "backup.sh"
corun backup --full
```

## Quick Reference

| Lệnh | Mô tả |
|------|-------|
| `corun --help` | Hiển thị trợ giúp |
| `corun -v` | Hiển thị phiên bản |
| `corun library list` | Danh sách tất cả libraries và scripts |
| `corun library info <id>` | Xem chi tiết library |
| `corun library install <path>` | Cài đặt library từ đường dẫn |
| `corun library remove <id>` | Gỡ bỏ library |
| `corun completion [shell]` | Cài đặt tab completion cho shell |

## Muốn tạo Library riêng?

Xem hướng dẫn chi tiết tại [README.developer.md](README.developer.md)

## License

MIT
