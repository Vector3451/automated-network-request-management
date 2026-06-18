**INSIGHT FOR APPRAOCH**

The task is divided into 5 main phases : 

**PHASE 1 - Requirement Analysis & Planning**

1. Business Objectives :-

The business objective for Automated Network Request Management in ServiceNow typically aligns with improving operational efficiency, reducing manual effort, and enhancing user satisfaction in managing network-related services

To streamline and automate the end-to-end lifecycle of network-related service requests using ServiceNow, thereby:

· Reducing manual effort and human error

· Accelerating request fulfilment times

· Enforcing standardized workflows and approval processes

· Improving visibility and tracking through a centralized platform

· Enhancing end-user experience with faster, more reliable service delivery

· Ensuring compliance with IT and security policies

2. Functional Scope :-

Covers catalog creation, form design, approval routing, flow designer automation, and email notifications.

3. Stakeholder Mapping :-

Stakeholders: End users (requesters), IT admins, network fulfillment team, and approvers.


i) End Users (Requesters) :-

Role : Employees or teams requesting network services through Service Portal only

Needs / Expectations : 
- Simple, intuitive request submission
- Fast turnaround- Status visibility

Impact of Automation :
✔️ Faster request fulfilment
✔️ Better visibility through ServiceNow portal

ii) IT Admins :-

Role : Manage ServiceNow configurations, integrations, and workflows.

Needs / Expectations :

- Reliable automation
- Minimal manual intervention- Easy change management

Impact of Automataion :
✔️ Reduced ticket workload
✔️ Easier maintenance and updates

iii) Network Fulfilment Team

Role : Executes network changes and ensures infrastructure reliability.

Needs / Expectations :

- Clear, complete request data
- Fewer manual tasks- Standardized processes

Impact of Automataion :
✔️ Automated task generation
✔️ Reduced human error
✔️ More time for complex issues

iv) Approvers

Role : Managers or compliance officers approving requests.

Needs / Expectations :
- Policy enforcement
- Quick, informed approval workflows

Impact of Automataion :
✔️ Structured, automated approval routing
✔️ Better audit trails

4. Execution Roadmap :-

Roadmap divided into milestones: catalog creation, form setup, approval integration, testing, and deployment.

Milestone 1 : Catalog Creation

Objective: Establish a structured, user-friendly service catalog for network requests.

·        Identify network request types

·        Define request catalogs and categories.

·        Create service catalog items with clear titles and descriptions.

·        Collaborate with network and IT teams for content accuracy.

·        Ensure catalog taxonomy aligns with ITSM structure.

Milestone 2 : Form Setup

Objective: Design dynamic, intuitive forms that capture all required request data.

·        Build catalog item forms using variables.

·        Add dynamic behaviours (show/hide fields based on selection).

·        Include mandatory fields to reduce incomplete submissions.

·        Align form inputs with downstream automation and workflows.

Milestone 3 : Approval Integration

Objective: Automate and enforce approval workflows for compliance and control.

·        Identify required approval chains (e.g., manager, network security).

·        Configure approval steps using Flow Designer or Workflow Editor.

·        Ensure audit logging and email notifications are enabled.

Milestone 4 : Testing 

Objective: Validate end-to-end request lifecycle and automation.

·        Perform unit testing on each catalog item.

·        Conduct end-to-end request simulation with multiple scenarios.

·        Validate approvals, task creation, notifications, and data accuracy.

·        Involve stakeholders in UAT (User Acceptance Testing).

·        Log defects and iterate improvements.

Milestone 5 : Deployment

Objective: Launch automated request management in the production environment.

·        Finalize deployment checklist.

·        Migrate workflows and catalog items from development to production.

·        Monitor system behaviour and performance post-launch.

·        Provide training to end users and fulfilment teams.

·        Setup support process for post-deployment issues.

**PHASE 2 - Backend Developement & Configuration**

Develop the core logic, configure system settings, and set up backend integrations and automations.

1. Data Architecture :-

The Automated Network Request Management solution in ServiceNow is built using a structured data model that combines standard platform tables with a custom network request table to ensure clarity, scalability, and control. Network requests are captured through catalog-driven records and stored with well-defined fields such as request type, access level, business justification, and related network configuration items. Forms are designed to dynamically display only relevant information using UI logic, while mandatory fields enforce data accuracy and compliance. List views provide operational visibility for approvers and network teams, enabling efficient tracking of requests, tasks, and statuses. This architecture ensures secure access, seamless automation, and reliable reporting across the entire request lifecycle.

