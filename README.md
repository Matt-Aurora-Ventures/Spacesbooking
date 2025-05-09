# Aurora Ventures X Spaces Engagement Portal

## Overview

The Aurora Ventures X Spaces Engagement Portal is a web application designed to streamline the management and tracking of X Spaces (formerly Twitter Spaces) engagements for clients of Aurora Ventures. It provides a centralized platform for both clients and administrators to monitor progress, manage information, and facilitate communication related to these online events.

## Key Features

### 1. Client Dashboard
- **Personalized View**: Each client logs in to a dashboard tailored to their specific project.
- **Engagement Tracking**: Clients can view the status of their X Space engagement across various phases, from initial contact to post-event follow-up. This includes a checklist of tasks and their completion status (Pending, Completed, Skipped/NA).
- **Information Management**: Clients can update their project summary, website, and social media links (e.g., X/Twitter profile).
- **Focus Topics**: Clients can specify key topics or themes they wish to focus on during their X Space.
- **Booking System (Google Calendar Integration)**: Once an administrator has authorized Google Calendar, clients can request to book available slots for their X Spaces. The system will attempt to create an event in the linked Google Calendar.

### 2. Admin Dashboard
- **Centralized Oversight**: Administrators have a comprehensive view of all client engagements.
- **All Engagements Overview**: Displays the status of every registered client project, pulling data from their respective tracking files.
- **Google Calendar Authorization**: Administrators can authorize the application to access a Google Calendar. This is a one-time setup required for the client booking system to function. The application uses OAuth 2.0 for secure access.
- **User Management (Implicit)**: While not a direct UI feature, the system is built upon a user model distinguishing between admin and client roles, each with specific project associations.

### 3. Engagement Tracking Files
- **Markdown-based**: Each client project has a corresponding `todo_<ProjectName>.md` file.
- **Phased Structure**: These files are structured into distinct phases (e.g., "Phase 1: Initial Contact & Qualification", "Phase 2: Preparation & Content Creation", etc.).
- **Task Checklists**: Within each phase, specific tasks are listed with their status (e.g., `* [x] Task Completed`, `* [ ] Task Pending`).
- **Dynamic Updates**: The portal reads these files to display the engagement status on both client and admin dashboards.

### 4. Google Calendar Integration
- **Secure Authorization**: Uses OAuth 2.0 for administrators to grant the application permission to manage Google Calendar events.
- **Automated Event Creation**: When a client books a slot, the system attempts to create an event in the authorized Google Calendar, including details like the project name and client notes.
- **Credential Management**: Requires a `credentials.json` file (obtained from Google Cloud Console) to be present on the server for the authorization flow to work. A `token.json` file is generated upon successful authorization to store the access and refresh tokens.

## Technologies Used

- **Backend**: Python, Flask (web framework)
- **Frontend**: HTML, CSS, JavaScript (for client-side interactions)
- **Templating**: Jinja2 (for dynamic HTML generation with Flask)
- **Authentication**: Flask-Login (for user session management)
- **Database (User Store)**: In-memory dictionary (for simplicity in this version, can be extended to use a persistent database like SQLAlchemy with MySQL/PostgreSQL).
- **Google API**: `google-api-python-client`, `google-auth-oauthlib` for Google Calendar integration.

## Setup & Deployment

The application is designed to be deployed as a Flask web server. Key setup points include:
- Ensuring all Python dependencies from `requirements.txt` are installed.
- Placing the `credentials.json` file (for Google Calendar API) in the `src/` directory of the application for the deployed version.
- The application uses an internal directory `src/engagements/` to store the `todo_*.md` tracking files.

## How to Use

1.  **Login**: Access the portal URL. Users will be prompted to log in.
    *   **Admin Credentials**: `aurora_admin` / `supersecretadminpass` (or as configured)
    *   **Client Credentials**: Specific to each client (e.g., `client_projectalpha` / `password_projectalpha`)
2.  **Admin Dashboard**: After admin login, the admin dashboard is displayed.
    *   Authorize Google Calendar if not already done.
    *   View the status of all client engagements.
3.  **Client Dashboard**: After client login, their project-specific dashboard is displayed.
    *   View their engagement status.
    *   Update their project information and focus topics.
    *   Book an X Space slot (if Google Calendar is authorized by admin).

