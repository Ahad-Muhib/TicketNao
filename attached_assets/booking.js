document.addEventListener('DOMContentLoaded', function() {
    // Form validation for booking forms
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(event) {
            if (!validateBookingForm()) {
                event.preventDefault();
            }
        });
    }
    
    // Search form validation
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            if (!validateSearchForm()) {
                event.preventDefault();
            }
        });
    }
    
    // Initialize date pickers if they exist
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        input.min = today;
    });
});

// Validate the booking form
function validateBookingForm() {
    const passengerName = document.getElementById('passenger-name');
    const passengerEmail = document.getElementById('passenger-email');
    const passengerPhone = document.getElementById('passenger-phone');
    
    let isValid = true;
    
    // Check if passenger name is provided
    if (!passengerName.value.trim()) {
        showInputError(passengerName, 'Passenger name is required');
        isValid = false;
    } else {
        clearInputError(passengerName);
    }
    
    // Check if email is valid
    if (!passengerEmail.value.trim()) {
        showInputError(passengerEmail, 'Email is required');
        isValid = false;
    } else if (!isValidEmail(passengerEmail.value.trim())) {
        showInputError(passengerEmail, 'Please enter a valid email address');
        isValid = false;
    } else {
        clearInputError(passengerEmail);
    }
    
    // Check if phone is valid
    if (!passengerPhone.value.trim()) {
        showInputError(passengerPhone, 'Phone number is required');
        isValid = false;
    } else if (!isValidPhone(passengerPhone.value.trim())) {
        showInputError(passengerPhone, 'Please enter a valid phone number');
        isValid = false;
    } else {
        clearInputError(passengerPhone);
    }
    
    // Check if at least one seat is selected
    const selectedSeats = document.querySelectorAll('.seat.selected');
    if (selectedSeats.length === 0) {
        showAlert('Please select at least one seat', 'danger');
        isValid = false;
    }
    
    return isValid;
}

// Validate the search form
function validateSearchForm() {
    const source = document.getElementById('source');
    const destination = document.getElementById('destination');
    const departureDate = document.getElementById('departure-date');
    
    let isValid = true;
    
    // Check if source is selected
    if (!source.value) {
        showInputError(source, 'Please select a source');
        isValid = false;
    } else {
        clearInputError(source);
    }
    
    // Check if destination is selected
    if (!destination.value) {
        showInputError(destination, 'Please select a destination');
        isValid = false;
    } else {
        clearInputError(destination);
    }
    
    // Check if source and destination are different
    if (source.value && destination.value && source.value === destination.value) {
        showInputError(destination, 'Source and destination cannot be the same');
        isValid = false;
    }
    
    // Check if departure date is selected
    if (!departureDate.value) {
        showInputError(departureDate, 'Please select a departure date');
        isValid = false;
    } else {
        clearInputError(departureDate);
    }
    
    return isValid;
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate phone number format
function isValidPhone(phone) {
    // Basic phone validation - at least 10 digits
    const phoneRegex = /^\+?[0-9]{10,15}$/;
    return phoneRegex.test(phone);
}

// Show error for input field
function showInputError(inputElement, message) {
    // Remove any existing error message
    clearInputError(inputElement);
    
    // Add error class to input
    inputElement.classList.add('is-invalid');
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    // Insert error message after input
    inputElement.parentNode.appendChild(errorDiv);
}

// Clear error for input field
function clearInputError(inputElement) {
    inputElement.classList.remove('is-invalid');
    
    // Remove any existing error message
    const errorMessage = inputElement.parentNode.querySelector('.invalid-feedback');
    if (errorMessage) {
        errorMessage.remove();
    }
}

// Show alert message
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 150);
    }, 5000);
}

// Print ticket
function printTicket() {
    window.print();
}
