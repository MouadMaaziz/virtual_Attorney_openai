


const CHAT_CONTAINER = document.getElementById('chat-container');
const RESULTS_FORM = document.getElementById('results');
const USER_INPUT = document.getElementById('user-input');
let assistant_alias = '';


// Prevent the default behaviour of Clear_session form:
document.getElementById('clear-session').addEventListener('submit',function(event){
    
} )

// Attach an event listener to the form submission
document.getElementById("chat-form").addEventListener("submit", function (event) {
    event.preventDefault(); // prevent the form from submitting in the traditional way
    showSpinner();
    sendMessage();
});

document.getElementById("pre-form").addEventListener("submit", function (event) {
    event.preventDefault(); // prevent the form from submitting in the traditional way
    userName = document.getElementById("user-name").value;
    customerName = userName
    userCountry = document.getElementById("country").value;
    legalCase = document.getElementById("legal-case").value;
    
    if (legalCase == false){
        initialMessage = `Hello, my name is ${userName}, I am from ${userCountry}.`
    }
    else{
        initialMessage = `Hello, my name is ${userName}, I am from ${userCountry},
        and I am seeking legal advice about ${legalCase}`;
    }

    showSpinner();
    sendMessage(initialMessage,userName);
    hidePreForm();
    showForm();
});

RESULTS_FORM.addEventListener("submit", function (event) {
    event.preventDefault(); // prevent the form from submitting in the traditional way
    showSpinner();
    sendMessage();
});


// Function to send user input to the server
function sendMessage(preData = '', userName='') {
    
    // Get user input from the input field
    let userInput = USER_INPUT.value +
        preData;

    let results = event.submitter.value

    // Display the user's message in the chat container
    if (userInput !== '') {
        CHAT_CONTAINER.innerHTML += `<p><span class='client-chat'> Client</span>: ${userInput}</p>`;
        scrollToBottom(); // Scroll to the bottom of the chat container
    }
    // Clear the text input from the button 
    USER_INPUT.value = "";

    // hide choices if available
    hideChoices()

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
    makeAjaxRequest('/chat?userName=' + customerName +'&user-input=' + encodeURIComponent(userInput) + '&results=' + encodeURIComponent(results), true);
}


// Function to append the assistant's message to the chat container
function appendBotMessage(message) {
    let assistant = assistant_alias || 'Assistant'
    if (message.text !== undefined) {
        CHAT_CONTAINER.innerHTML += '<br>' + `<p><span class='assistant-chat'> ${assistant} :</span> ${message.text}</p>`;
        scrollToBottom();
        hideSpinner();
    }

    // If the response contains notes object. Equivalent of hitting DONE.
    if (message.notes !== undefined) {
        CHAT_CONTAINER.innerHTML += '<br>' +
            `<p> <span class='report-section'> NOTES </span></p>` +
            `<p> ${message.notes.replace(/\n/g, '<br>').replace(/#/g, ' ')}</p>`;
        scrollToBottom();
        showChoices();
        hideSpinner()
    }

    // If the response contains lawyer_report object
    if (message.lawyer_report !== undefined) {
        CHAT_CONTAINER.innerHTML += '<br>' +
            `<p> <span class='report-section'> REPORT </span></p>` +
            `<p> ${message.lawyer_report.replace(/#/g, ' ').replace(/\n/g, '<br>')}</p>`;
        scrollToBottom();
        showChoices();
        hideSpinner()
    }

    // If the response contains form_requirements object
    if (message.form_requirements !== undefined) {
        CHAT_CONTAINER.innerHTML += '<br>' +
            `<p> <span class='report-section'> FORM REQUIREMENTS </span></p>` +
            `<p> ${message.form_requirements.replace(/#/g, ' ').replace(/\n/g, '<br>')}</p>`;
        scrollToBottom();
        showChoices();
        hideSpinner()
    }

    // If the response contains scenario_and_outcomes object
    if (message.scenario_and_outcomes !== undefined) {
        CHAT_CONTAINER.innerHTML += '<br>' +
            `<p> <span class='report-section'> SCENARIONS AND OUTCOMES </span></p>` +
            `<p> ${message.scenario_and_outcomes.replace(/#/g, ' ').replace(/\n/g, '<br>')}</p>`;
        scrollToBottom();
        showChoices();
        hideSpinner()
    }


    // Show upload form button at the mention of the word form or Form
    const wordsToCheck = /\b(?:form|Form|FORM|forms|Document|document|Documents|documents)\b/;
    const containsAnyWord = wordsToCheck.test(message.text);
    if (containsAnyWord) {
        setTimeout(showUploadButton, 3000);
    }

}


function showUploadButton() {
    document.getElementById('in-chat-wrapper').style.display = 'block';
    document.getElementById('in-chat-wrapper').classList.add('active');
    document.getElementById('in-chat-wrapper').style.opacity = '1';
}

function hidePreForm() {
    document.getElementById('pre-form').style.display = 'none';
}

function showForm() {
    document.getElementById('chat-form').style.opacity = 1;
    CHAT_CONTAINER.style.display = 'block';
}

function scrollToBottom() {
    CHAT_CONTAINER.scrollTop = CHAT_CONTAINER.scrollHeight;
}

function showChoices() {
    RESULTS_FORM.style.display = 'block';
}

function hideChoices() {
    RESULTS_FORM.style.display = 'none';
    scrollToBottom();

}

function showSpinner() {
    document.getElementById("spinner").style.display = "block";
}

function hideSpinner() {
    document.getElementById("spinner").style.display = "none";
}


function getAttorney() {
    RESULTS_FORM.style.display = 'none';
    assistant_alias = 'Your personel attorney';
    CHAT_CONTAINER.innerHTML += '<br>' + `<p class='intro'><span > Passing your info to an attorney. Please wait...</p>`;

}