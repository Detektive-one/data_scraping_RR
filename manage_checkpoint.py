"""
Checkpoint management utility script.
Use this to view, clear, or modify scraping checkpoints.
"""
import sys
from checkpoint import Checkpoint


def show_checkpoint():
    """Display current checkpoint status"""
    cp = Checkpoint()
    print("\n" + "=" * 60)
    print("Current Checkpoint Status")
    print("=" * 60)
    print(f"Current Page:    {cp.data['current_page']}")
    print(f"Total Scraped:   {cp.data['total_scraped']:,} novels")
    print(f"Last Fiction ID: {cp.data['last_fiction_id']}")
    print(f"Timestamp:       {cp.data['timestamp']}")
    print("=" * 60)


def clear_checkpoint():
    """Clear the checkpoint to start fresh"""
    cp = Checkpoint()
    confirm = input("\n⚠ Are you sure you want to clear the checkpoint? (yes/no): ")
    if confirm.lower() == 'yes':
        cp.clear()
        print("✓ Checkpoint cleared. Next run will start from page 1.")
    else:
        print("✗ Cancelled.")


def set_checkpoint():
    """Manually set checkpoint values"""
    cp = Checkpoint()
    print("\n" + "=" * 60)
    print("Set Checkpoint Values")
    print("=" * 60)
    
    try:
        page = int(input(f"Enter page number (current: {cp.data['current_page']}): "))
        total = int(input(f"Enter total scraped (current: {cp.data['total_scraped']}): "))
        
        cp.save(page, total)
        print(f"\n✓ Checkpoint updated to page {page}, {total:,} novels scraped")
    except ValueError:
        print("✗ Invalid input. Please enter numbers only.")
    except KeyboardInterrupt:
        print("\n✗ Cancelled.")


def main():
    """Main menu"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'show':
            show_checkpoint()
        elif command == 'clear':
            clear_checkpoint()
        elif command == 'set':
            set_checkpoint()
        else:
            print(f"Unknown command: {command}")
            print_usage()
    else:
        # Interactive menu
        while True:
            print("\n" + "=" * 60)
            print("Checkpoint Manager")
            print("=" * 60)
            print("1. Show checkpoint status")
            print("2. Clear checkpoint (start fresh)")
            print("3. Set checkpoint manually")
            print("4. Exit")
            print("=" * 60)
            
            choice = input("Enter choice (1-4): ").strip()
            
            if choice == '1':
                show_checkpoint()
            elif choice == '2':
                clear_checkpoint()
            elif choice == '3':
                set_checkpoint()
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-4.")


def print_usage():
    """Print usage information"""
    print("\nUsage:")
    print("  python manage_checkpoint.py [command]")
    print("\nCommands:")
    print("  show   - Display current checkpoint status")
    print("  clear  - Clear checkpoint to start fresh")
    print("  set    - Manually set checkpoint values")
    print("\nIf no command is provided, interactive menu will be shown.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
