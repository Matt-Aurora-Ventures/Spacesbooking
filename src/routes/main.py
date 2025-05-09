import os
import datetime
import traceback # Added for detailed exception logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from src.models.user import User, users_db 
from src.utils import parse_todo_file
from src.calendar_service import get_calendar_service, create_event, CREDENTIALS_FILE, TOKEN_FILE, SCOPES

# For Google OAuth
from google_auth_oauthlib.flow import Flow
import google.oauth2.credentials

main_bp = Blueprint("main", __name__)

# --- OAuth Routes ---
@main_bp.route("/authorize-google-calendar")
@login_required
def authorize_google_calendar():
    if not current_user.is_admin:
        flash("Only admins can authorize Google Calendar.", "danger")
        return redirect(url_for("main.dashboard"))
    if not os.path.exists(CREDENTIALS_FILE):
        flash("Google API credentials file (credentials.json) is missing. Please contact admin.", "danger")
        return redirect(url_for("main.admin_dashboard"))

    try:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            scopes=SCOPES,
            redirect_uri=url_for("main.oauth2callback", _external=True)
        )
        authorization_url, state = flow.authorization_url(access_type="offline", prompt="consent")
        session["oauth_state"] = state # Store state in session
        return redirect(authorization_url)
    except Exception as e:
        flash(f"Error initializing Google OAuth flow: {str(e)}", "danger")
        print(f"OAuth Init Error: {e}\n{traceback.format_exc()}")
        return redirect(url_for("main.admin_dashboard"))

@main_bp.route("/oauth2callback")
@login_required
def oauth2callback():
    if not current_user.is_admin:
        flash("Only admins can complete Google Calendar authorization.", "danger")
        return redirect(url_for("main.dashboard"))
        
    state = session.get("oauth_state")
    if not state or state != request.args.get("state"):
        flash("OAuth state mismatch. Please try authorizing again.", "danger")
        return redirect(url_for("main.admin_dashboard"))

    try:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE, 
            scopes=SCOPES,
            state=state,
            redirect_uri=url_for("main.oauth2callback", _external=True)
        )
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        with open(TOKEN_FILE, "w") as token_file_obj:
            token_file_obj.write(credentials.to_json())
        flash("Google Calendar authorized successfully!", "success")
    except Exception as e:
        flash(f"Error during Google Calendar authorization: {str(e)}", "danger")
        print(f"OAuth2Callback Error: {e}\n{traceback.format_exc()}")
    return redirect(url_for("main.admin_dashboard"))

# --- Standard Routes ---
@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("main.admin_dashboard"))
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("main.admin_dashboard"))
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            if user.is_admin:
                return redirect(url_for("main.admin_dashboard"))
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("main.admin_dashboard"))
        
    project_name = current_user.project_name
    engagement_data = parse_todo_file(project_name)
    
    calendar_authed = os.path.exists(TOKEN_FILE)

    if engagement_data and engagement_data.get("error"):
        flash(f"Could not load engagement status: {engagement_data['error']}", "warning")
        engagement_data_for_template = {"error_message": engagement_data["error"], "phases": {}}
    elif not engagement_data:
        flash("No engagement data found for your project yet.", "info")
        engagement_data_for_template = {"error_message": "No engagement data found.", "phases": {}}
    else:
        engagement_data_for_template = {"phases": engagement_data}

    return render_template("dashboard.html", engagement_status=engagement_data_for_template, client_info=current_user, calendar_authed=calendar_authed)

