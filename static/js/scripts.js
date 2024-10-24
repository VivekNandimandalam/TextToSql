document.getElementById('queryForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const question = document.getElementById('question').value;
    console.log(`Submitted question: ${question}`);

    fetch('/submit_query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ 'question': question })
    })
    .then(response => response.json())
    .then(data => {
        console.log(`Response received: ${JSON.stringify(data)}`);

        // Display the generated SQL query in the #generatedSQL div
        if (data.generatedSQL) {
            document.getElementById('generatedSQL').textContent = data.generatedSQL;
        }

        // If there's an image (for charts), show it
        if (data.image) {
            document.getElementById('imageContainer').innerHTML = `<img src="data:image/png;base64,${data.image}" />`;
        } 
        
        // If there's a result, display the result (as HTML table)
        else if (data.result) {
            document.getElementById('result').innerHTML = data.result;
        } 
        
        // If there's an error, display the error message
        else if (data.error) {
            document.getElementById('result').innerHTML = 'Error: ' + data.error;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerHTML = 'An error occurred: ' + error;
    });
});
