import os
import re
import traceback # Added for detailed exception logging

# Define the engagement directory path using an environment variable or a default
# This makes the path configurable and avoids hardcoding it directly in the function.
ENGAGEMENT_DIR_PATH = os.getenv("ENGAGEMENT_DIR_PATH", "/home/ubuntu/client_portal_project/client_portal/src/engagements")

# Ensure the engagement directory exists when the module is loaded
# This is a proactive approach to prevent errors if the directory is missing.
if not os.path.exists(ENGAGEMENT_DIR_PATH):
    try:
        os.makedirs(ENGAGEMENT_DIR_PATH)
        print(f"Successfully created directory: {ENGAGEMENT_DIR_PATH}")
    except Exception as e:
        print(f"Error creating directory {ENGAGEMENT_DIR_PATH}: {e}")

def parse_todo_file(project_name):
    """Parses the todo file for a given project and returns structured status."""
    print(f"--- parse_todo_file START for {project_name} ---")
    todo_file_path = os.path.join(ENGAGEMENT_DIR_PATH, f"todo_{project_name}.md")
    print(f"parse_todo_file: Attempting to parse {todo_file_path}")
    
    if not os.path.exists(todo_file_path):
        print(f"parse_todo_file: File NOT FOUND: {todo_file_path}")
        # Create the file if it doesn't exist to prevent errors later
        try:
            with open(todo_file_path, 'w') as f:
                f.write(f"# Placeholder for {project_name}\n") # Add some default content
            print(f"parse_todo_file: Created placeholder file: {todo_file_path}")
        except Exception as e:
            print(f"parse_todo_file: Error creating placeholder file {todo_file_path}: {e}")
            return {"error": f"Tracking file not found and could not be created: {todo_file_path}"}
        # return {"error": f"Tracking file not found: {todo_file_path}"}

    phases = {
        "Phase 1: Initial Contact & Qualification": [],
        "Phase 2: Preparation & Content Creation": [],
        "Phase 3: Scheduling & Promotion": [],
        "Phase 4: Post-Space Promotion & Follow-up": []
    }
    current_phase_name = None
    task_regex = re.compile(r"^\s*\*\s*\[([x\s~])\]\s*(.+)$")

    try:
        print(f"parse_todo_file: Attempting to open and read {todo_file_path}")
        with open(todo_file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.rstrip()
                # print(f"parse_todo_file: Processing line {i+1}: 	is_empty={not line.strip()}, content=\"{line}\"") # Reduced verbosity
                if line.startswith("### Phase"):
                    current_phase_name = line.strip("# ").strip()
                    # print(f"parse_todo_file: Found phase: {current_phase_name}")
                    if current_phase_name not in phases:
                        phases[current_phase_name] = [] 
                    continue
                
                if current_phase_name:
                    match = task_regex.match(line)
                    if match:
                        status_char = match.group(1)
                        task_description = match.group(2).strip()
                        status = "Pending"
                        if status_char == "x":
                            status = "Completed"
                        elif status_char == "~":
                            status = "Skipped/NA"
                        # print(f"parse_todo_file: Found task: name={task_description}, status={status}")
                        phases[current_phase_name].append({"task": task_description, "status": status})
        # print(f"parse_todo_file: Successfully processed {todo_file_path}")
                        
    except Exception as e:
        print(f"--- parse_todo_file CRITICAL ERROR for {project_name} ---\nFile: {todo_file_path}\n{e}\n{traceback.format_exc()}\n--- End parse_todo_file CRITICAL ERROR ---")
        return {"error": f"Error parsing tracking file: {str(e)}"}
    
    active_phases = {name: tasks for name, tasks in phases.items() if name in [
        "Phase 1: Initial Contact & Qualification",
        "Phase 2: Preparation & Content Creation",
        "Phase 3: Scheduling & Promotion",
        "Phase 4: Post-Space Promotion & Follow-up"
    ] and tasks}
    
    if not any(p in active_phases for p in [
        "Phase 1: Initial Contact & Qualification",
        "Phase 2: Preparation & Content Creation",
        "Phase 3: Scheduling & Promotion",
        "Phase 4: Post-Space Promotion & Follow-up"
    ]):
        active_phases = {name: tasks for name, tasks in phases.items() if tasks}

    if not active_phases and not any(phases.values()):
        print(f"parse_todo_file: No tasks found or could not parse phases correctly for {project_name}. Phases data: {phases}")
        return {"error": "No tasks found or could not parse phases correctly."}

    print(f"--- parse_todo_file END for {project_name}. Result: {active_phases} ---")
    return active_phases

if __name__ == "__main__":
    # Test the parser with an example project
    # Make sure a todo_CaddyFinance.md file exists in /home/ubuntu/outreach_engagements/
    # For testing, you might need to copy one of the existing todo files to todo_CaddyFinance.md
    # e.g., cp /home/ubuntu/outreach_engagements/todo_IdyllicLabs.md /home/ubuntu/outreach_engagements/todo_CaddyFinance.md
    print("Testing with CaddyFinance...")
    caddy_status = parse_todo_file("CaddyFinance")
    print(caddy_status)
    print("\nTesting with IdyllicLabs...")
    idyllic_status = parse_todo_file("IdyllicLabs")
    print(idyllic_status)

