// Select the radio buttons and the custom text input
const radios = document.querySelectorAll('input[name="file-pages-radio"]');
const customInput = document.getElementById('file-pages-custom');

// Add an event listener to each radio button
radios.forEach(radio => {
     radio.addEventListener('change', function() {
          // Enable custom input only if the "custom pages" radio (value="4") is selected
          customInput.disabled = (this.value !== "4");
     });
});