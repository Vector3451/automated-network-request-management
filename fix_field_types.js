// Fix Script: Set proper types on all custom table fields
// Run this in System Definition > Fix Scripts > New

var fields = [
    // u_network_request fields
    {table: 'u_network_request', element: 'u_requested_for', type: 'reference', ref: 'sys_user'},
    {table: 'u_network_request', element: 'u_location', type: 'reference', ref: 'cmn_location'},
    {table: 'u_network_request', element: 'u_network_group', type: 'reference', ref: 'sys_user_group'},
    {table: 'u_network_request', element: 'u_approver', type: 'reference', ref: 'sys_user'},
    {table: 'u_network_request', element: 'u_requested_for_email', type: 'string'},
    {table: 'u_network_request', element: 'u_business_justification', type: 'string'},
    {table: 'u_network_request', element: 'u_approval_notes', type: 'string'},
    {table: 'u_network_request', element: 'u_requested_for_phone', type: 'string'},
    {table: 'u_network_request', element: 'u_access_level', type: 'string'},
    {table: 'u_network_request', element: 'u_device_other', type: 'string'},
    {table: 'u_network_request', element: 'u_portal_details', type: 'string'},
    {table: 'u_network_request', element: 'u_department', type: 'string'},
    {table: 'u_network_request', element: 'u_request_type', type: 'string'},
    {table: 'u_network_request', element: 'u_device', type: 'string'},
    {table: 'u_network_request', element: 'u_description', type: 'string'},
    {table: 'u_network_request', element: 'u_urgency', type: 'string'},
    {table: 'u_network_request', element: 'u_requested_for_username', type: 'string'},
    {table: 'u_network_request', element: 'u_short_description', type: 'string'},
    {table: 'u_network_request', element: 'u_approval_state', type: 'string'},
    {table: 'u_network_request', element: 'u_request_number', type: 'string'},
    
    // u_network_task fields
    {table: 'u_network_task', element: 'u_network_request', type: 'reference', ref: 'u_network_request'},
    {table: 'u_network_task', element: 'u_configuration_item', type: 'reference', ref: 'cmdb_ci'},
    {table: 'u_network_task', element: 'u_task_type', type: 'string'},
    {table: 'u_network_task', element: 'u_work_notes', type: 'string'},
    {table: 'u_network_task', element: 'u_implementation_plan', type: 'string'},
    {table: 'u_network_task', element: 'u_rollback_plan', type: 'string'},
    
    // u_network_database fields
    {table: 'u_network_database', element: 'u_assignment_group', type: 'reference', ref: 'sys_user_group'},
    {table: 'u_network_database', element: 'u_assigned_to', type: 'reference', ref: 'sys_user'},
    {table: 'u_network_database', element: 'u_request_number', type: 'string'},
    {table: 'u_network_database', element: 'u_customer_document', type: 'string'},
    {table: 'u_network_database', element: 'u_device_details', type: 'string'},
    {table: 'u_network_database', element: 'u_date_of_enquiry', type: 'date'},
    {table: 'u_network_database', element: 'u_customer_address', type: 'string'},
    {table: 'u_network_database', element: 'u_approval_state', type: 'string'},
    {table: 'u_network_database', element: 'u_requested_for', type: 'string'},
];

var count = 0;
for (var i = 0; i < fields.length; i++) {
    var f = fields[i];
    var gr = new GlideRecord('sys_dictionary');
    gr.addQuery('name', f.table);
    gr.addQuery('element', f.element);
    gr.query();
    if (gr.next()) {
        gr.setValue('type', f.type);
        if (f.ref) {
            gr.setValue('reference', f.ref);
        }
        gr.update();
        count++;
        gs.info('Fixed: ' + f.table + '.' + f.element + ' -> ' + f.type);
    } else {
        gs.info('NOT FOUND: ' + f.table + '.' + f.element);
    }
}
gs.info('Total fixed: ' + count + ' fields');
