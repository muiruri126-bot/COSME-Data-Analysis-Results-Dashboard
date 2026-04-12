"""Generate COSME DIP System User Guide as PDF using fpdf2."""
import os
import sys

# Add backend to path for any needed imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fpdf import FPDF


class UserGuidePDF(FPDF):
    """Custom PDF class for the COSME DIP User Guide."""

    BLUE = (0, 51, 102)       # Plan International navy
    LIGHT_BLUE = (0, 78, 154)
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100)
    LIGHT_GRAY = (240, 240, 240)
    BLACK = (30, 30, 30)

    def header(self):
        if self.page_no() == 1:
            return  # Skip header on cover page
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.GRAY)
        self.cell(0, 8, 'COSME DIP System - User Guide', align='L')
        self.set_font('Helvetica', '', 9)
        self.cell(0, 8, f'Page {self.page_no()}', align='R', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(*self.LIGHT_BLUE)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*self.GRAY)
        self.cell(0, 10, 'Plan International Kenya - COSME Project', align='C')

    def cover_page(self):
        self.add_page()
        self.ln(40)
        # Title block
        self.set_fill_color(*self.BLUE)
        self.rect(0, 60, 210, 80, 'F')
        self.set_y(70)
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(*self.WHITE)
        self.cell(0, 14, 'COSME DIP System', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 18)
        self.cell(0, 12, 'User Guide', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(8)
        self.set_font('Helvetica', '', 12)
        self.cell(0, 8, 'Detailed Implementation Plan Tracker', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 8, 'Community-based Solutions for Mangrove Ecosystems', align='C', new_x='LMARGIN', new_y='NEXT')

        self.set_y(160)
        self.set_text_color(*self.BLACK)
        self.set_font('Helvetica', '', 11)
        self.cell(0, 8, 'Plan International Kenya', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 8, 'Version 1.0 - July 2026', align='C', new_x='LMARGIN', new_y='NEXT')

    def chapter_title(self, number, title):
        self.add_page()
        self.ln(4)
        self.set_fill_color(*self.BLUE)
        self.set_text_color(*self.WHITE)
        self.set_font('Helvetica', 'B', 18)
        self.cell(0, 14, f'  {number}. {title}', fill=True, new_x='LMARGIN', new_y='NEXT')
        self.ln(6)
        self.set_text_color(*self.BLACK)

    def section_title(self, title):
        self.ln(4)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(*self.LIGHT_BLUE)
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(*self.BLACK)
        self.ln(2)

    def sub_section(self, title):
        self.ln(2)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.BLUE)
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(*self.BLACK)
        self.ln(1)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet_list(self, items):
        self.set_font('Helvetica', '', 10)
        for item in items:
            self.set_x(self.l_margin + 6)
            self.multi_cell(180, 6, '- ' + item)
        self.ln(2)

    def numbered_list(self, items):
        self.set_font('Helvetica', '', 10)
        for i, item in enumerate(items, 1):
            self.set_x(self.l_margin + 6)
            self.multi_cell(180, 6, f'{i}. {item}')
        self.ln(2)

    def info_box(self, text):
        self.set_fill_color(235, 245, 255)
        self.set_draw_color(*self.LIGHT_BLUE)
        x = self.get_x()
        y = self.get_y()
        self.set_font('Helvetica', 'I', 9)
        # Approximate height
        lines = len(text) // 85 + 1
        h = max(lines * 5 + 6, 12)
        self.rect(x + 4, y, 182, h, 'DF')
        self.set_xy(x + 8, y + 3)
        self.multi_cell(174, 5, text)
        self.ln(4)

    def table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 // len(headers)] * len(headers)

        # Header row
        self.set_fill_color(*self.BLUE)
        self.set_text_color(*self.WHITE)
        self.set_font('Helvetica', 'B', 9)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, border=1, fill=True, align='C')
        self.ln()

        # Data rows
        self.set_text_color(*self.BLACK)
        self.set_font('Helvetica', '', 9)
        for row_idx, row in enumerate(rows):
            if row_idx % 2 == 0:
                self.set_fill_color(*self.LIGHT_GRAY)
            else:
                self.set_fill_color(*self.WHITE)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell), border=1, fill=True)
            self.ln()
        self.ln(3)


