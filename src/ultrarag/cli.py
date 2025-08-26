import importlib.metadata
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

ULTRARAG_LOGO = r"""
   _ __ ___ __  ______             ____  ___   ______   ___    ____ 
  _ __ ___ / / / / / /__________ _/ __ \/   | / ____/  |__ \  / __ \
 _ __ ___ / / / / / __/ ___/ __ `/ /_/ / /| |/ / __    __/ / / / / /
_ __ ___ / /_/ / / /_/ /  / /_/ / _, _/ ___ / /_/ /   / __/_/ /_/ / 
 _ __ ___\____/_/\__/_/   \__,_/_/ |_/_/  |_\____/   /____(_)____/  
                                                           
""".lstrip(
    "\n"
)


def get_version_safe(pkgname: str) -> str:
    try:
        return importlib.metadata.version(pkgname)
    except Exception:
        return "<not installed>"


def make_server_banner(
    pipeline_name: str,
    show_logo: bool = True,
    doc_url: str = "https://github.com/OpenBMB/UltraRAG",
) -> Panel:
    logo_text = Text(ULTRARAG_LOGO, style="#722EA5") if show_logo else ""
    info_table = Table.grid(padding=(0, 1))
    info_table.add_column(style="bold", justify="center")
    info_table.add_column(style="bold cyan", justify="left")
    info_table.add_column(style="white", justify="left")
    info_table.add_row("🖥️", "Pipeline name:", pipeline_name)
    info_table.add_row("", "", "")
    info_table.add_row("📚", "Docs:", doc_url)
    info_table.add_row("", "", "")
    info_table.add_row(
        "🏎️", "FastMCP version:", Text(get_version_safe("fastmcp"), style="dim white")
    )
    info_table.add_row(
        "🤝", "MCP version:", Text(get_version_safe("mcp"), style="dim white")
    )
    return Panel(
        Group(logo_text, "", info_table),
        title="UltraRAG 2.0",
        title_align="left",
        border_style="dim",
        padding=(1, 4),
        expand=False,
    )


def log_server_banner(pipeline_name: str):
    console = Console(stderr=True)
    panel = make_server_banner(pipeline_name)
    console.print(Group("\n", panel, "\n"))
