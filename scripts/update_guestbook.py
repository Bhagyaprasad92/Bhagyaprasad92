import os
import json
import re
import html

def update_guestbook():
    issue_user = os.environ.get("ISSUE_USER")
    issue_body = os.environ.get("ISSUE_BODY")
    
    if not issue_user or not issue_body:
        print("Missing ISSUE_USER or ISSUE_BODY")
        return
        
    message = "Thanks for visiting!"
    if "### Your Message" in issue_body:
        parts = issue_body.split("### Your Message")
        if len(parts) > 1:
            message = parts[1].strip()
    
    # Clean up markdown response
    message = message.replace('\n', ' ').replace('\r', '').strip()
    if message == "_No response_":
        message = "Just stopped by to say hi!"
    
    if len(message) > 60:
        message = message[:57] + "..."
    
    entry = {
        "user": issue_user,
        "avatar": f"https://github.com/{issue_user}.png",
        "message": message
    }
    
    # Load existing
    try:
        with open("data/guestbook.json", "r", encoding="utf-8") as f:
            guests = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        guests = []
        
    # Remove existing entry for same user (update their message and move to top)
    guests = [g for g in guests if g["user"] != issue_user]
    
    # Add new entry to the front
    guests.insert(0, entry)
    
    # Keep only the latest 10
    guests = guests[:10]
    
    # Save json back
    with open("data/guestbook.json", "w", encoding="utf-8") as f:
        json.dump(guests, f, indent=2)
        
    # Generate Clean Markdown List
    markdown_lines = ["<ul style=\"list-style: none;\">"]
    for g in guests:
        avatar = g["avatar"]
        user = g["user"]
        msg = html.escape(g["message"])
        line = f'  <li><a href="https://github.com/{user}"><img src="{avatar}?s=60" width="25" style="border-radius:50%; vertical-align:middle;" /></a> <b><a href="https://github.com/{user}">@{user}</a></b>: <i>"{msg}"</i></li>'
        markdown_lines.append(line)
    markdown_lines.append("</ul>")
    
    new_html = "\n".join(markdown_lines)
    
    # Update README.md
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme = f.read()
            
        start_tag = "<!-- GUESTBOOK-START -->"
        end_tag = "<!-- GUESTBOOK-END -->"
        
        pattern = re.compile(f"{start_tag}.*?{end_tag}", re.DOTALL)
        if pattern.search(readme):
            new_readme = pattern.sub(f"{start_tag}\n{new_html}\n{end_tag}", readme)
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(new_readme)
            print("Successfully updated README.md")
        else:
            print("Guestbook tags not found in README.md")
    except Exception as e:
        print(f"Error updating README: {e}")

if __name__ == "__main__":
    update_guestbook()