def generate_guide():
    pdf = UserGuidePDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Cover Page ──
    pdf.cover_page()

    # ── Table of Contents ──
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(*pdf.BLUE)
    pdf.cell(0, 14, 'Table of Contents', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(6)
    pdf.set_text_color(*pdf.BLACK)

    toc = [
        ('1', 'Introduction', 3),
        ('2', 'Getting Started', 4),
        ('3', 'Login & Authentication', 5),
        ('4', 'Implementation Plan (Framework)', 6),
        ('5', 'Activity Detail & Task Management', 7),
        ('6', 'Gantt Chart', 9),
        ('7', 'Executive Dashboard', 10),
        ('8', 'Reports & Export', 11),
        ('9', 'User Management (Admin)', 12),
        ('10', 'User Roles & Permissions', 13),
        ('11', 'Troubleshooting & FAQ', 14),
    ]

    for num, title, page in toc:
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(10, 8, num)
        pdf.cell(140, 8, title)
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 8, f'....... {page}', align='R', new_x='LMARGIN', new_y='NEXT')

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 1: Introduction
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('1', 'Introduction')

    pdf.section_title('1.1 About the COSME DIP System')
    pdf.body_text(
        'The COSME Detailed Implementation Plan (DIP) Tracker is a web-based project management '
        'system designed for Plan International Kenya to track and manage activities under the '
        'Community-based Solutions for Mangrove Ecosystems (COSME) project. The system enables '
        'real-time monitoring of project implementation, task management, and progress reporting '
        'across the entire results framework hierarchy.'
    )

    pdf.section_title('1.2 Key Features')
    pdf.bullet_list([
        'Results Framework Management - Navigate the full IO > IMO > Output > Activity hierarchy',
        'Task Management - Create, assign, update and track tasks with planned vs actual tracking',
        'Gantt Chart Visualization - Visual timeline of tasks with status color coding',
        'Executive Dashboard - KPIs, charts, delayed task analysis, and workload distribution',
        'Reports & Excel Export - Activity progress, output completion, variance, and workload reports',
        'Role-Based Access Control (RBAC) - Five roles with granular permissions',
        'Audit Trail - Full audit logging of all changes for accountability',
        'Notifications - In-app notifications for task assignments and status changes',
    ])

    pdf.section_title('1.3 System Requirements')
    pdf.bullet_list([
        'Modern web browser (Chrome, Firefox, Edge, Safari)',
        'Internet connection',
        'Valid user account with assigned role(s)',
    ])

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 2: Getting Started
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('2', 'Getting Started')

    pdf.section_title('2.1 Accessing the System')
    pdf.body_text(
        'Open your web browser and navigate to the COSME DIP system URL provided by your '
        'administrator. You will be presented with the login screen.'
    )

    pdf.section_title('2.2 System Navigation')
    pdf.body_text(
        'After logging in, you will see the main application with a sidebar navigation panel on the left '
        'containing the following menu items:'
    )

    pdf.table(
        ['Menu Item', 'Description', 'Access'],
        [
            ['Implementation Plan', 'Browse and drill into the results framework', 'All users'],
            ['Gantt Chart', 'Visual timeline of tasks and activities', 'All users'],
            ['Dashboard', 'Executive KPIs and charts', 'All users'],
            ['Reports', 'Tabular reports with Excel export', 'All users'],
            ['Admin', 'User management panel', 'Admin only'],
        ],
        [50, 90, 50],
    )

    pdf.body_text(
        'The top bar shows your user profile, notification bell (with unread count), '
        'and a logout button. On mobile devices, use the hamburger menu to open the sidebar.'
    )

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 3: Login & Authentication
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('3', 'Login & Authentication')

    pdf.section_title('3.1 Logging In')
    pdf.numbered_list([
        'Navigate to the system URL in your browser.',
        'Enter your registered email address.',
        'Enter your password.',
        'Click the "Sign In" button.',
        'Upon successful login, you will be redirected to the Implementation Plan page.',
    ])

    pdf.section_title('3.2 Registering a New Account')
    pdf.body_text(
        'If you do not have an account, click the "Register here" link on the login page.'
    )
    pdf.numbered_list([
        'Enter your full name.',
        'Enter a valid email address.',
        'Enter a phone number (optional).',
        'Create a password (minimum 6 characters).',
        'Click "Create Account".',
        'You will be automatically logged in with a Viewer role. Contact your Admin to assign additional roles.',
    ])

    pdf.section_title('3.3 Forgot Password')
    pdf.numbered_list([
        'Click "Forgot your password?" on the login page.',
        'Enter your registered email address.',
        'Click "Send Reset Link".',
        'Check your email for the password reset link.',
        'Click the link and enter your new password.',
    ])
    pdf.info_box('Note: For security, the system will always show a success message even if the email is not registered.')

    pdf.section_title('3.4 Session Management')
    pdf.body_text(
        'Your session uses JWT (JSON Web Tokens) with the following timeouts:\n'
        '- Access token: 15 minutes (auto-refreshed silently)\n'
        '- Refresh token: 7 days\n'
        '- After 7 days of inactivity, you will need to log in again.'
    )

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 4: Implementation Plan (Framework)
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('4', 'Implementation Plan (Framework)')

    pdf.section_title('4.1 Results Framework Hierarchy')
    pdf.body_text(
        'The COSME project uses a four-level results framework hierarchy:'
    )
    pdf.table(
        ['Level', 'Code Format', 'Example', 'Description'],
        [
            ['Intermediate Outcome', '1100, 1200, 1300', 'IO 1100', 'High-level project results'],
            ['Immediate Outcome', '1110, 1120, ...', 'IMO 1110', 'Medium-term outcomes'],
            ['Output', '1111, 1112, ...', 'Output 1111', 'Deliverables'],
            ['Activity', '1111.1, 1111.2', 'Act 1111.1', 'Specific work items'],
        ],
        [42, 42, 32, 74],
    )

    pdf.section_title('4.2 Navigating the Framework')
    pdf.numbered_list([
        'On the Implementation Plan page, you will see a Results Framework Overview showing all Intermediate Outcomes.',
        'Click on an Intermediate Outcome or select it from the dropdown to load its Immediate Outcomes.',
        'Select an Immediate Outcome to load its Outputs.',
        'Select an Output to view its Activities as cards.',
        'Click an Activity card (or select from the dropdown) to navigate to its task detail page.',
    ])

    pdf.section_title('4.3 Activity Cards')
    pdf.body_text(
        'Each activity is displayed as a card showing:\n'
        '- Activity code (e.g., 1111.1)\n'
        '- Description\n'
        '- Status badge (On track, Completed, etc.)\n'
        '- Budget Holder name (if assigned)\n\n'
        'Click any card to navigate to the Activity Detail page where you can manage tasks.'
    )

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 5: Activity Detail & Task Management
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('5', 'Activity Detail & Task Management')

    pdf.section_title('5.1 Activity Overview')
    pdf.body_text(
        'The Activity Detail page shows the activity header with code, description, status, '
        'and budget holder. Below that is the task management area with a toolbar and task table.'
    )

    pdf.section_title('5.2 Creating a Task')
    pdf.numbered_list([
        'Click the "Add Task" button.',
        'Fill in the task details in the modal form:',
        '   - Task Name (required)',
        '   - Plan/Actual: Select "Planned" for planned timeline or "Actual" for actual dates',
        '   - Start Date and End Date (required)',
        '   - Status: Pending, In progress, Complete, Delayed, or Cancelled',
        '   - Responsible: Type the name of the responsible person',
        '   - Evidence: Required when status is "Complete"',
        'Click "Create Task" to save.',
    ])

    pdf.info_box(
        'Tip: Create a "Planned" task first with target dates, then create an "Actual" task '
        'with the same name to track variance between planned and actual timelines.'
    )

    pdf.section_title('5.3 Editing a Task')
    pdf.numbered_list([
        'Click the pencil icon in the Actions column of the task you want to edit.',
        'Modify the fields as needed in the modal form.',
        'Click "Save Changes".',
    ])
    pdf.body_text(
        'When a task status is changed to "Delayed" or "Cancelled", the system automatically '
        'notifies the Budget Holder(s) associated with the activity.'
    )

    pdf.section_title('5.4 Deleting a Task')
    pdf.body_text(
        'Click the trash icon next to a task and confirm the deletion. Tasks are soft-deleted '
        '(not permanently removed) to maintain audit trail integrity.'
    )

    pdf.section_title('5.5 Filtering Tasks')
    pdf.body_text(
        'Use the status dropdown above the task table to filter tasks by status '
        '(Pending, In progress, Complete, Delayed, Cancelled).'
    )

    pdf.section_title('5.6 Task Statuses')
    pdf.table(
        ['Status', 'Description', 'Color Code'],
        [
            ['Pending', 'Task has not started yet', 'Gray'],
            ['In progress', 'Task is currently being worked on', 'Blue'],
            ['Complete', 'Task has been finished (requires evidence)', 'Green'],
            ['Delayed', 'Task is behind schedule', 'Orange'],
            ['Cancelled', 'Task has been cancelled', 'Dark gray'],
        ],
        [40, 110, 40],
    )

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 6: Gantt Chart
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('6', 'Gantt Chart')

    pdf.section_title('6.1 Overview')
    pdf.body_text(
        'The Gantt Chart page provides a visual timeline view of tasks across the results framework. '
        'Each task is displayed as a colored bar representing its duration and status.'
    )

    pdf.section_title('6.2 Using the Gantt Chart')
    pdf.numbered_list([
        'Select a View Level: "Intermediate Outcome" or "Activity".',
        'Select a specific item from the dropdown.',
        'The chart will display a summary card with progress, task counts, and date range.',
        'Below the summary, individual task bars are shown with color coding by status.',
        'Hover over any bar to see details: dates, status, and plan/actual type.',
    ])

    pdf.section_title('6.3 Reading the Gantt Bars')
    pdf.body_text(
        'Each bar represents a task:\n'
        '- Bar length indicates task duration (number also shown in days)\n'
        '- Bar color indicates status: Gray=Pending, Blue=In Progress, Green=Complete, '
        'Orange=Delayed, Dark Gray=Cancelled\n'
        '- The task name is shown on the left\n'
        '- The status label is shown on the right'
    )

    pdf.section_title('6.4 Roll-up Information')
    pdf.body_text(
        'When viewing at a higher level (Intermediate Outcome), the system shows roll-up data:\n'
        '- Overall progress percentage\n'
        '- Complete tasks vs total tasks\n'
        '- Date range spanning the earliest start to latest end\n'
        '- Groups broken down by sub-levels (Immediate Outcomes or Activities)'
    )

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 7: Executive Dashboard
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('7', 'Executive Dashboard')

    pdf.section_title('7.1 KPI Cards')
    pdf.body_text(
        'The dashboard displays six key performance indicators at the top:'
    )
    pdf.table(
        ['KPI', 'Description'],
        [
            ['Total Tasks', 'Total number of active (non-deleted) tasks in the system'],
            ['Complete', 'Number of tasks with status "Complete"'],
            ['In Progress', 'Number of tasks currently in progress'],
            ['Delayed', 'Number of tasks marked as delayed'],
            ['% Complete', 'Percentage of total tasks that are complete'],
            ['On-Time Rate', 'Percentage of completed tasks finished on or before planned end date'],
        ],
        [45, 145],
    )

    pdf.section_title('7.2 Charts')
    pdf.sub_section('Tasks by Status (Pie Chart)')
    pdf.body_text(
        'A pie chart showing the distribution of tasks across all five statuses. '
        'Each slice is color-coded to match the status colors used throughout the system.'
    )

    pdf.sub_section('Workload by Person (Bar Chart)')
    pdf.body_text(
        'A horizontal stacked bar chart showing how many tasks each person is responsible for, '
        'broken down by status. This helps identify workload imbalances.'
    )

    pdf.section_title('7.3 Delayed Task Analysis')
    pdf.sub_section('Delayed Ageing Buckets')
    pdf.body_text(
        'Tasks that are past their end date are grouped into four ageing buckets:\n'
        '- 1-7 days overdue\n'
        '- 8-14 days overdue\n'
        '- 15-30 days overdue\n'
        '- 30+ days overdue\n\n'
        'This helps prioritize which delayed tasks need immediate attention.'
    )

    pdf.sub_section('Top Delayed Tasks Table')
    pdf.body_text(
        'A table listing the top 10 most delayed tasks with task name, activity code, '
        'due date, days overdue, and responsible person.'
    )

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 8: Reports & Export
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('8', 'Reports & Export')

    pdf.section_title('8.1 Available Reports')
    pdf.body_text(
        'The Reports page provides four built-in reports accessible via tabs:'
    )
    pdf.table(
        ['Report', 'Description'],
        [
            ['Activity Progress', 'Shows each activity with total tasks, complete count, and % complete'],
            ['Output Completion', 'Shows each output with activity count, task totals, and completion rate'],
            ['Variance', 'Compares planned vs actual dates for tasks, showing start/end variance in days'],
            ['Workload', 'Shows each user with their task counts broken down by status'],
        ],
        [45, 145],
    )

    pdf.section_title('8.2 Using Reports')
    pdf.numbered_list([
        'Navigate to the Reports page from the sidebar.',
        'The Activity Progress report loads automatically on entry.',
        'Click on any tab to switch to a different report.',
        'Report data is displayed in a table with sortable columns.',
    ])

    pdf.section_title('8.3 Excel Export')
    pdf.body_text(
        'Click the "Export Full DIP" button (green) in the top-right corner to download the '
        'complete DIP data as an Excel workbook (.xlsx). The export contains two sheets:\n'
        '- "DIP Framework": Full hierarchy with codes, descriptions, status, and completion stats\n'
        '- "Tasks": All tasks with activity codes, responsible persons, dates, and statuses\n\n'
        'The Excel file auto-fits columns and uses styled headers for easy reading.'
    )

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 9: User Management (Admin)
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('9', 'User Management (Admin)')

    pdf.info_box('This section is for users with the Admin role only.')

    pdf.section_title('9.1 Viewing Users')
    pdf.body_text(
        'The Admin page shows a table of all system users with their name, email, assigned roles, '
        'and active/inactive status.'
    )

    pdf.section_title('9.2 Creating a New User')
    pdf.numbered_list([
        'Click the "Add User" button.',
        'Fill in the required fields: Full Name, Email, Password.',
        'Optionally set Phone and assign a Budget Holder.',
        'Select one or more roles by clicking the role checkboxes.',
        'Click "Create User" (or Save).',
    ])

    pdf.section_title('9.3 Editing a User')
    pdf.numbered_list([
        'Click the pencil icon next to the user.',
        'Modify fields as needed. Leave password blank to keep the existing password.',
        'Click Save.',
    ])

    pdf.section_title('9.4 Activating / Deactivating Users')
    pdf.body_text(
        'Click the "Deactivate" button next to an active user to disable their account. '
        'Click "Activate" to re-enable a deactivated user. Deactivated users cannot log in.'
    )

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 10: User Roles & Permissions
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('10', 'User Roles & Permissions')

    pdf.section_title('10.1 Role Overview')
    pdf.table(
        ['Role', 'Description'],
        [
            ['Admin', 'Full system access: manage users, roles, framework, all tasks'],
            ['ME_Specialist', 'Full create/edit/report across all entities + dashboards'],
            ['Budget_Holder', 'View portfolio; manage tasks under own budget holder portfolio'],
            ['Implementer', 'Create/update assigned tasks; add comments and attachments'],
            ['Viewer', 'Read-only access to dashboards, framework, and reports'],
        ],
        [40, 150],
    )

    pdf.section_title('10.2 Permission Matrix')
    pdf.body_text('Key permissions by role:')

    pdf.table(
        ['Action', 'Admin', 'ME Spec', 'Budget H', 'Impl', 'Viewer'],
        [
            ['View Framework', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
            ['Create/Edit Activities', 'Yes', 'Yes', 'Own', 'No', 'No'],
            ['Create Tasks', 'Yes', 'Yes', 'Own', 'Yes', 'No'],
            ['Update Tasks', 'Yes', 'Yes', 'Own', 'Own', 'No'],
            ['Delete Tasks', 'Yes', 'Yes', 'No', 'No', 'No'],
            ['View Dashboard', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
            ['Export Reports', 'Yes', 'Yes', 'Yes', 'No', 'Yes'],
            ['Manage Users', 'Yes', 'No', 'No', 'No', 'No'],
            ['View Audit Logs', 'Yes', 'Yes', 'No', 'No', 'No'],
        ],
        [40, 24, 24, 24, 24, 24],
    )

    pdf.info_box(
        '"Own" means the user can only perform the action on items within their assigned '
        'budget holder portfolio or tasks assigned to them.'
    )

    pdf.section_title('10.3 Role Assignment')
    pdf.body_text(
        'Users can have multiple roles. For example, a user can be both a Budget_Holder and an '
        'Implementer. The system grants the union of all permissions from assigned roles.'
    )

    # ═══════════════════════════════════════════════════════════
    #  CHAPTER 11: Troubleshooting & FAQ
    # ═══════════════════════════════════════════════════════════
    pdf.chapter_title('11', 'Troubleshooting & FAQ')

    pdf.section_title('Q: I cannot see any activities after logging in.')
    pdf.body_text(
        'A: If you are a Budget Holder, you will only see activities assigned to your budget holder '
        'portfolio. If no activities are assigned to your portfolio, the list will be empty. '
        'Contact your Admin or M&E Specialist to verify your budget holder assignment.'
    )

    pdf.section_title('Q: I get "Insufficient permissions" when trying to create a task.')
    pdf.body_text(
        'A: Your user role may not have task creation permissions. Viewers cannot create tasks. '
        'Contact your Admin to assign the appropriate role (Implementer, Budget_Holder, ME_Specialist, or Admin).'
    )

    pdf.section_title('Q: My session keeps expiring.')
    pdf.body_text(
        'A: Access tokens expire every 15 minutes but are automatically refreshed. If you are '
        'inactive for more than 7 days, you will need to log in again. This is a security feature.'
    )

    pdf.section_title('Q: How do I track planned vs actual dates?')
    pdf.body_text(
        'A: Create a task with Plan/Actual set to "Planned" for your target dates. When the actual '
        'work starts/completes, create another task with the same name but set Plan/Actual to "Actual" '
        'with the real dates. The Variance Report will automatically calculate the difference.'
    )

    pdf.section_title('Q: The Excel export button does not work.')
    pdf.body_text(
        'A: Ensure your browser allows file downloads from the system URL. If using a pop-up blocker, '
        'allow pop-ups for the COSME DIP system domain. Try right-clicking and "Save As" if needed.'
    )

    pdf.section_title('Q: How do I change my password?')
    pdf.body_text(
        'A: Use the "Forgot your password?" link on the login page to request a password reset email. '
        'Alternatively, ask your Admin to reset your password from the User Management page.'
    )

    pdf.section_title('Q: I cannot access the Admin panel.')
    pdf.body_text(
        'A: The Admin panel is only visible to users with the Admin role. '
        'If you believe you should have Admin access, contact your system administrator.'
    )

    pdf.section_title('Q: Tasks are showing as delayed but they are on track.')
    pdf.body_text(
        'A: The system automatically considers a task delayed if its end date has passed and the status '
        'is still "In progress" or "Pending". Update the task status to "Complete" or extend the end '
        'date if the timeline has changed.'
    )

    # ── Save ──
    output_path = os.path.join(os.path.dirname(__file__), 'COSME_DIP_User_Guide.pdf')
    pdf.output(output_path)
    print(f'User guide generated: {output_path}')
    print(f'File size: {os.path.getsize(output_path):,} bytes')
    return output_path


if __name__ == '__main__':
    generate_guide()
