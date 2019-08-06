"use strict";

let operationConfigurations = [] // List of objects each describing the configuration of an operation
let dataToProcess = {}           // Object to be sent to AJAX call when the user clicks the PROCESS button
let configuredImages = 0         // Counter for keeping track of number of images configured

// For each uploaded file, creates a container holding the uploaded file and a revealing "CONFIGURE" button over the file
function populateFilesAndOperationsContainer(data) {

	let imageNames = data['image']
	let filesAndOperationsContainer = $('#filesAndOperationsContainer')

	for (const name of imageNames) {

		// Build the img element to be displayed
		let path = '../static/uploads/images/' + name
		let image = $('<img>').addClass('hoverable_image')
		image.prop('src', path)
		image.prop('alt', 'Image Preview not Available')
		image.prop('height', '200')

		// Build the div holding the revealing "CONFIGURE" button
		let configureDiv = $('<div>').addClass('configure_container')
		let configureButton = $('<button>').addClass('ui primary button')
		configureButton.html('CONFIGURE')
		configureButton.click(function() {
            displayConfigurationModal(name)
        })
		configureDiv.append(configureButton)

		// Build the containing div
		let container = $('<div>').addClass('hoverable_container')
		container.append(image).append(configureDiv)

		filesAndOperationsContainer.append(container)
	}
}

// Initialises and opens the operation configuration modal
function displayConfigurationModal(imageName) {

	populateOperationsSelect()
	let operationsSelect = $("[name='operations']")
	let parameterConfigurationAccordion = $('#paramCfgAccordion')
	parameterConfigurationAccordion.accordion()

	$('#configurationModal').modal({
								onHide: function() {    // Called whenever modal is closed
									operationsSelect.dropdown('clear')
                                    parameterConfigurationAccordion.empty()
								},
                                onApprove: function() { // ACCEPT button
                                    // Only count this image as configured if it has not yet been configured before
                                    if (!dataToProcess.hasOwnProperty(imageName)) {
                                        configuredImages++
                                    }

                                    // Add the configuration of this image to the call data
                                    dataToProcess[imageName] = JSON.parse(JSON.stringify(operationConfigurations))

                                    // Reevaluate the state of the PROCESS button
                                    checkProcessCondition()
								},
								onDeny: function() {    // CANCEL button

								}
							}).modal('show')
}

// Populates the operations select element within the configuration modal by parsing the 'operations.json' file
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
                // When selecting an item, a new operation configuration is stored in the list of configurations
                let opConfig = {}
                opConfig['function'] = data[addedValue]['function']
                opConfig['params'] = {}
                operationConfigurations.push(opConfig)

                // And the corresponding parameter configuration accordion is also added
                createAccordion(addedValue, data)

                // Reevaluate the state of the ACCEPT button
                checkAcceptCondition()
            },
            onRemove: function(removedValue) {
                // When removing a selected item, the corresponding parameter configuration accordion and operation configuration entry are also removed
                removeAccordion(removedValue)

                // Remove the corresponding entry from the list of configurations
                for (let i = 0; i < operationConfigurations.length; i++) {
                    if (operationConfigurations[i]['function'] == data[removedValue]['function']) {
                        operationConfigurations.splice(i, 1)
                        break
                    }
                }

                // Reevaluate the state of the ACCEPT button
                checkAcceptCondition()
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

    // Add the parameter items to the menu
    let paramsList = data[addedValue]['parameters']
    for (const parameter of paramsList) {
        menu.append(createMenuEntry(parameter, data[addedValue]['function']))
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
function createMenuEntry(parameterObject, functionName) {

    let dropdownDiv = $('<div>').addClass('ui left pointing scrolling dropdown link item')
    dropdownDiv.attr('data-content', parameterObject['description']) // Add the description of the parameter as a popup
    let dropdownIcon = $('<i>').addClass('dropdown icon')
    let dropdownText = parameterObject['name'].charAt(0).toUpperCase() + parameterObject['name'].slice(1)
    let dropdownMenu = $('<div>').addClass('menu')

    let paramType = parameterObject['type']
    let paramDefault = (parameterObject.hasOwnProperty('default')) ? parameterObject['default'] : undefined

    // Store the default parameter value in the list of configurations as well
    for (let j = 0; j < operationConfigurations.length; j++) {
        if (operationConfigurations[j]['function'] == functionName && paramDefault != undefined) {
            operationConfigurations[j]['params'][dropdownText.toLowerCase()] = paramDefault
        }
    }

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
        onChange: function(value, text) {
            // When selecting an item, update the parameter value in the list of configurations as well
            for (let i = 0; i < operationConfigurations.length; i++) {
                if (operationConfigurations[i]['function'] == functionName) {
                    // The value will be converted to number if it is numeric
                    operationConfigurations[i]['params'][dropdownText.toLowerCase()] = Number.isNaN(Number(value)) ? value : Number(value)
                }
            }
        },
        onHide: function() {
            checkAcceptCondition() // Reevaluate the state of the ACCEPT button
        }
    })
    dropdownDiv.popup()

    return dropdownDiv
}

