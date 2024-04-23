window.onload = function() {
    var timestampDiv = document.getElementById('timestamp');
    var d = new Date();
    var timestamp = d.toLocaleString(); // Get the current timestamp in a human-readable format
    timestampDiv.innerHTML = "File generated at: " + timestamp;
};
