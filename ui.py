from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from models import Note

console = Console()

def display_menu():
    """显示主菜单"""
    menu = """
    [bold blue]笔记管理程序[/bold blue]
    
    1. 添加笔记
    2. 删除笔记
    3. 查找笔记（按标题）
    4. 搜索笔记（按内容）
    5. 修改笔记
    6. 查看所有笔记
    7. 退出程序
    """
    console.print(Panel(menu, title="菜单", border_style="blue"))

def display_notes(notes: list[Note]):
    """显示笔记列表"""
    table = Table(title="笔记列表", show_header=True, header_style="bold magenta")
    table.add_column("标题", style="cyan")
    table.add_column("内容", style="green")
    table.add_column("创建时间", style="yellow")
    table.add_column("更新时间", style="yellow")

    for note in notes:
        table.add_row(
            note.title,
            note.content,
            note.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            note.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        )

    console.print(table) 