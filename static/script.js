//for the forget password thing
document.getElementById('resetPasswordForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const email = document.getElementById('email').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const message = document.getElementById('message');

    // Basic validation
    if (newPassword !== confirmPassword) {
        message.textContent = "Passwords do not match.";
        message.className = "text-danger"; // Change text color to red
        return;
    }


     fetch('/api/reset-password', {
         method: 'POST',
         headers: {
             'Content-Type': 'application/json'
         },
         body: JSON.stringify({ email, newPassword })
     })
     .then(response => {
         if (response.ok) {
             message.textContent = "Password reset successful!";
             message.className = "text-success"; // Change text color to green
         } else {
             message.textContent = "Failed to reset password.";
             message.className = "text-danger"; // Change text color to red
         }
     })
     .catch(error => {
         message.textContent = "An error occurred.";
         message.className = "text-danger"; // Change text color to red
     });

    message.textContent = "Password reset functionality is not yet implemented.";
    message.className = "text-info"; // Change text color to blue
});

