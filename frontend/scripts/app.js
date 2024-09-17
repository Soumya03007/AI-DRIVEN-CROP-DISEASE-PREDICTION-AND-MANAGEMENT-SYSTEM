// Handle image upload and analysis
document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const cropType = document.getElementById('cropType').value;
    const fileInput = document.getElementById('formFile');

    if (!cropType || fileInput.files.length === 0) {
        alert('Please select a crop type and upload an image.');
        return;
    }

    const formData = new FormData();
    formData.append('crop_type', cropType);
    formData.append('file', fileInput.files[0]);  // Ensure it's "file" to match backend

    try {
        const response = await fetch('http://localhost:8000/upload-image/', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();

            // Check if result contains both keys before displaying
            if (result.result && result.result.predicted_disease && result.result.solution) {
                document.getElementById('resultSection').style.display = 'block';
                document.getElementById('predictedDisease').innerText = result.result.predicted_disease;
                document.getElementById('predictedSolution').innerText = result.result.solution;
            } else {
                alert('Unexpected response format.');
                console.log(result);
            }
        } else {
            const errorText = await response.text(); // Show backend error message
            alert(`Failed to analyze image: ${errorText}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while uploading the image.');
    }
});


// Handle admin login and fetch users
document.getElementById('adminLoginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const email = document.getElementById('adminEmail').value;
    const password = document.getElementById('adminPassword').value;

    if (!email || !password) {
        alert('Please enter both email and password.');
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/admin/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
            const userList = await response.json();

            document.getElementById('userListSection').style.display = 'block';
            const userTableBody = document.querySelector('#userTable tbody');
            userTableBody.innerHTML = ''; // Clear previous content

            // Populate user list
            userList.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.email}</td>
                    <td>${new Date(user.registered_on).toLocaleString()}</td>
                `;
                userTableBody.appendChild(row);
            });
        } else {
            alert('Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while logging in.');
    }
});
