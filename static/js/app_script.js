// Attach an event listener to the form submission
document.getElementById("chat-form").addEventListener("submit", function (event) {
    event.preventDefault(); // prevent the form from submitting in the traditional way
    showSpinner();
    sendMessage();
});

document.getElementById("pre-form").addEventListener("submit", function (event) {
    event.preventDefault(); // prevent the form from submitting in the traditional way
    userName = document.getElementById("user-name").value;
    userCountry = document.getElementById("country").value;
    legalCase = document.getElementById("legal-case").value;
    initialMessage = `Hello, my name is ${userName}, I am from ${userCountry},
    and I am seeking legal advice about ${legalCase}`;
    showSpinner();
    sendMessage(initialMessage);
    hidePreForm();
    showForm();
});

document.getElementById("results").addEventListener("submit", function (event) {
    event.preventDefault(); // prevent the form from submitting in the traditional way
    showSpinner();
    sendMessage();
});

let assistant_alias = ''

// Function to send user input to the server
function sendMessage(preData='') {
    // Get user input from the input field
    let userInput = document.getElementById("user-input").value +
    preData;
    
    let results = event.submitter.value

    // Display the user's message in the chat container
    if (userInput !== ''){
    document.getElementById("chat-container").innerHTML += `<p><span class='client-chat'> Client</span>: ${userInput}</p>`;
    scrollToBottom(); // Scroll to the bottom of the chat container
    }   
    // Clear the text input from the button 
    document.getElementById("user-input").value = "";

    // Make an AJAX request to your Flask server with the user input
    function makeAjaxRequest(url, callback) {
        const xhr = new XMLHttpRequest();

        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    appendBotMessage(response);
                    hideSpinner();
                } else {
                    console.log('Error: ' + xhr.status);
                    hideSpinner();
                }
            }
        };

        xhr.open('GET', url, true);
        xhr.send();
    }
    // Configure and send the AJAX request
    makeAjaxRequest('/chat?user-input=' + encodeURIComponent(userInput)+'&results=' + encodeURIComponent(results), true);
}

// Function to append the assistant's message to the chat container
function appendBotMessage(message) {
    let assistant = assistant_alias || 'Assistant'
    if (message.text !== undefined) {
        document.getElementById('chat-container').innerHTML += '<br>' + `<p><span class='assistant-chat'> ${assistant} :</span> ${message.text}</p>`;
        scrollToBottom();
    }
    if (message.notes !== undefined){
        document.getElementById('chat-container').innerHTML += '<br>' +
        `<p> <span class='report-section'> NOTES </span></p>`+
        `<p> ${message.notes.replace(/\n/g, '<br>')}</p>`; 
        scrollToBottom();
        showChoices();
    }
    if (message.lawyer_report !== undefined){
        document.getElementById('chat-container').innerHTML += '<br>' +
        `<p> <span class='report-section'> REPORT </span></p>` +
        `<p> ${message.lawyer_report.replace(/#/g, ' ').replace(/\n/g, '<br>')}</p>`;
        scrollToBottom(); 
        showChoices();
    }
    if (message.form_requirements !== undefined){
        document.getElementById('chat-container').innerHTML += '<br>' +
        `<p> <span class='report-section'> FORM REQUIREMENTS </span></p>`+
        `<p> ${message.form_requirements.replace(/#/g, ' ').replace(/\n/g, '<br>')}</p>`; 
        scrollToBottom();
        showChoices();
    }
    if (message.scenario_and_outcomes !== undefined){
        document.getElementById('chat-container').innerHTML += '<br>' +
        `<p> <span class='report-section'> SCENARIONS AND OUTCOMES </span></p>`+
        `<p> ${message.scenario_and_outcomes.replace(/#/g, ' ').replace(/\n/g, '<br>')}</p>`; 
        scrollToBottom();
        showChoices();
    }

    // Show upload form button at the mention of the word form or Form
    const wordsToCheck = ["form", "Form", "FORM"]
    const containsAnyWord = wordsToCheck.some(word=> message.text.includes(word));
    if (containsAnyWord){
        setTimeout(showUploadButton,3000);
    }

}

function showUploadButton(){
    document.getElementById('in-chat-wrapper').style.display = 'block';
    document.getElementById('in-chat-wrapper').classList.add('active');
    document.getElementById('in-chat-wrapper').style.opacity = '1';
}

function hidePreForm() {
    document.getElementById('pre-form').style.display = 'none';
}

function showForm() {
    document.getElementById('chat-form').style.opacity = 1;
    document.getElementById('chat-container').style.display = 'block';
}

function scrollToBottom() {
    let chatContainer = document.getElementById("chat-container");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showChoices() {
document.getElementById('results').style.display = 'block';
}

function hideChoices() {
    document.getElementById('results').style.display = 'none';
    document.getElementById('chat-container').innerHTML += '<br>' + `<p class='intro'><span > Passing your info to an attorney. Please wait...</p>`;
    scrollToBottom();
    assistant_alias = 'Your personel attorney';
}

function showSpinner() {
document.getElementById("spinner").style.display = "block";
}

function hideSpinner() {
document.getElementById("spinner").style.display = "none";
}
