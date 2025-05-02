document.addEventListener('DOMContentLoaded', function() {
    // Set minimum date for date inputs to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    if (dateInputs.length > 0) {
        const today = new Date().toISOString().split('T')[0];
        dateInputs.forEach(input => {
            input.setAttribute('min', today);
            // If no date is set, default to today
            if (!input.value) {
                input.value = today;
            }
        });
    }

    // Populate cities function for search forms
    window.populateCities = function(sourceInput, destinationId) {
        const destinationInput = document.getElementById(destinationId);
        if (!destinationInput) return;

        // Clear destination if source and destination are the same
        if (destinationInput.value === sourceInput.value) {
            destinationInput.value = '';
        }
    };

    // Print ticket function for booking confirmation page
    window.printTicket = function() {
        window.print();
    };

    // Initialize any dataTables on the page
    const dataTables = document.querySelectorAll('.datatable');
    if (dataTables.length > 0 && typeof simpleDatatables !== 'undefined') {
        dataTables.forEach(table => {
            new simpleDatatables.DataTable(table);
        });
    }

    // Booking form validation
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(event) {
            const selectedSeats = document.querySelectorAll('.seat.selected');
            if (selectedSeats.length === 0) {
                event.preventDefault();
                
                // Show alert
                const alertContainer = document.getElementById('alert-container');
                alertContainer.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        Please select at least one seat.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
                
                // Scroll to alert
                alertContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    // Handle destination options based on selected source
    const sourceSelect = document.getElementById('source');
    if (sourceSelect && sourceSelect.tagName === 'SELECT') {
        sourceSelect.addEventListener('change', function() {
            const destinationSelect = document.getElementById('destination');
            if (!destinationSelect) return;

            const selectedSource = this.value;
            
            // Enable all destination options first
            for (let i = 0; i < destinationSelect.options.length; i++) {
                destinationSelect.options[i].disabled = false;
            }
            
            // Disable the source city in destination dropdown
            for (let i = 0; i < destinationSelect.options.length; i++) {
                if (destinationSelect.options[i].value === selectedSource) {
                    destinationSelect.options[i].disabled = true;
                    
                    // If currently selected destination is now disabled, reset selection
                    if (destinationSelect.value === selectedSource) {
                        destinationSelect.value = '';
                    }
                    break;
                }
            }
        });
    }
});
