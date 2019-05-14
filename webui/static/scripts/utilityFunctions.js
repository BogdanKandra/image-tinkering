let operationsConfigurationObj = {}

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
                createAccordion(addedValue, data)
                operationsConfigurationObj[addedValue] = []
                console.log(operationsConfigurationObj)
            },
            onRemove: function(removedValue) {
                // When removing a selected item, the corresponding parameter configuration accordion is also removed
                removeAccordion(removedValue)
                delete operationsConfigurationObj[removedValue]
                console.log(operationsConfigurationObj)
            }
        })

        // Append each operation name to the select element
        $.each(data, function(key, value) {
            let option = $('<option>')
            option.prop('value', key)
                  .text(key)
            operationsSelect.append(option)
        })
    })
}

// Creates and appends a new entry to the parameter configuration accordion
function createAccordion(addedValue, data) {
	let parameterConfigurationAccordion = $('#paramCfgAccordion')

    // Create the title component
    let titleDiv = $('<div>').addClass('title')
    let titleIcon = $('<i>').addClass('dropdown icon')
    let titleValue = addedValue + ' Parameters'
    titleDiv.text(titleValue)
    titleDiv.prepend(titleIcon)

    // Create the content component
    let contentDiv = $('<div>').addClass('content')
    contentDiv.prop('id', addedValue)
    let menu = $('<div>').addClass('ui vertical menu')

    let paramsList = data[addedValue]['parameters']
    for (const parameter of paramsList) {
        menu.append(createMenuEntry(parameter))
    }

    contentDiv.append(menu)
    parameterConfigurationAccordion.append(titleDiv).append(contentDiv)
}

// Remove an entry from the parameter configuration accordion
function removeAccordion(removedValue) {

    $('.title').filter('div:contains(' + removedValue + ')').remove()
    $('[id="' + removedValue + '"]').remove()
}

// Creates and returns a Semantic UI dropdown which must be an item of a menu
function createMenuEntry(parameterObject) {

    let dropdownDiv = $('<div>').addClass('ui left pointing scrolling dropdown link item')
    dropdownDiv.attr('data-content', parameterObject['description']) // Add the description of the parameter as a popup
    let dropdownIcon = $('<i>').addClass('dropdown icon')
    let dropdownText = parameterObject['name'].charAt(0).toUpperCase() + parameterObject['name'].slice(1)
    let dropdownMenu = $('<div>').addClass('menu')

    let paramType = parameterObject['type']
    let paramDefault = (parameterObject.hasOwnProperty('default')) ? parameterObject['default'] : undefined

    if (paramType == 'range') {
        for (let i = parameterObject['minimum']; i <= parameterObject['maximum']; i++) {
            let item = $('<div>').addClass('item')
            item.text(i)
            if (i == paramDefault) {
                item.addClass('active selected')
            }
            dropdownMenu.append(item)
        }
    } else if (paramType == 'lookup') {
        for (const value of parameterObject['values']) {
            let item = $('<div>').addClass('item')
            item.text(value)
            if (value == paramDefault) {
                item.addClass('active selected')
            }
            dropdownMenu.append(item)
        }
    }

    dropdownDiv.append(dropdownIcon).append(dropdownText).append(dropdownMenu)
    // Initialise the dropdown and specify the trigger for the animation as 'hover'
    dropdownDiv.dropdown({
        on: 'hover',
        onChange: function(value) {
            // When selecting an item...
            console.log(value)
        }
    })
    dropdownDiv.popup()

    return dropdownDiv
}