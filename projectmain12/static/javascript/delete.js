function deleteItem(productId) {
    const data = {
        'product_id': productId,
        'mode': "4"
    };

    // Confirm deletion
    if (confirm('Are you sure you want to delete this item?')) {
        sendRequest(
            data,
            function (response) {
                // Success callback: Remove the row from the table
                showAlert("Item deleted successfully", 'alert-success');
                fetchProductUpdates();
            },
            function (error) {
                // Error callback
                console.error('There was a problem with the fetch operation:', error);
            }
        );
    }
}