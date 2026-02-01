# Corun CLI

> **Command Runner** - CLI tool để quản lý và chạy shell scripts

## Cài đặt

```bash
# Development
pip install -e .

# Production (soon)
pipx install corun
```

## Sử dụng

```bash
# Xem help
corun --help

# Quản lý libraries
corun library list
corun library info <library_id>
corun library install /path/to/library
corun library remove <library_id>

# Chạy commands
corun <library_id> <command> [args...]
corun <standalone_script> [args...]
```

## Cấu trúc Addons

```
~/.corun/addons/
├── my_lib/
│   ├── metadata.json
│   ├── cmd1.sh
│   └── cmd2.sh
└── standalone.sh
```

## License

MIT
