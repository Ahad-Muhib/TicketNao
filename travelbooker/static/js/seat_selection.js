document.addEventListener('DOMContentLoaded', function() {
    const scheduleId = document.getElementById('schedule-id').value;
    const seatLayout = document.getElementById('seat-layout');
    const fareElement = document.getElementById('fare');
    const totalPriceElement = document.getElementById('total-price');
    const selectedSeatCount = document.getElementById('selected-seat-count');
    const selectedSeatsContainer = document.getElementById('selected-seats');
    const selectedSeatIdsInput = document.getElementById('selected-seat-ids');
    
    // Store selected seats and their details
    const selectedSeats = new Map();
    let farePerSeat = 0;

    // Fetch seat data from API
    fetch(`/api/schedule/${scheduleId}/seats/`)
        .then(response => response.json())
        .then(data => {
            // Set fare value
            farePerSeat = data.fare;
            fareElement.textContent = farePerSeat.toFixed(2);
            
            // Generate seat layout
            renderSeatLayout(data);
        })
        .catch(error => {
            console.error('Error fetching seat data:', error);
            seatLayout.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i> Failed to load seat layout. Please try again later.
                </div>
            `;
        });

    // Function to render the seat layout
    function renderSeatLayout(data) {
        const seats = data.seats;
        const layout = data.bus_layout;
        
        // Group seats by deck if multiple decks exist
        const seatsByDeck = {};
        seats.forEach(seat => {
            const deck = seat.deck || 'main';
            if (!seatsByDeck[deck]) seatsByDeck[deck] = [];
            seatsByDeck[deck].push(seat);
        });
        
        // Clear loading spinner
        seatLayout.innerHTML = '';
        
        // Create layout for each deck
        Object.keys(seatsByDeck).sort().forEach(deck => {
            const deckSeats = seatsByDeck[deck];
            
            // Create deck container if multiple decks
            const deckContainer = document.createElement('div');
            deckContainer.className = 'seat-deck mb-4';
            
            if (Object.keys(seatsByDeck).length > 1) {
                const deckTitle = document.createElement('h5');
                deckTitle.textContent = deck === 'main' ? 'Main Deck' : deck.charAt(0).toUpperCase() + deck.slice(1) + ' Deck';
                deckTitle.className = 'deck-title mb-3';
                deckContainer.appendChild(deckTitle);
            }
            
            // Create the bus outline
            const busContainer = document.createElement('div');
            busContainer.className = 'bus-container';
            
            // Create driver's area
            const driverArea = document.createElement('div');
            driverArea.className = 'driver-area';
            driverArea.innerHTML = '<i class="fas fa-steering-wheel"></i>';
            busContainer.appendChild(driverArea);
            
            // Create seat grid
            const seatGrid = document.createElement('div');
            seatGrid.className = 'seat-grid';
            seatGrid.style.gridTemplateColumns = `repeat(${layout.cols}, 1fr)`;
            seatGrid.style.gridTemplateRows = `repeat(${layout.rows}, 1fr)`;
            
            // Map of positions to detect empty slots for aisle
            const positionMap = new Map();
            deckSeats.forEach(seat => {
                positionMap.set(`${seat.x}-${seat.y}`, seat);
            });
            
            // Fill the grid
            for (let y = 0; y < layout.rows; y++) {
                for (let x = 0; x < layout.cols; x++) {
                    const key = `${x}-${y}`;
                    const seatData = positionMap.get(key);
                    
                    if (seatData) {
                        // Create seat element
                        const seatElement = document.createElement('div');
                        seatElement.className = `seat ${seatData.type || ''} ${seatData.booked ? 'booked' : 'available'}`;
                        seatElement.dataset.seatId = seatData.id;
                        seatElement.dataset.seatNumber = seatData.number;
                        seatElement.title = `Seat ${seatData.number} (${seatData.type || 'Regular'})`;
                        seatElement.innerHTML = `<span>${seatData.number}</span>`;
                        
                        // Add click event for available seats
                        if (!seatData.booked) {
                            seatElement.addEventListener('click', function() {
                                toggleSeatSelection(this, seatData);
                            });
                        }
                        
                        seatGrid.appendChild(seatElement);
                    } else {
                        // Create empty space (could be aisle or just empty)
                        const emptySpace = document.createElement('div');
                        emptySpace.className = 'seat-space';
                        seatGrid.appendChild(emptySpace);
                    }
                }
            }
            
            busContainer.appendChild(seatGrid);
            deckContainer.appendChild(busContainer);
            seatLayout.appendChild(deckContainer);
        });
        
        // Add seat legend
        const legend = document.createElement('div');
        legend.className = 'seat-legend mt-3';
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
        seatLayout.appendChild(legend);
    }

    // Function to toggle seat selection
    function toggleSeatSelection(seatElement, seatData) {
        const seatId = seatData.id;
        
        if (selectedSeats.has(seatId)) {
            // Deselect the seat
            selectedSeats.delete(seatId);
            seatElement.classList.remove('selected');
        } else {
            // Select the seat
            selectedSeats.set(seatId, {
                id: seatId,
                number: seatData.number,
                type: seatData.type || 'Regular'
            });
            seatElement.classList.add('selected');
        }
        
        // Update the UI
        updateSelectedSeatsUI();
    }

    // Function to update selected seats UI
    function updateSelectedSeatsUI() {
        // Update selected seat count
        selectedSeatCount.textContent = selectedSeats.size;
        
        // Update total price
        const totalPrice = selectedSeats.size * farePerSeat;
        totalPriceElement.textContent = totalPrice.toFixed(2);
        
        // Update selected seats display
        if (selectedSeats.size === 0) {
            selectedSeatsContainer.innerHTML = '<p>No seats selected</p>';
        } else {
            selectedSeatsContainer.innerHTML = '';
            const seatList = document.createElement('div');
            seatList.className = 'selected-seat-list';
            
            selectedSeats.forEach(seat => {
                const seatItem = document.createElement('div');
                seatItem.className = 'selected-seat-item';
                seatItem.innerHTML = `
                    <span class="seat-number">Seat ${seat.number}</span>
                    <span class="seat-type">${seat.type}</span>
                    <span class="seat-price">₹${farePerSeat.toFixed(2)}</span>
                    <button type="button" class="btn-remove-seat" data-seat-id="${seat.id}">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                seatList.appendChild(seatItem);
            });
            
            selectedSeatsContainer.appendChild(seatList);
            
            // Add remove seat event listeners
            document.querySelectorAll('.btn-remove-seat').forEach(button => {
                button.addEventListener('click', function() {
                    const seatId = this.dataset.seatId;
                    // Find and deselect the seat in the layout
                    const seatElement = document.querySelector(`.seat[data-seat-id="${seatId}"]`);
                    if (seatElement) {
                        seatElement.classList.remove('selected');
                    }
                    // Remove from selected seats
                    selectedSeats.delete(parseInt(seatId));
                    // Update UI
                    updateSelectedSeatsUI();
                });
            });
        }
        
        // Update hidden input with selected seat IDs
        selectedSeatIdsInput.value = JSON.stringify(Array.from(selectedSeats.keys()));
    }

    // Initialize form with user data if available
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        // Prefill email if user is logged in
        const userEmail = document.querySelector('a#userDropdown')?.textContent.trim();
        if (userEmail) {
            const emailInput = document.getElementById('passenger-email');
            if (emailInput && !emailInput.value) {
                emailInput.value = userEmail;
            }
        }
    }
});