- Creation of tables 

· Navigate to: System Definition > Tables.
· Click New to create a new table.

· Fill in Table Information:
·     Name: Network Database
·     Label: Network Database
·     Auto-generate schema: Leave it checked if you'd like ServiceNow to auto-generate schema fields.
· Click Submit to create the table.

- Creation of fields

·   In ServiceNow, fields are created at the table level. To create a field, you first need to identify the table where the field will reside.

1.   In the Application Navigator (left-side panel), type Tables in the search bar.
2.   Under System Definition, click Tables. This will take you to a list of all tables in the system.

Select the Table to Add the Field

·     From the list of tables, search for and select the table you want to add a field to. For example, if you want to add a field to the Network database table:

1.   Type "Network database" in the search box or scroll through the list.
2.   Click on the Network database table name. You’ll now see a list of all fields (columns) associated with the Network database table.

Open the Table's Columns

·     After selecting the table, you'll be brought to a view that lists all the columns (fields) that currently exist on that table.
·     To create a new field (column), go to the Columns tab (this is where all fields for the selected table are listed).


Create a New Field

1.   In the Columns tab, click the New button located at the top-right corner of the page to create a new field.
2.   You’ll now be prompted with a form where you need to define the new field. The following fields need to be filled out:

- Define Field Properties

Fill in the following details for your new field:

1. Column Label (Field Label)

·     Description: This is the name that will be displayed on the forms, lists, and records.
·     Example: Customer Name

2. Column Name

·     Description: This is the internal name of the field and is auto-generated based on the column label. It should be unique for each field. Do not manually edit this unless necessary.
·     Example: customer_name
·     Description: The type of field determines the kind of data it will store. You need to choose the correct type based on the data you want to store (e.g., text, number, date, etc.). Some of the most common types include:
o   String: For short text values (e.g., name, description).
o   Integer: For numbers without decimals (e.g., age, number of items).
o   Choice: A dropdown list of options.
o   Reference: A field that links to another table (e.g., linking to a User table).
o   Boolean: A true/false checkbox.
o   Date: For a date picker field.
o   Date/Time: For both date and time.
·     Example: String, Choice, Reference

  3.  Max Length (Optional)

·     Description: If you are creating a string-type field, you can specify the maximum length of the text allowed.
·     Example: 255 characters (default length for a string field).

4. Mandatory

·     Description: Check this box if the field should be required when creating or updating records.
·     Example: For a "Customer Name" field, this might be required.

5. Default Value (Optional)

·     Description: You can set a default value for the field if desired. This value will appear automatically when creating a new record.
·     Example: Set the default value to "New Customer" for a "Customer Name" field.

6. Read-Only

·     Description: Check this box if the field should be read-only (users cannot modify its value). This is commonly used for calculated or system-generated fields.
·     Example: "Created Date" or "Record Number".

7: Save the Field

·     Once you’ve configured all the necessary field properties, click Submit or Save to create the field.
·     After saving, ServiceNow will create the new field and add it to the list of columns for the selected table.

- Add the field to a form

After creating the field, you may want to add it to a form so that users can view or update it.

1.   To do this, navigate to System UI > Forms in the application navigator.
2.   Select the form you want to modify (e.g., Incident form).
3.   Open the Form Designer (click on the "Design" icon).
4.   From the Field Navigator on the left side, search for the new field you created.
5.   Drag the field onto the form layout where you want it to appear.
6.   Click Save or Publish to apply the changes.

Test the New Field

·     Go to a record in the table where the field was added (e.g., create a new incident or record).
·     Check if the new field appears on the form.
·     Verify the field behaves as expected (e.g., required, read-only, etc.).

Key Field Types in ServiceNow:

·     String: Short text input (e.g., a name, description).
·     Integer: Whole numbers.
·     Choice: Dropdown list with predefined options.
·     Reference: A reference field to another table (e.g., referencing an User table).
·     Date: A date picker.
·     Date/Time: A combination of date and time.
·     Boolean: Checkbox (True/False).
·     Currency: Currency field with monetary values.

Additional Tips:

·     Field Data Types: Make sure you choose the correct field type based on the type of data you want to store (e.g., Text, Integer, Date).
·     UI Policies/Client Scripts: These can be used to make fields visible, read-only, or mandatory based on certain conditions.
·     Naming Conventions: Follow proper naming conventions for field labels and column names to maintain consistency.

