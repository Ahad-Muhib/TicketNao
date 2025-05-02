document.addEventListener('DOMContentLoaded', function() {
    // Initialize data tables if exists
    const dataTables = document.querySelectorAll('.table-datatable');
    if (dataTables.length > 0) {
        dataTables.forEach(table => {
            new simpleDatatables.DataTable(table, {
                searchable: true,
                fixedHeight: true,
                perPage: 10
            });
        });
    }
    
    // Form validation for admin forms
    const adminForms = document.querySelectorAll('.needs-validation');
    adminForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Delete confirmation
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                event.preventDefault();
            }
        });
    });
    
    // Initialize datetime pickers
    const datetimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    datetimeInputs.forEach(input => {
        // Set min date to today
        const now = new Date();
        const today = now.toISOString().slice(0, 16);
        input.min = today;
    });
    
    // Handle bus type selection
    const busTypeSelect = document.getElementById('bus-type');
    const amenitiesField = document.getElementById('amenities');
    
    if (busTypeSelect && amenitiesField) {
        busTypeSelect.addEventListener('change', function() {
            const busType = busTypeSelect.value;
            let defaultAmenities = '';
            
            // Set default amenities based on bus type
            switch (busType) {
                case 'AC Sleeper':
                    defaultAmenities = 'AC, Sleeper Berths, Blanket, Pillow, Charging Point, Water Bottle';
                    break;
                case 'AC Seater':
                    defaultAmenities = 'AC, Reclining Seats, Charging Point, Water Bottle';
                    break;
                case 'Non-AC Sleeper':
                    defaultAmenities = 'Sleeper Berths, Blanket';
                    break;
                case 'Non-AC Seater':
                    defaultAmenities = 'Standard Seats';
                    break;
                case 'Deluxe':
                    defaultAmenities = 'AC, Reclining Seats, TV, WiFi, Charging Point, Snacks, Water Bottle';
                    break;
            }
            
            // Only update if the field is empty or contains default values
            if (!amenitiesField.value || 
                amenitiesField.value === 'AC, Sleeper Berths, Blanket, Pillow, Charging Point, Water Bottle' ||
                amenitiesField.value === 'AC, Reclining Seats, Charging Point, Water Bottle' ||
                amenitiesField.value === 'Sleeper Berths, Blanket' ||
                amenitiesField.value === 'Standard Seats' ||
                amenitiesField.value === 'AC, Reclining Seats, TV, WiFi, Charging Point, Snacks, Water Bottle') {
                amenitiesField.value = defaultAmenities;
            }
        });
    }
    
    // Handle dashboard stats animations
    const statCounters = document.querySelectorAll('.stat-counter');
    if (statCounters.length > 0) {
        statCounters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            let count = 0;
            const duration = 2000; // 2 seconds
            const increment = target / (duration / 16); // 60fps
            
            const updateCounter = () => {
                if (count < target) {
                    count += increment;
                    counter.textContent = Math.ceil(count);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };
            
            updateCounter();
        });
    }
});

// Dynamic city dropdown population
function populateCities(selectElement, targetSelectId) {
    const targetSelect = document.getElementById(targetSelectId);
    if (!targetSelect) return;
    
    // Clear existing options except the first one
    while (targetSelect.options.length > 1) {
        targetSelect.remove(1);
    }
    
    // Get major cities and populate the dropdown
    const cities = [
        'Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore', 'Hyderabad', 'Ahmedabad', 
        'Pune', 'Surat', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 
        'Bhopal', 'Visakhapatnam', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra'
    ];
    
    // Get the selected city to exclude
    const selectedCity = selectElement.value;
    
    // Add all other cities
    cities.forEach(city => {
        if (city !== selectedCity) {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            targetSelect.appendChild(option);
        }
    });
}
