document.addEventListener('DOMContentLoaded', function() {
    // Fetch seats data for the schedule
    const scheduleId = document.getElementById('schedule-id').value;
    
    fetchSeats(scheduleId);
    
    // Handle seat selection form submission
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(event) {
            const selectedSeats = document.querySelectorAll('.seat.selected');
            if (selectedSeats.length === 0) {
                event.preventDefault();
                showAlert('Please select at least one seat', 'danger');
            }
        });
    }
});

// Fetch seats from API
function fetchSeats(scheduleId) {
    fetch(`/api/seats/${scheduleId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            renderSeats(data.seats, data.fare);
        })
        .catch(error => {
            console.error('Error fetching seats:', error);
            showAlert('Failed to load seats. Please try again.', 'danger');
        });
}

// Render the bus layout with seats
function renderSeats(seats, fare) {
    const seatContainer = document.getElementById('seat-layout');
    const selectedSeatsContainer = document.getElementById('selected-seats');
    const totalPriceElement = document.getElementById('total-price');
    
    // Clear existing contents
    seatContainer.innerHTML = '';
    selectedSeatsContainer.innerHTML = '';
    totalPriceElement.textContent = '0.00';
    
    // Set fare
    document.getElementById('fare').textContent = fare.toFixed(2);
    
    // Create a map for seat layout
    const busLayout = document.createElement('div');
    busLayout.className = 'bus-layout';
    
    // Create a steering wheel element
    const steeringWheel = document.createElement('div');
    steeringWheel.className = 'steering-wheel';
    steeringWheel.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="4"></circle><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"></line><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"></line><line x1="14.83" y1="9.17" x2="19.07" y2="4.93"></line><line x1="4.93" y1="19.07" x2="9.17" y2="14.83"></line></svg>';
    busLayout.appendChild(steeringWheel);
    
    // Create seats container
    const seatsContainer = document.createElement('div');
    seatsContainer.className = 'seats-container';
    
    // Calculate rows and columns
    const totalSeats = seats.length;
    const seatsPerRow = 4; // 2 seats on each side with an aisle
    const rows = Math.ceil(totalSeats / seatsPerRow);
    
    let seatIndex = 0;
    for (let row = 0; row < rows; row++) {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'seat-row';
        
        for (let col = 0; col < seatsPerRow; col++) {
            // Add aisle after the 2nd seat
            if (col === 2) {
                const aisleDiv = document.createElement('div');
                aisleDiv.className = 'aisle';
                rowDiv.appendChild(aisleDiv);
            }
            
            if (seatIndex < totalSeats) {
                const seat = seats[seatIndex];
                const seatDiv = document.createElement('div');
                seatDiv.className = `seat ${seat.type.toLowerCase()} ${seat.booked ? 'booked' : 'available'}`;
                seatDiv.dataset.id = seat.id;
                seatDiv.dataset.number = seat.number;
                seatDiv.textContent = seat.number;
                
                // Add click event for seat selection
                if (!seat.booked) {
                    seatDiv.addEventListener('click', function() {
                        toggleSeatSelection(seatDiv, fare);
                    });
                }
                
                rowDiv.appendChild(seatDiv);
                seatIndex++;
            } else {
                // Empty space for incomplete rows
                const emptyDiv = document.createElement('div');
                emptyDiv.className = 'seat-placeholder';
                rowDiv.appendChild(emptyDiv);
            }
        }
        
        seatsContainer.appendChild(rowDiv);
    }
    
    busLayout.appendChild(seatsContainer);
    seatContainer.appendChild(busLayout);
    
    // Add legend
    const legend = document.createElement('div');
    legend.className = 'seat-legend';
    legend.innerHTML = `
        <div class="legend-item">
            <div class="seat-sample available"></div>
            <span>Available</span>
        </div>
        <div class="legend-item">
            <div class="seat-sample selected"></div>
            <span>Selected</span>
        </div>
        <div class="legend-item">
            <div class="seat-sample booked"></div>
            <span>Booked</span>
        </div>
    `;
    seatContainer.appendChild(legend);
}

// Toggle seat selection
function toggleSeatSelection(seatElement, fare) {
    const seatId = seatElement.dataset.id;
    const seatNumber = seatElement.dataset.number;
    const selectedSeatsContainer = document.getElementById('selected-seats');
    const totalPriceElement = document.getElementById('total-price');
    
    // Toggle the selected class
    seatElement.classList.toggle('selected');
    
    // Update the hidden form field for selected seats
    updateSelectedSeatsInput();
    
    // Update the selected seats display
    renderSelectedSeats();
    
    // Update total price
    updateTotalPrice(fare);
}

// Update the hidden input field with selected seat IDs
function updateSelectedSeatsInput() {
    const selectedSeats = document.querySelectorAll('.seat.selected');
    const selectedSeatIdsInput = document.getElementById('selected-seat-ids');
    
    const seatIds = Array.from(selectedSeats).map(seat => seat.dataset.id);
    selectedSeatIdsInput.value = JSON.stringify(seatIds);
}

// Render the list of selected seats
function renderSelectedSeats() {
    const selectedSeats = document.querySelectorAll('.seat.selected');
    const selectedSeatsContainer = document.getElementById('selected-seats');
    
    selectedSeatsContainer.innerHTML = '';
    
    if (selectedSeats.length === 0) {
        selectedSeatsContainer.innerHTML = '<p>No seats selected</p>';
        return;
    }
    
    const seatList = document.createElement('ul');
    seatList.className = 'list-group';
    
    Array.from(selectedSeats)
        .sort((a, b) => parseInt(a.dataset.number) - parseInt(b.dataset.number))
        .forEach(seat => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            listItem.innerHTML = `
                Seat ${seat.dataset.number}
                <button type="button" class="btn btn-sm btn-outline-danger" 
                    onclick="removeSeat('${seat.dataset.id}')">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">
                      <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                    </svg>
                </button>
            `;
            seatList.appendChild(listItem);
            
            // Add a hidden input for each selected seat
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'seats[]';
            hiddenInput.value = seat.dataset.id;
            document.getElementById('booking-form').appendChild(hiddenInput);
        });
    
    selectedSeatsContainer.appendChild(seatList);
}

// Remove a seat from selection
function removeSeat(seatId) {
    const seatElement = document.querySelector(`.seat[data-id="${seatId}"]`);
    if (seatElement) {
        seatElement.classList.remove('selected');
        
        // Update hidden input and display
        updateSelectedSeatsInput();
        renderSelectedSeats();
        
        // Update total price
        const fare = parseFloat(document.getElementById('fare').textContent);
        updateTotalPrice(fare);
    }
}

// Update the total price based on selected seats
function updateTotalPrice(fare) {
    const selectedSeats = document.querySelectorAll('.seat.selected');
    const totalPriceElement = document.getElementById('total-price');
    
    const totalPrice = selectedSeats.length * fare;
    totalPriceElement.textContent = totalPrice.toFixed(2);
}

// Show alert message
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    
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
