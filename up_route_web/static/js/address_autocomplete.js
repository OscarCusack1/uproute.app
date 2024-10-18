
function bingMapsReady() {
    Microsoft.Maps.loadModule("Microsoft.Maps.AutoSuggest", {
      callback: onLoad,
      errorCallback: logError,
      credentials: Agg3Y0d4Y9AXCgHr7czdzqzmBzyk5GHVJeORQ3hqzdYlxvqA_SpywmgADpXJtJij,
    });
  
    function onLoad() {
      var options = { maxResults: 8 };
      initAutosuggestControl(options, "address-field", "address-location-input-container");
      initAutosuggestControl(options, "start-location-input", "start-location-input-container");
      initAutosuggestControl(options, "end-location-input", "end-location-input-container");
    }
}
  
function initAutosuggestControl(
    options,
    suggestionBoxId,
    suggestionContainerId
  ) {
    console.log(`initAutosuggestControl called for ${suggestionBoxId}`);
    var manager = new Microsoft.Maps.AutosuggestManager(options);
    manager.attachAutosuggest(
      "#" + suggestionBoxId,
      "#" + suggestionContainerId,
      selectedSuggestion
    );
  
    function selectedSuggestion(suggestionResult) {
      var inputElement = document.getElementById(suggestionBoxId)
      inputElement.value = suggestionResult.formattedSuggestion;
      var event = new Event('change', { bubbles: true });
      inputElement.dispatchEvent(event);
    }
  }
  
  
  function logError(message) {
    console.log(message);
  }

// Function to update the map with all addresses
function updateMap() {
    // Fetch the map HTML from the server
    console.log('Fetching map...');
    fetch('/address/get_map/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error from server:', data.error);
                return;
            }
            // Get the map container
            const mapContainer = document.getElementById('map-container');
            
            // Update the map container with the new map HTML
            mapContainer.innerHTML = data.map_html;
        })
        .catch(error => {
            console.error('Error fetching map:', error);
        });
}