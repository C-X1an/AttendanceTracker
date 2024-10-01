document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.closeModal').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.classList.remove('visible');
            })
            document.body.classList.remove('modal-active');
        });
    });

    const sidebar = document.querySelector('.sidebar');
    const menuBtn = document.querySelector('.menu-btn');
    menuBtn.addEventListener('click', function() {
        sidebar.classList.toggle('show');
    });

    document.getElementById('logoutBtn').addEventListener('click', function() {
        if (confirm('Are you sure you want to logout?')) {
            window.location.href = '/logout';
        }
    });
});

function showModal(modal, id=0) {
    if (modal === 'addUser') {
        document.getElementById('addUserModal').classList.add('visible');
    }
    else if (modal === 'editUser') {
        document.getElementById(id + 'editUserModal').classList.add('visible');
    }
    else if (modal === 'resetPassword') {
        document.getElementById(id + 'resetPasswordModal').classList.add('visible');
    }
    else if (modal === 'removeUser') {
        document.getElementById(id + 'removeUserModal').classList.add('visible');
    }
    else if (modal === 'editAttendance') {
        document.getElementById(id + 'editAttendanceModal').classList.add('visible');
    }
    document.body.classList.add('modal-active');
}

function toggleTables(time) {
    if (time === 'morning') {
        document.getElementById('morning-tables').style.display = 'block';
        document.getElementById('afternoon-tables').style.display = 'none';
        document.getElementById('morning-toggle').classList.add('active-toggle');
        document.getElementById('afternoon-toggle').classList.remove('active-toggle');
    } else if (time === 'afternoon') {
        document.getElementById('morning-tables').style.display = 'none';
        document.getElementById('afternoon-tables').style.display = 'block';
        document.getElementById('afternoon-toggle').classList.add('active-toggle');
        document.getElementById('morning-toggle').classList.remove('active-toggle');
    }
}

function download_report() {
    window.location.href = '/generate-report';
}

// Function to show the filter dropdown
function openFilterDropdown(filterId) {
    const dropdown = document.getElementById(filterId);
    dropdown.classList.toggle('show');
}

// Function to filter the attendance table
function filterTable() {
    const table = document.getElementById('attendance-table');
    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    // Get filter values
    const employeeTypeFilters = Array.from(document.querySelectorAll('#employee-type-filter input:checked')).map(el => el.value);
    const departmentFilters = Array.from(document.querySelectorAll('#department-filter input:checked')).map(el => el.value);
    const morningCheckinFilters = Array.from(document.querySelectorAll('#morning-checkin-filter input:checked')).map(el => el.value);
    const afternoonCheckinFilters = Array.from(document.querySelectorAll('#afternoon-checkin-filter input:checked')).map(el => el.value);

    // Loop through rows and hide/show based on filters
    for (let row of rows) {
        const employeeType = row.cells[0].innerText;
        const department = row.cells[2].innerText;
        const morningCheckin = row.cells[3].innerText;
        const afternoonCheckin = row.cells[4].innerText;

        const show = (employeeTypeFilters.length === 0 || employeeTypeFilters.includes(employeeType)) &&
                     (departmentFilters.length === 0 || departmentFilters.includes(department)) &&
                     (morningCheckinFilters.length === 0 || morningCheckinFilters.includes(morningCheckin)) &&
                     (afternoonCheckinFilters.length === 0 || afternoonCheckinFilters.includes(afternoonCheckin));

        row.style.display = show ? '' : 'none';
    }
}

// Hide dropdown if clicked outside
document.addEventListener('click', function(event) {
    const dropdowns = document.querySelectorAll('.filter-dropdown');
    dropdowns.forEach(dropdown => {
        const filterBtn = dropdown.previousElementSibling;
        if (!filterBtn.contains(event.target)) {
            if (!dropdown.contains(event.target)) {
                dropdown.classList.remove('show');
            }
        }
    });
});
