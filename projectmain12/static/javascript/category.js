
function sendRequest2(data, successCallback, errorCallback) {
    const url = `/DeleteCategoryItem/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    };

    fetch(url, options)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok.');
            }
        })
        .then(data => {
            successCallback(data); // Call the success callback with the response data
        })
        .catch(error => {
            errorCallback(error); // Call the error callback if there is an issue
        });
}


function Categorysdata() {
    const data = {
        'mode': '3' // Example additional parameter
    };

    sendRequest2(
        data,
        function (data) { // Success callback
            const tableBody = document.querySelector('#Categorys-list tbody'); // Target table body
            tableBody.innerHTML = ''; // Clear the table

            // Iterate through the categories data and populate the table
            data.categories1.forEach((category, index) => {
                const newRow = document.createElement('tr');
                newRow.id = `categoryRow_${category.id}`;
                newRow.innerHTML = `
                      <tr>
                          <td>${index + 1}</td> <!-- Auto-increment index -->
                          <td value="${category.id}">${category.name}</td>
                          <td>
                              <button id="deleteButton_${category.id}" onclick="DeleteCategoryItem1(${category.id})">Delete</button>
                          </td>
                      </tr>
                  `;
                tableBody.appendChild(newRow);
            });
        },
        function (error) { // Error callback
            console.error('Error fetching category data:', error);
        }
    );
}




function Add_category() {
    const category_name = document.getElementById('category-name').value;



    const data = {
        'category_name': category_name,

        'mode': "2"
    };

    sendRequest2(
        data,           // Data to send
        function (data) {
            // Success callback
            showAlert("category new item added successfully", 'alert-success'); // Or display a success notification
            Categorysdata();

            // Refresh product list
        },
        function (error) { // Error callback
            showAlert("category new item not added", 'alert-error');
            console.error('Error adding item:', error);
        }
    );
}

    function DeleteCategoryItem1(category_id) {
        const data = {
            'category_id': category_id,
            'mode': "4"
        };
        // Confirm deletion
        if (confirm('Are you sure you want to delete this item?')) {
            sendRequest2(
                data,
                function (response) {
                    // Success callback: Remove the row from the table
                    showAlert("categoryItem deleted successfully", 'alert-success');
                    const row = document.getElementById('categoryRow_' + category_id);
                    row.parentNode.removeChild(row);
                },
                function (error) {
                    // Error callback
                    showAlert("categoryItem not deleted", 'alert-error');
                }
            );
        }
    }