// Checks whether the currently selected operations are correctly configured and decides whether the ACCEPT button must be enabled or not
// If no operations have been selected or there are params which do not have a default value and have not been set, disable the ACCEPT button
// Else, enable it
function checkAcceptCondition() {

    // Locate and disable the button; only enable it if conditions are met
    let acceptButton = $('#configurationActions div.ui.approve.primary.button')
    if (!acceptButton.hasClass('disabled')) {
        acceptButton.addClass('disabled')
    }

    // The button remains disabled if no operation has been selected
    let operationsCount = operationConfigurations.length
    if (operationsCount != 0) {
        let parameterGroups = $('#paramCfgAccordion .ui.vertical.menu')
        let parametersOk = true
        
        // For each group of parameters, check the values of the parameters
        $.each(parameterGroups, function(index) {
            let dropdowns = $(this).children()
            let dropdownsOk = true
            
            // For each dropdown, check if a value was set; if not, break (return false)
            $.each(dropdowns, function(index) {
                let options = $(this).find('.menu').children()
                let parameterSet = false

                $.each(options, function() {
                    if (this.classList.contains('selected')) {
                        parameterSet = true
                        return false
                    }
                })

                if (!parameterSet) {
                    dropdownsOk = false
                    return false
                }
            })

            if (!dropdownsOk) {
                parametersOk = false
                return false
            }
        })

        if (parametersOk) {
            acceptButton.removeClass('disabled')
        }
    }
}

// Checks the number of input images which have been configured. If at least one, the PROCESS button is enabled; else, it stays disabled
function checkProcessCondition() {

    let processButton = $('#configurationButtons .ui.button')
    processButton.addClass('disabled')

    if (configuredImages > 0) {
        processButton.removeClass('disabled')
    }
}

// Checks how many files have been configured from the total uploaded and starts the processing if the user agrees
function processFiles() {

    let processButton = $('#configurationButtons .ui.button')
    processButton.addClass('disabled')
    let totalImages = $('#filesAndOperationsContainer').children().length

    if (configuredImages != totalImages) {
        let notificationText = 'You have configured ' + configuredImages + ' out of ' + totalImages + 
                               ' images. Unconfigured images will not be processed in any way. Proceed?'
        
        new Noty({
            text: notificationText,
            layout: 'top',
            theme: 'sunset',
            closeWith: [],
            buttons: [
                Noty.button('YES', 'ui button positive tiny', function($noty) {
                    // If clicked 'YES', launch the AJAX call
                    $noty.close()
                    processFilesAjax()
                }),
                Noty.button('NO', 'ui button negative tiny', function($noty) {
                    // If clicked 'NO', do nothing and display a notification
                    $noty.close()
                    processButton.removeClass('disabled')
                    displayNotification({'text': 'File Processing was Canceled', 'type': 'info', 'theme': 'sunset'})
                })
            ]
        }).show()
    } else {
        processFilesAjax()
    }
}

// Performs the AJAX call which processes the files and the directs the user to the results step
function processFilesAjax() {

    let processButton = $('#configurationButtons .ui.button')

    $.ajax({
        url: '/process/',
        method: 'POST',
        data: JSON.stringify({'data': dataToProcess}),
        contentType: 'application/json',
        success: function(data) {
            processButton.removeClass('disabled')
            displayNotification({'text': 'Processing Complete!', 'type': 'success', 'theme': 'sunset'})

            // Direct the user to the Results Step
			$('#operationSelectionContent').css('display', 'none')
			$('#resultsContent').css('display', 'block')
			$('#steps').children('.step').eq(1).removeClass('active')
			$('#steps').children('.step').eq(1).addClass('completed')
            $('#steps').children('.step').eq(2).addClass('active')
            
            // Populate the container holding resulting images
			populateResultsContainer(data)
        },
        error: function(request, status, error) {
            displayNotification({'text': 'An error occured during processing', 'type': 'error', 'theme': 'sunset'})
            processButton.removeClass('disabled')
        }
    })
}