@main_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    print("--- Admin Dashboard Start ---")
    try:
        if not current_user.is_admin:
            flash("You do not have permission to access this page.", "danger")
            print("Admin Dashboard: Non-admin user tried to access.")
            return redirect(url_for("main.dashboard"))

        all_engagements_data = {}
        engagement_dir = "/home/ubuntu/client_portal_project/client_portal/src/engagements"
        print(f"ADMIN_DASHBOARD_ROUTE: Using engagement_dir = {engagement_dir} --- V_LATEST")
        
        if not os.path.exists(engagement_dir):
            flash(f"Engagement directory critical error: {engagement_dir} not found. Please check server logs.", "danger")
            print(f"Admin Dashboard: Engagement directory NOT FOUND: {engagement_dir}")
        else:
            print(f"Admin Dashboard: Engagement directory FOUND: {engagement_dir}")
            try:
                print("Admin Dashboard: Attempting to list engagement directory contents...")
                filenames = os.listdir(engagement_dir)
                print(f"Admin Dashboard: Files in engagement directory: {filenames}")
                for filename in filenames:
                    print(f"Admin Dashboard: Processing file: {filename}")
                    if filename.startswith("todo_") and filename.endswith(".md"):
                        project_name_from_file = filename[len("todo_"):-len(".md")]
                        print(f"Admin Dashboard: Extracted project name: {project_name_from_file}")
                        if not project_name_from_file: 
                            print(f"Admin Dashboard: Skipping empty project name from file: {filename}")
                            continue
                        
                        parsed_data = parse_todo_file(project_name_from_file)
                        print(f"Admin Dashboard: Parsed data for {project_name_from_file}: {parsed_data}")
                        if parsed_data:
                            if parsed_data.get("error"):
                                all_engagements_data[project_name_from_file] = {"error": parsed_data["error"], "phases": {}}
                            else:
                                all_engagements_data[project_name_from_file] = {"phases": parsed_data}
                        else: 
                            all_engagements_data[project_name_from_file] = {"error": f"Could not parse or find tracking file for {project_name_from_file}.", "phases": {}}
                    else:
                        print(f"Admin Dashboard: Skipping non-matching file: {filename}")
            except Exception as e_listdir:
                flash(f"Error reading engagement directory contents: {str(e_listdir)}", "danger")
                print(f"Admin Dashboard: Exception while listing directory: {e_listdir}\n{traceback.format_exc()}")
        
        print("Admin Dashboard: Processing registered client users...")
        for user_id, user_obj in users_db.items():
            print(f"Admin Dashboard: Checking user: {user_obj.username}, Project: {user_obj.project_name}, IsAdmin: {user_obj.is_admin}")
            if not user_obj.is_admin and user_obj.project_name:
                if user_obj.project_name not in all_engagements_data:
                    print(f"Admin Dashboard: Project {user_obj.project_name} not found in file-based engagements. Parsing its todo file.")
                    parsed_data = parse_todo_file(user_obj.project_name)
                    print(f"Admin Dashboard: Parsed data for user {user_obj.project_name}: {parsed_data}")
                    if parsed_data and not parsed_data.get("error"):
                         all_engagements_data[user_obj.project_name] = {"phases": parsed_data}
                    elif parsed_data and parsed_data.get("error"):
                        all_engagements_data[user_obj.project_name] = {"error": parsed_data["error"], "phases": {}}
                    else: 
                        all_engagements_data[user_obj.project_name] = {"error": f"Tracking file not found or unparseable for {user_obj.project_name}.", "phases": {}}
        
        calendar_authed = os.path.exists(TOKEN_FILE)
        print(f"Admin Dashboard: Calendar authorized: {calendar_authed}")
        print(f"Admin Dashboard: Data to render: {all_engagements_data}")
        print("--- Admin Dashboard End (Pre-render) ---")
        return render_template("admin_dashboard.html", all_engagements=all_engagements_data, calendar_authed=calendar_authed)
    except Exception as e_main:
        print(f"--- Admin Dashboard CRITICAL ERROR ---\n{e_main}\n{traceback.format_exc()}\n--- End Admin Dashboard CRITICAL ERROR ---")
        # Optionally, render a generic error page or re-raise to let Flask handle it (which results in 500)
        flash("A critical error occurred on the admin dashboard. Please check server logs.", "danger")
        return render_template("admin_dashboard.html", all_engagements={}, calendar_authed=False, critical_error=True) # Pass a flag for template


@main_bp.route("/onboarding_info")
@login_required
def onboarding_info():
    return render_template("onboarding_info.html")

@main_bp.route("/update-info", methods=["GET", "POST"])
@login_required
def update_client_info():
    if current_user.is_admin:
        flash("Admin users cannot update client-specific info here.", "warning")
        return redirect(url_for("main.admin_dashboard"))
    if request.method == "POST":
        summary = request.form.get("project_summary")
        website = request.form.get("project_website")
        x_social = request.form.get("project_x_social")
        
        current_user.update_info(summary, website, x_social)
        flash("Your information has been updated successfully!", "success")
        return redirect(url_for("main.dashboard"))
    
    return render_template("client_info_form.html", client_info=current_user)

@main_bp.route("/update-focus-topics", methods=["GET", "POST"])
@login_required
def update_focus_topics():
    if current_user.is_admin:
        flash("Admin users cannot update client-specific focus topics here.", "warning")
        return redirect(url_for("main.admin_dashboard"))
    if request.method == "POST":
        topics = request.form.get("focus_topics")
        current_user.update_focus_topics(topics)
        flash("Your focus topics have been updated successfully!", "success")
        return redirect(url_for("main.dashboard"))
    
    return render_template("focus_topics_form.html", client_info=current_user)

@main_bp.route("/book-slot", methods=["GET", "POST"])
@login_required
def submit_booking_request():
    if current_user.is_admin:
        flash("Admin users cannot book slots.", "warning")
        return redirect(url_for("main.admin_dashboard"))

    if not os.path.exists(TOKEN_FILE):
        flash("Booking system is not available. Google Calendar needs to be authorized by an admin.", "warning")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        booking_date_str = request.form.get("booking_date")
        booking_time_str = request.form.get("booking_time") # Format HH:MM
        booking_notes = request.form.get("booking_notes")
        project_name = current_user.project_name

        try:
            year, month, day = map(int, booking_date_str.split("-"))
            hour, minute = map(int, booking_time_str.split(":"))
            start_dt_naive = datetime.datetime(year, month, day, hour, minute)
            end_dt_naive = start_dt_naive + datetime.timedelta(hours=1) 
            start_datetime_iso = start_dt_naive.isoformat()
            end_datetime_iso = end_dt_naive.isoformat()

            service = get_calendar_service()
            if not service:
                flash("Google Calendar service is unavailable. Please try re-authorizing from the admin dashboard or contact support.", "danger")
                return redirect(url_for("main.dashboard"))

            event_summary = f"X Space: Aurora Ventures with {project_name}"
            event_description = f"X Space discussion with {project_name}.\nNotes from client: {booking_notes}"
            
            created_event = create_event(service, event_summary, start_datetime_iso, end_datetime_iso, description=event_description)

            if created_event:
                flash(f"Booking successful! Event created in Google Calendar for {booking_date_str} at {booking_time_str} CST.", "success")
            else:
                flash("Failed to create event in Google Calendar. Please check logs or try again.", "danger")

        except ValueError:
            flash("Invalid date or time format submitted.", "danger")
        except Exception as e:
            flash(f"An error occurred during booking: {str(e)}", "danger")
            print(f"Error during booking: {e}\n{traceback.format_exc()}")

        return redirect(url_for("main.dashboard"))

    return render_template("booking_form.html")


@main_bp.route("/logout")
@login_required
def logout():
    session.pop("oauth_state", None) 
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))

