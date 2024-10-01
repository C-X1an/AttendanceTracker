document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.menu-button').addEventListener('click', function() {
        document.querySelector('.navbar').classList.toggle('show');
    });

    const morningCheckbox = document.getElementById('morning-present');
    const afternoonCheckbox = document.getElementById('afternoon-present');
    const morningDropdown = document.getElementById('morning-dropdown');
    const afternoonDropdown = document.getElementById('afternoon-dropdown');
    const remarksTextarea = document.getElementById('attendance-remarks');

    function updateVisibility() {
        // Check morning attendance
        if (morningCheckbox.checked) {
            morningDropdown.classList.remove('show');
        } else {
            morningDropdown.classList.add('show');
        }

        // Check afternoon attendance
        if (afternoonCheckbox.checked) {
            afternoonDropdown.classList.remove('show');
        } else {
            afternoonDropdown.classList.add('show');
        }

        // Show remarks textarea if any dropdown is visible
        if (morningDropdown.classList.contains('show') || afternoonDropdown.classList.contains('show')) {
            remarksTextarea.style.display = 'block';
        } else {
            remarksTextarea.style.display = 'none';
        }
    }

    // Attach change event listeners to checkboxes
    morningCheckbox.addEventListener('change', updateVisibility);
    afternoonCheckbox.addEventListener('change', updateVisibility);

    // Initial call to set the correct visibility on page load
    updateVisibility();
})

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
}
