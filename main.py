import typer
from rich.console import Console
from rich.prompt import Prompt
from note_manager import NoteManager
from ui import display_menu, display_notes

app = typer.Typer()
console = Console()
note_manager = NoteManager()

@app.command()
def main():
    """笔记管理程序主入口"""
    while True:
        display_menu()
        choice = Prompt.ask("请选择操作", choices=["1", "2", "3", "4", "5", "6", "7"])
        
        if choice == "1":
            title = Prompt.ask("请输入笔记标题")
            content = Prompt.ask("请输入笔记内容")
            note_manager.add_note(title, content)
            console.print("[green]笔记添加成功！[/green]")
            
        elif choice == "2":
            title = Prompt.ask("请输入要删除的笔记标题")
            if note_manager.delete_note(title):
                console.print("[green]笔记删除成功！[/green]")
            else:
                console.print("[red]未找到该笔记！[/red]")
                
        elif choice == "3":
            title = Prompt.ask("请输入要查找的笔记标题")
            note = note_manager.find_note_by_title(title)
            if note:
                display_notes([note])
            else:
                console.print("[red]未找到该笔记！[/red]")
                
        elif choice == "4":
            keyword = Prompt.ask("请输入要搜索的关键词")
            notes = note_manager.search_notes(keyword)
            if notes:
                display_notes(notes)
            else:
                console.print("[red]未找到包含该关键词的笔记！[/red]")
                
        elif choice == "5":
            title = Prompt.ask("请输入要修改的笔记标题")
            new_content = Prompt.ask("请输入新的笔记内容")
            if note_manager.update_note(title, new_content):
                console.print("[green]笔记修改成功！[/green]")
            else:
                console.print("[red]未找到该笔记！[/red]")
                
        elif choice == "6":
            notes = note_manager.get_all_notes()
            if notes:
                display_notes(notes)
            else:
                console.print("[yellow]当前没有任何笔记！[/yellow]")
                
        elif choice == "7":
            console.print("[yellow]感谢使用笔记管理程序，再见！[/yellow]")
            break

if __name__ == "__main__":
    app() 