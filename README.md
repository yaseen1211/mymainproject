Project Name: Supplify
Module of: Supplify – Disaster Management and Emergency Response System
Tech Stack: Django (Backend), MySQL (Database), Bootstrap (Frontend), HTML/CSS/JS (UI)

🧩 Purpose:
"Supplify" manages relief supplies and logistics during disasters. It ensures organized donation management, transparent distribution, and efficient volunteer coordination across multiple relief camps and affected zones.

🔑 Core Features
1. Camp Management
Model: Camp

Fields:

Camp_ID (Primary Key)

Camp_Name

Location

Functionality:

Admins can create, view, and manage multiple camps.

Each camp is linked with supply data and volunteers.

2. Product Management
Model: Product

Fields:

Product_ID

Name

Category

Unit

Functionality:

List and manage products required across camps.

Categorized by necessity (e.g., food, medicine, clothing).

3. Volunteer Management
Model: Volunteer

Fields:

Volunteer_ID

Name

Camp_ID (Foreign Key)

Username, Password

Functionality:

Volunteers log in and see only the data of their assigned camp.

Can manage submitted items, view camp requests, and participate in logistics.

4. Submitted Items
Model: SubmittedItem

Fields:

Item_ID

Product_ID (FK to Product)

Camp_ID (FK to Camp)

Quantity

Status (e.g., Pending, Approved)

Date_Submitted

Functionality:

Track items donated or submitted to each camp.

Camp-specific breakdown helps avoid redundancy or shortages.

5. Notification System
Used to broadcast updates like urgent needs or alerts to admins, volunteers, or users.

5.1. Publish Notification
Fields:

To (Admin/Volunteer/User/All)

Subject

Message

Priority (High, Medium, Low)

Actions:

Publish: Sends out the alert.

Cancel: Discards creation.

5.2. View Notification
Shows:

Date

Subject

Priority

Close Status (Yes/No)

Close Notification: Marks a notification as expired or resolved.

6. Login and Access Control
Admin Login:

Full access to manage all camps, items, notifications, and volunteers.

Volunteer Login:

Restricted to their camp data only.

Can only view and submit items relevant to their assigned camp.

🎨 UI/UX Design
Frontend Theme:

Colors: White background, black text, blue highlights.

Structure: Clean tabular views, responsive layout with Bootstrap.

Pages Include:

Camp Dashboard

Add/View Products

Notification Console

Volunteer Dashboard

Submitted Item Tracker

📊 Database Structure (Simplified ER)
lua
Copy code
Camp ----< Volunteer
  |
  v
SubmittedItem >---- Product
🔮 Future Enhancements
AI Integration:

Detect disaster zones via satellite/data input.

Auto-create zones/camps based on affected areas.

Automated Notifications:

Alert users/volunteers about new disasters or updated needs.

Send requests for item categories urgently required.

Mobile Application:

Android/iOS support for users and volunteers.

Government API Integration:

Sync disaster zones with official disaster management authorities.

User Login Functionality:

Public donors can log in to track their donations.

General users receive push alerts about item shortages.

🧠 Smart Logistics (Planned)
Auto-suggestions for supplies based on past disaster data.

Prioritized routing for item dispatch based on urgency and location.

Let me know if you want a PDF version, diagram, or PowerPoint presentation of this overview!







