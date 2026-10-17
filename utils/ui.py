"""
Terminal UI formatting and colored output helpers for Jarvis.
"""

import os
import sys

# Enable ANSI escape sequence colors in Windows console
if os.name == "nt":
    os.system("")

class Colors:
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

BANNER = f"""{Colors.CYAN}{Colors.BOLD}
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
{Colors.BLUE}   >>> The Intelligent Python Voice Assistant <<<{Colors.RESET}
"""

def print_banner(mode: str = "voice"):
    print(BANNER)
    print(f"{Colors.DIM}------------------------------------------------------------{Colors.RESET}")
    print(f" {Colors.GREEN}● Status:{Colors.RESET} Online & Ready")
    print(f" {Colors.YELLOW}● Mode:{Colors.RESET} {mode.capitalize()} Input")
    print(f" {Colors.CYAN}● Commands:{Colors.RESET} Say or type 'help' for available actions")
    print(f" {Colors.CYAN}● Exit:{Colors.RESET} Say or type 'exit' / 'quit' to close")
    print(f"{Colors.DIM}------------------------------------------------------------{Colors.RESET}\n")

def print_jarvis(message: str):
    """Print a message spoken by Jarvis."""
    print(f"{Colors.CYAN}{Colors.BOLD}[JARVIS]{Colors.RESET} {message}")

def print_user(message: str):
    """Print the user's detected or typed input."""
    print(f"{Colors.GREEN}{Colors.BOLD}[YOU]{Colors.RESET} {message}")

def print_status(message: str):
    """Print a system status or informational note."""
    print(f"{Colors.YELLOW}[SYSTEM]{Colors.RESET} {message}")

def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {message}")

def print_listening():
    """Print a listening indicator."""
    print(f"{Colors.MAGENTA}🎤 Listening...{Colors.RESET}", end="\r", flush=True)

def clear_listening():
    """Clear the listening indicator line."""
    print(" " * 30, end="\r", flush=True)
