// Populates the operations select element with the available possible operations from the 'operations.json' file
function populateOperationsSelect() {

    let operationsSelect = $("[name='operations']")
    operationsSelect.empty()  // Remove the old contents

    // Append the default option to the select element
    let defaultOption = $('<option>')
    defaultOption.prop('value', '')
                 .html('Select the operation(s) to be performed...')
    operationsSelect.append(defaultOption)

    // Read the JSON file
    $.getJSON('static/config/operations.json')
    .done(function(data) {
        // Initialise the Semantic Dropdown and attach event handlers
        operationsSelect.dropdown({
            onAdd: function(addedValue) {
                // When selecting an item, the corresponding parameter configuration accordion is also added
                console.log('Added option having value:', addedValue)
                console.log('Added accordion having name equal to addedValue')
            },
            onRemove: function(removedValue) {
                // When removing a selected item, the corresponding parameter configuration accordion is also removed
                console.log('Removed option having value:', removedValue)
                console.log('Removed accordion having name equal to addedValue')
            }
        })

        // Append each operation name to the select element
        $.each(data, function(key, value) {
            let option = $('<option>')
            option.prop('value', key.toLowerCase())
                  .html(key)
            operationsSelect.append(option)
        })
    })
}