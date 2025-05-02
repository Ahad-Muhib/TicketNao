document.addEventListener('DOMContentLoaded', function() {
    // Initialize dataTables
    const dataTables = document.querySelectorAll('.datatable');
    if (dataTables.length > 0 && typeof simpleDatatables !== 'undefined') {
        dataTables.forEach(table => {
            new simpleDatatables.DataTable(table);
        });
    }

    // Confirm deletion modals
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Populate destination cities based on source
    window.populateCities = function(sourceInput, destinationId) {
        const sourceValue = sourceInput.value;
        const destinationInput = document.getElementById(destinationId);
        
        if (!destinationInput) return;
        
        // If it's a select element
        if (destinationInput.tagName === 'SELECT') {
            // Enable all options first
            for (let i = 0; i < destinationInput.options.length; i++) {
                destinationInput.options[i].disabled = false;
            }
            
            // Disable the matching source
            for (let i = 0; i < destinationInput.options.length; i++) {
                if (destinationInput.options[i].value === sourceValue) {
                    destinationInput.options[i].disabled = true;
                    
                    // If this was the selected option, reset it
                    if (destinationInput.value === sourceValue) {
                        destinationInput.value = '';
                    }
                    break;
                }
            }
        } else {
            // Regular input field
            if (destinationInput.value === sourceValue) {
                destinationInput.value = '';
            }
        }
    };

    // Dynamic form fields for seat layout (used in bus creation)
    const busTypeSelect = document.getElementById('bus_type');
    const totalSeatsInput = document.getElementById('total_seats');
    
    if (busTypeSelect && totalSeatsInput) {
        // Set default seat count based on bus type
        busTypeSelect.addEventListener('change', function() {
            const busType = this.value;
            switch(busType) {
                case 'AC':
                    totalSeatsInput.value = 36;
                    break;
                case 'Non-AC':
                    totalSeatsInput.value = 40;
                    break;
                case 'Sleeper':
                    totalSeatsInput.value = 30;
                    break;
                case 'Semi-Sleeper':
                    totalSeatsInput.value = 32;
                    break;
                case 'Luxury':
                    totalSeatsInput.value = 28;
                    break;
                default:
                    totalSeatsInput.value = 36;
            }
        });
    }

    // Date range validation for schedules
    const departureTimeInput = document.getElementById('departure_time');
    const arrivalTimeInput = document.getElementById('arrival_time');
    
    if (departureTimeInput && arrivalTimeInput) {
        departureTimeInput.addEventListener('change', function() {
            // Ensure arrival is after departure
            if (arrivalTimeInput.value && arrivalTimeInput.value <= departureTimeInput.value) {
                // Set arrival to departure + 1 hour as minimum
                const departureDate = new Date(departureTimeInput.value);
                departureDate.setHours(departureDate.getHours() + 1);
                
                // Format for datetime-local input
                const year = departureDate.getFullYear();
                const month = String(departureDate.getMonth() + 1).padStart(2, '0');
                const day = String(departureDate.getDate()).padStart(2, '0');
                const hours = String(departureDate.getHours()).padStart(2, '0');
                const minutes = String(departureDate.getMinutes()).padStart(2, '0');
                
                arrivalTimeInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
            }
        });
        
        arrivalTimeInput.addEventListener('change', function() {
            // Warn if arrival is before departure
            if (departureTimeInput.value && arrivalTimeInput.value <= departureTimeInput.value) {
                alert('Arrival time must be after departure time.');
                arrivalTimeInput.focus();
            }
        });
    }

    // Filter functionality for admin tables
    const filterInputs = document.querySelectorAll('.table-filter');
    filterInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const tableId = this.dataset.tableTarget;
            const table = document.getElementById(tableId);
            if (!table) return;
            
            const searchText = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchText) ? '' : 'none';
            });
        });
    });
});

// Function to toggle seat availability in admin panel
function toggleSeatStatus(seatId, button) {
    // Send request to toggle status
    fetch(`/admin-panel/seats/${seatId}/toggle-status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update button text and class
            if (data.is_active) {
                button.textContent = 'Active';
                button.classList.remove('btn-danger');
                button.classList.add('btn-success');
            } else {
                button.textContent = 'Inactive';
                button.classList.remove('btn-success');
                button.classList.add('btn-danger');
            }
        } else {
            alert('Failed to update seat status.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating seat status.');
    });
}

// Helper function to get CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
