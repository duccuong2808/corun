Cấu trúc Project cho CLI corun (Cập nhật với Metaprogramming cho Nhóm Lệnh)
Cấu trúc này được cải tiến để sử dụng metaprogramming nhằm tự động tạo các nhóm lệnh (group commands) từ các thư mục trong library/ và các sub-command từ các tệp .sh trong từng thư mục. Mỗi thư mục trong library/ tương ứng với một nhóm lệnh, và mỗi tệp .sh trong thư mục đó tương ứng với một sub-command.
Cấu trúc thư mục
corun/
├── corun/                    # Thư mục chứa mã nguồn chính của CLI
│   ├── __init__.py           # Đánh dấu thư mục là Python package
│   ├── cli.py                # Điểm vào chính của CLI, tự động tạo nhóm lệnh
│   ├── library/              # Thư mục chứa kho thư viện lệnh
│   │   ├── app_list/         # Thư viện "App list" (nhóm lệnh "app")
│   │   │   ├── ls.sh         # Script cho lệnh "app ls"
│   │   │   ├── size.sh       # Script cho lệnh "app size"
│   │   │   └── metadata.json # Metadata mô tả thư viện
│   │   ├── sys_info/         # Thư viện "Sys info" (nhóm lệnh "sys")
│   │   │   ├── cpu.sh        # Script cho lệnh "sys cpu"
│   │   │   ├── mem.sh        # Script cho lệnh "sys mem"
│   │   │   └── metadata.json # Metadata mô tả thư viện
│   │   └── ...               # Các thư viện khác
│   └── utils/                # Thư viện tiện ích
│       ├── __init__.py
│       ├── shell.py          # Xử lý thực thi script bash/zsh
│       └── library_manager.py # Quản lý tải/gỡ cài đặt thư viện
├── tests/                    # Thư mục chứa các bài kiểm thử
│   ├── __init__.py
│   ├── test_cli.py           # Kiểm thử các lệnh CLI
│   └── test_library.py       # Kiểm thử quản lý thư viện
├── docs/                     # Tài liệu dự án
│   ├── installation.md       # Hướng dẫn cài đặt
│   ├── usage.md              # Hướng dẫn sử dụng
│   └── contributing.md       # Hướng dẫn đóng góp thư viện
├── setup.py                  # Tệp cài đặt Python package
├── requirements.txt          # Danh sách thư viện phụ thuộc
├── README.md                 # Giới thiệu dự án
├── LICENSE                   # Giấy phép (MIT)
├── .gitignore                # Tệp git ignore
└── config.json               # Cấu hình CLI

Mô tả chi tiết thay đổi
1. Thư mục corun/library/

Mỗi thư mục con (ví dụ: app_list/, sys_info/) tương ứng với một nhóm lệnh (group command: app, sys).
Mỗi tệp .sh trong thư mục tương ứng với một sub-command (ví dụ: ls.sh → app ls, cpu.sh → sys cpu).
Tệp metadata.json mô tả thông tin thư viện và danh sách sub-command.

2. Loại bỏ thư mục corun/commands/

Không cần thư mục commands/ nữa vì các nhóm lệnh và sub-command được tạo động trong cli.py dựa trên cấu trúc thư mục library/.
Điều này giảm thiểu mã nguồn thủ công và tăng tính linh hoạt khi thêm nhóm lệnh mới.

3. Triển khai corun/cli.py với Metaprogramming
Tệp cli.py sử dụng metaprogramming để quét thư mục library/ và tự động tạo các nhóm lệnh cùng sub-command.
import click
import os
from pathlib import Path
from corun.utils.shell import run_shell_script

# Đường dẫn đến thư mục thư viện
LIBRARY_PATH = Path(__file__).parent / "library"

def create_dynamic_command(script_path):
    """Tạo lệnh động từ tệp script."""
    def dynamic_command():
        if script_path.exists():
            run_shell_script(script_path)
        else:
            click.echo(f"Error: Script {script_path} not found.")
    dynamic_command.__name__ = script_path.stem  # Tên lệnh
    dynamic_command.__doc__ = f"Run {script_path.stem} command from {script_path.parent.name} library."
    return click.command()(dynamic_command)

def create_dynamic_group(group_name, library_path):
    """Tạo nhóm lệnh động từ thư mục thư viện."""
    @click.group(name=group_name)
    def dynamic_group():
        f"""Nhóm lệnh cho thư viện {group_name}, tự động tạo từ {library_path}."""
        pass
    # Thêm sub-command từ các tệp .sh
    for script in library_path.glob("*.sh"):
        if script.is_file():
            command = create_dynamic_command(script)
            dynamic_group.add_command(command, name=script.stem)
    return dynamic_group