2. Automation Logic :-

Implemented Flow Designer logic: Get Catalog Variables, Create Record, Ask for Approval, Send Email, Update Record.
Triggered on catalog item submission; supports dynamic automation.

- Creation of Flow
- Configuring Trigger
- Configuring Actions
- Flow Chart

3. Buisness Rules :-

UI Policies to display additional fields when certain choices are made (e.g., if device = Others, show description).
Conditional logic and field dependencies configured within ServiceNow.

- Catalog UI Policy Configuration

Scenario: If user selects types of devices is Others, then Please specify field should populate.

Procedure:

1. Navigate to catalog items
2. Open Network Request item
3. In related list, we have Catalog UI policy
4. Click on New button to configure New UI policy
5. Select Applies to as Catalog item
6. Select catalog item as Network Request
7. Provide short description, if required
8. Apply condition>> types of devices is others
9. Click on save, after saving the form will get UI policy actions in the related list
10. Click on New button to configure new UI Policy action, and select the variable which we want to display on condition
11. Make Visible True as per our requirement
12. Update the UI Policy and Test the same on Catalog form.



**PHASE 3 - UI/UX Development & Configuration**

Design user-friendly interfaces and customize layouts to enhance usability and brand consistency.

1. Interface Desgin :-

Designing and customizing ServiceNow interfaces—like forms, lists, and Service Portals—to ensure a user-friendly experience that aligns with business needs, using tools such as UI Policies, UI Actions, and the ServiceNow UI Builder.

- Creation of Sevice Catalog

1. Navigate to Application navigator
2. Click on All >> search for Service Catalog
3. Under Service Catalog>> Maintain items
4. Click on New
5. Fill the details >> Name– Network Request
6. Select Catalog>> Service Catalog
7. Select Category>> Network
8. Fill the Short Description as Network request Management
9. Click on Save.

- Variables Configuration

1. Open the catalog item just created.
2. Scroll down to the Variables related list and click New to create form fields.
3. Select Variables type as Single, Multi line text, reference, choices etc as per requirement
4. Catalog item–  Network Request
5. Order–100,200,300,,,
6. Question– provide the variable label
7. Name–provide the variables name(used for scripting)
8. Tooltip– this will appear when cursor overed on the field
9. Example text – this will suggest what we need to enter on the field.
10. Mandatory, Read-Only– need to configure on demand
11. Auto populate– need to select dependent variable, apply dot walking to get selected value.
12. Click on Save or Submit.

- Variables Types

1. Is this a New connection or Relocation? >> Choice >> New/ Relocation/None
2. If this is a relocation, Please provide your relocated address here>>Strin
3. Types of devices>> Choice>> Laptop/Mobiles/Others
4. Please provide address here>>String
5. Provide device details here>> String
6. If anything else, please specify>> String

- Variable Set Configuration

To enhance form usability:

○   Navigate to the Variable Sets (optional).
○   Follow the same procedure as we used for Variables Creation, for the variable set as well.
○   Apply variable sets to the catalog item.
   Variables Types
1. Opened on behalf of >> Reference>> reference to user table
2. Email Id >> Single line text >> Auto populate by Opened on behalf of variable.
3. User name >>Single line text >> Auto populate by Opened on behalf of variable.
4. Phone Number >>Single line text >> Auto populate by Opened on behalf of variable.
5. Proof of Document >> Attachment

2. Navigation Flow :-

Login to ServiceNow PDI

Copy the Instance domain ex: https://dev402064.service-now.com.

Paste the URL in the Next tab and add Prefix SP to the URL.

ex: https://dev402064.service-now.com/sp.

Search for Network Requests.

Fill the required details and click on submit

New Requests will be generated with request numbers and users will get particular emails on the same.

3. Usability :-

Auto-filled Fields

Fields like:

o   Name---Select Opened on behalf of

o   Email—Auto populate

o   Phone Number-- Auto populate

o   User Name-- Auto populate

Note: auto-filled based on the logged-in user using reference variables only and for every dependent field need to configure Auto populate Value while creating a variable.

4. Tooltips & Help Text :-

Tooltip/Help Texts icons added next to complex fields to guide users

**PHASE 4 - Data Migration, Testing & Security**

