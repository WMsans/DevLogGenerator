import sys
from pathlib import Path

# Ensure we can import from src
sys.path.append("src")

from devlog.git_scanner import scan_commits
from devlog.draft import generate_draft

def test_summary_generation():
    print("1. Scanning git history...")
    # Scan the current directory for commits
    commits = scan_commits(Path("."), max_count=5)
    
    if not commits:
        print("Error: No commits found. Make sure you are in a git repo.")
        return

    print(f"   Found {len(commits)} commits.")

    # Select all found commits for the summary
    selected_indices = list(range(len(commits)))
    
    # Define the specific output file you requested
    output_file = Path("Summary.md")
    
    print(f"2. Sending to Ollama (qwen3) to generate '{output_file}'...")
    try:
        generate_draft(
            commits=commits,
            selected_indices=selected_indices,
            output_path=output_file,
            project_name="DevLog Test",
            model="qwen3:8b" # Ensure this matches a model you have installed
        )
        print("   ...Done!")
    except Exception as e:
        print(f"   Error connecting to LLM: {e}")
        return

    # Verify the file was created
    if output_file.exists():
        content = output_file.read_text()
        print("\nSUCCESS! File generated. Content snippet:\n")
        print("-" * 20)
        print(content[:300] + "...") # Print first 300 chars
        print("-" * 20)
    else:
        print("FAILURE: File was not created.")

if __name__ == "__main__":
    test_summary_generation()