# Tạo CLI chính
@click.group()
def cli():
    """Corun CLI: Chạy các lệnh từ kho thư viện do cộng đồng đóng góp."""
    pass

# Tự động thêm các nhóm lệnh từ các thư mục trong library/
for library_dir in LIBRARY_PATH.iterdir():
    if library_dir.is_dir() and (library_dir / "metadata.json").exists():
        group_name = library_dir.name.replace("_", "-")  # Chuyển app_list thành app-list
        group = create_dynamic_group(group_name, library_dir)
        cli.add_command(group)

if __name__ == "__main__":
    cli()

4. Tệp corun/utils/shell.py
Hàm hỗ trợ thực thi script shell (không thay đổi).
import subprocess
import click

def run_shell_script(script_path):
    """Thực thi script shell và xử lý đầu ra."""
    try:
        result = subprocess.run(
            [str(script_path)],
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running script {script_path}: {e.stderr}", err=True)

5. Tệp corun/library/app_list/metadata.json
Mô tả thông tin thư viện app_list.
{
  "name": "App list",
  "version": "1.0.0",
  "author": "Community Contributor",
  "description": "Thư viện cung cấp các lệnh để quản lý danh sách ứng dụng.",
  "shells": ["bash", "zsh"],
  "commands": ["ls", "size"]
}

6. Tệp corun/library/app_list/ls.sh
Script cho lệnh app ls.
#!/bin/bash
# Liệt kê các ứng dụng trong hệ thống
ls -l /Applications 2>/dev/null || dir  # macOS hoặc Windows

7. Tệp corun/library/app_list/size.sh
Script cho lệnh app size.
#!/bin/bash
# Hiển thị kích thước ứng dụng
du -sh /Applications/* 2>/dev/null || dir /s  # macOS hoặc Windows

8. Tệp corun/library/sys_info/metadata.json
Mô tả thư viện sys_info.
{
  "name": "Sys info",
  "version": "1.0.0",
  "author": "Community Contributor",
  "description": "Thư viện cung cấp các lệnh để xem thông tin hệ thống.",
  "shells": ["bash", "zsh"],
  "commands": ["cpu", "mem"]
}

9. Tệp corun/library/sys_info/cpu.sh
Script cho lệnh sys cpu.
#!/bin/bash
# Hiển thị thông tin CPU
lscpu 2>/dev/null || systeminfo | findstr /C:"Processor"  # Linux hoặc Windows

10. Tệp corun/library/sys_info/mem.sh
Script cho lệnh sys mem.
#!/bin/bash
# Hiển thị thông tin bộ nhớ
free -h 2>/dev/null || systeminfo | findstr /C:"Memory"  # Linux hoặc Windows

Cách hoạt động

Khởi chạy CLI:

Chạy corun sẽ quét thư mục library/ để tìm các thư mục con (như app_list/, sys_info/).
Mỗi thư mục có metadata.json sẽ được ánh xạ thành một nhóm lệnh (ví dụ: app, sys).
Các tệp .sh trong thư mục được ánh xạ thành sub-command (ví dụ: ls.sh → app ls, cpu.sh → sys cpu).


Ví dụ lệnh:

corun app ls: Thực thi library/app_list/ls.sh.
corun sys cpu: Thực thi library/sys_info/cpu.sh.


Thêm nhóm lệnh hoặc sub-command mới:

Tạo thư mục mới trong library/ (ví dụ: new_library/) với metadata.json và các tệp .sh.
CLI tự động nhận diện nhóm lệnh new-library và các sub-command tương ứng.



Lợi ích của Metaprogramming

Tự động hóa hoàn toàn: Không cần khai báo thủ công nhóm lệnh hoặc sub-command trong mã Python.
Mở rộng dễ dàng: Chỉ cần thêm thư mục hoặc tệp .sh vào library/.
Bảo trì đơn giản: Mã lệnh nằm trong script shell, dễ chỉnh sửa và đóng góp.

Các bước tiếp theo

Thêm cơ chế kiểm tra quyền thực thi của tệp .sh trước khi chạy.
Triển khai library_manager.py để tải/gỡ thư viện từ kho cộng đồng (GitHub).
Viết kiểm thử trong tests/ để đảm bảo các nhóm lệnh và sub-command được tạo đúng.
Cập nhật tài liệu trong docs/ để hướng dẫn cách thêm thư viện mới.