Migrate data securely, perform rigorous testing, and ensure system access and data protection mechanisms are in place.

1. Data Handling :-

Variables to Custom Table Records

- In this Case I used Process Automation technique to Capture the Variables through the catalog item and are automatically mapped and stored in a custom table (u_network_database) for structured tracking.

Process to map the variables as shown below.

- Create a flow in flow designer and add Trigger points as per our requirement.

- Select/Use Get Catalog Variables Action to access the Variables from Service Catalog.

- User Create/Update record action and Select the Network database.

- Click on Add fields (+) icon to Map the Variables to particular fields as per our requirements.

2. Access Control :-

While creating a custom table 4 ACL’s are created automatically, in this scenario I used the default ACL’s only

- Access Control Rules (ACLs): Configured to restrict read/write access to sensitive fields depending on the role.

Dynamic Approver Assignment via Flow Designer

- Utilized Flow Designer’s “Ask for Approval” and “If” conditions to determine the appropriate approver (manager or group) based on:

o   Requester’s department (network group manager will receive the approval)

o   Requester State (when request is approved only)

Process to map the variables as shown below.

- Create a flow in flow designer and add Trigger points as per our requirement.

- Select/Use Ask for approval action to send approval request to the particular group/ manager.

- Use If from the flow logic to validate the approval state in Network database table.

3. QA Testing :-

Request Lifecycle Verification

- Simulated real-world submissions and verified:

o   Request creation

o   Approval routing

o   Email notifications

o   Ticket Closure

- Used ServiceNow system logs and audit history to confirm proper execution of each stage.

4. Data Integrity :-

Field Validation and Automation

Mandatory Fields: Enforced on client and server side to prevent incomplete submissions.

Auto-Populate Logic: Set up default values (e.g., current user, location) using catalog client scripts and UI policies.

Approval State Validation: Ensured that a request cannot progress unless the required approval is completed using flow conditions and approval state checks in the workflow.

**PHASE 5 - Deployment, Documentation & Final Presentation**

Deploy the final solution, prepare technical/user documentation, and present the working system to stakeholders.

1. Troubleshooting :-

 Flow Execution Logs: Used Flow Designer's Execution Details to trace flow steps, identify failures, and verify condition paths during approvals and notifications.

· Email Logs: Checked email logs in System Logs → Email → Sent/Received to validate notification triggers and message delivery status.

· Variable Population Issues: Resolved misaligned or missing data bindings using:

- Variable set debugging
- Catalog client scripts for dynamic population

· Form Behaviour Testing: Confirmed UI policies and visibility logic via Service Portal form tests and preview mode.

2. Innovation :-

· Implemented end-to-end automation using:

- Flow Designer (no custom script includes or business rules)
- Dynamic approvals and task creation
- Client scripts and UI policies kept to minimal, essential use

· Ensured maintainability and ease of handoff to admins or future developers.

3. Document Functional Overview :-

· Variables:
- Request type, justification, Portal details, urgency

· Approval Use Cases:
- Manager approval for standard requests
- Network security approval for high-sensitivity requests
- Group approval for department-specific tasks

4. Document Technical Blueprint :-

- Flow Designer workflows (screenshots with explanations)
- Variable-to-field mapping logic from catalog item to custom table
- Custom table schema (u_network_database & u_network_task)
- Approval condition logic in Flow steps
- Portal widget references (if any customizations were made)

5. Document Setup Manual :-

· Provided step-by-step manual for recreating the solution in a new Personal Developer Instance (PDI):

- Catalog item creation
- Variable configuration
- Flow Designer workflow setup
- ACL and role configuration
- Test submission data

· Screenshots and order of operations included for clarity.

6. Explaination Clarity :-

· Documentation and presentation follow logical, sequential structure:
- What → Why → How → Outcome

· Each step includes:
- Clear headings
- Labelled screenshots
- Explanatory notes for replicability.

7. Realisim & Quality :-

- Workflow mimics real enterprise IT request handling, including:
o   Role-based approvals
o   Data validations

- Solution tested with realistic use cases and sample data.

8. Scalability & Future Plan :-

Future enhancements considered:

·   Auto-provisioning via integrations with network tools (e.g., Cisco DNA Centre, Ansible)
·   Orchestration flows using ServiceNow Integration Hub
·   Reporting dashboards for request volume, fulfilments, and etc.
·   Expansion to other IT services (e.g., device provisioning, access requests)
