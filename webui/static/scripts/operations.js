"use strict";

let operationConfigurations = [] // List of objects each describing the configuration of an operation
let dataToProcess = {}           // Object to be sent to AJAX call when the user clicks the PROCESS button
let configuredImages = 0         // Counter for keeping track of number of images configured
let extraInputFiles = {}         // Object containing all extra input images (as File objects)
let extraInputsNames = []        // List containing the names of the extra input parameters needed for certain operations

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
            deleteExtraInputsAjax(name)
            displayConfigurationModal(name)
        })
		configureDiv.append(configureButton)

		// Build the containing div
		let container = $('<div>').addClass('hoverable_container')
		container.append(image).append(configureDiv)

		filesAndOperationsContainer.append(container)
	}
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
                opConfig['type'] = data[addedValue]['type']
                opConfig['params'] = {}
                if (opConfig['type'].startsWith('many-to-')) {
                    opConfig['extras'] = data[addedValue]['extraInputsNames']
                }
                operationConfigurations.push(opConfig)

                // Open a modal asking the user to select the extra inputs, if the operation type is 'many-to-'
                if (opConfig['type'].startsWith('many-to-')) {
                    displayExtraInputsModal(data, addedValue)
                }

                createAccordion(addedValue, data) // The corresponding parameter configuration accordion is also added
                updateOperationsSelect(data) // Update the contents of the configurations dropdown, if necessary
                checkAcceptCondition() // Reevaluate the state of the ACCEPT button
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

                // If a many-to- operation has been removed, cancel the Files selected just before
                if (data[removedValue]['type'].startsWith('many-to-')) {
                    extraInputFiles = {}
                }
                
                updateOperationsSelect(data) // Update the contents of the configurations dropdown, if necessary
                checkAcceptCondition() // Reevaluate the state of the ACCEPT button
            }
        })

        // Append each operation name to the select element
        $.each(data, function(key, _value) {
            let option = $('<option>')
            option.prop('value', key)
                  .text(key)
            operationsSelect.append(option)
        })
    })
}

// Populates the container within the extra inputs modal
function populateExtraInputsModal(extraInputsNames) {

    let extraParamsContainer = $('#extraParams').empty()
    let extraInputsSelected = {}
    for (let i = 0; i < extraInputsNames.length; i++) {
        extraInputsSelected[extraInputsNames[i]] = false
    }
    
    for (const name of extraInputsNames) {
        let extraParamConfig = $('<div>').addClass('extraParamConfig')

        // Build a div containing parameter information
        let paramNameSpan = $('<span>').append($('<strong>').text(name + ' Image'))
        let paramInfoContainer = $('<div>').addClass('extraInputsDetails')
                                           .append(paramNameSpan)

        // Build a div containing a placeholder for the image preview
        let imagePreviewContainer = $('<div>').addClass('ui placeholder extraInputImage')
                                              .append($('<div>').addClass('rectangular image'))

        // Build the file input
        let fileIcon = $('<i>').addClass('file image icon')
        let fileLabel = $('<label>').prop('for', name)
                                    .addClass('ui labeled icon primary button')
                                    .text('SELECT')
        let fileInput = $('<input>').prop('type', 'file')
                                    .prop('id', name)
                                    .prop('accept', 'image/*')
                                    .prop('style', 'display:none')
                                    .addClass('primary small')
                                    .change(function(event) {

                                        // Manage the number of selected extra images and
                                        // Display the selected image in place of the placeholder (or the placeholder, if the user did not select any image)
                                        $('#' + $(this).prop('id') + '_extra').replaceWith(imagePreviewContainer)
                                        let filesCount = event.target.files.length
                                        
                                        if (filesCount == 0) {
                                            extraInputsSelected[$(this).prop('id')] = false
                                            extraInputFiles[$(this).prop('id')] = undefined
                                        } else {
                                            extraInputsSelected[$(this).prop('id')] = true
                                            extraInputFiles[$(this).prop('id')] = event.target.files[0]

                                            let imageElement = $('<img>')
                                            imageElement.prop('src', URL.createObjectURL(event.target.files[0]))
                                            imageElement.prop('alt', 'Image Preview not Available')
                                            imageElement.prop('height', '200')
                            
                                            $(imagePreviewContainer).replaceWith($('<div>').prop('id', $(this).prop('id') + '_extra')
                                                                                           .addClass('extraInputImage')
                                                                                           .append(imageElement))
                                        }

                                        checkExtraAcceptCondition(extraInputsSelected)
                                    })
        fileLabel.append(fileIcon)
        let fileContainer = $('<div>').append(fileLabel).append(fileInput)

        extraParamConfig.append(paramInfoContainer).append(imagePreviewContainer).append(fileContainer)
        extraParamsContainer.append(extraParamConfig)
    }
}

// Updates the list of available operations, based on the operations selected by the user
function updateOperationsSelect(data) {

    let operationsSelectItems = $('.description').find('.ui.dropdown.selection').find('.menu.transition').find('.item')

    if (operationConfigurations.length != 0) {
        let selectedOperationsTypes = operationConfigurations.map(x => x['type'])

        if (selectedOperationsTypes.includes('one-to-many') || selectedOperationsTypes.includes('many-to-many')) {
            // If the user has selected a -to-many operation, disable all other available operations and notify user
            operationsSelectItems.addClass('disabled')
            let notificationText = 'Operations which yield several result images cannot be chained by other operations. Remove it to be able to chain other operations'
            displayNotification({'text': notificationText, 'type': 'info'})
        } else {
            // If the user has selected a -to-one operation, disable all non one-to- operations
            let allOperationsNames = $.map(operationsSelectItems, (element, _index) => $(element).text())

            $.each(operationsSelectItems, function(index, value) {
                if (!data[allOperationsNames[index]]['type'].includes('one-to-') && !$(value).hasClass('filtered')) {
                    $(value).addClass('disabled')
                } else {
                    $(value).removeClass('disabled')
                }
            })
        }
    } else {
        // If the user has not selected any operations, restore all operations to original state
        operationsSelectItems.removeClass('disabled')
    }
}

// Initialises and opens the operation configuration modal
function displayConfigurationModal(imageName) {

	populateOperationsSelect(imageName)
	let operationsSelect = $("[name='operations']")
	let parameterConfigurationAccordion = $('#paramCfgAccordion')
	parameterConfigurationAccordion.accordion()

	$('#configurationModal').modal({
                        allowMultiple: true,
                        onHide: function() {    // Called whenever modal is closed
                            operationsSelect.dropdown('clear')
                            parameterConfigurationAccordion.empty()
                            extraInputFiles = {} // Reset the File dictionary
                        },
                        onApprove: function() { // ACCEPT button
                            // Only count this image as configured if it has not yet been configured before
                            if (!dataToProcess.hasOwnProperty(imageName)) {
                                configuredImages++
                            }
                            
                            dataToProcess[imageName] = JSON.parse(JSON.stringify(operationConfigurations)) // Add the configuration of this image to the call data

                            // If extra input files are needed, make a file upload
                            if (extraInputFiles != {}) {
                                uploadExtraInputs(imageName)
                            }

                            checkProcessCondition() // Reevaluate the state of the PROCESS button
                        },
                        onDeny: function() {    // CANCEL button

                        }
                    }).modal('show')
}

// Initialises and opens the extra inputs selection modal
function displayExtraInputsModal(data, addedValue) {

    extraInputsNames = data[addedValue]['extraInputsNames']
    let acceptedExtraInputsModal = false
    populateExtraInputsModal(extraInputsNames)

	$('#extraInputsModal').modal({
                        allowMultiple: true,
                        onHide: function() {    // Called whenever modal is closed
                            if (!acceptedExtraInputsModal) {
                                // Remove the operation which triggered this modal from the operation chain, since the user canceled extra inputs selection
                                let operationsSelect = $("[name='operations']")
                                operationsSelect.dropdown('remove selected', addedValue)
                                
                                displayNotification({'text': 'The selected operation has been canceled, due to not selecting the necessary extra inputs', 'type': 'info'})
                            }

                            $('#extraInputsActions div.ui.approve.primary.button').addClass('disabled')
                            acceptedExtraInputsModal = false
                        },
                        onApprove: function() { // ACCEPT button
                            acceptedExtraInputsModal = true
                        },
                        onDeny: function() {    // CANCEL button
                            acceptedExtraInputsModal = false
                        }
                    }).modal('show')
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
                                .prop('data-tooltip', parameterObject['description']) // Add the description of the parameter as a popup
                                .prop('id', parameterObject['name'] + '_parameter')
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
        let step = (parameterObject.hasOwnProperty('step')) ? parameterObject['step'] : 1

        for (let i = parameterObject['minimum']; i <= parameterObject['maximum']; i += step) {
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
        onChange: function(value, _text) {
            // When selecting an item, update the parameter value in the list of configurations as well
            for (let i = 0; i < operationConfigurations.length; i++) {
                if (operationConfigurations[i]['function'] == functionName) {
                    // The value will be converted to number if it is numeric
                    operationConfigurations[i]['params'][dropdownText.toLowerCase()] = Number.isNaN(Number(value)) ? value : Number(value)
                }
            }

            // Check whether the presence of another parameter depends on this parameters' value
            if (parameterObject.hasOwnProperty('presenceDependency')) {
                let presenceDependency = parameterObject['presenceDependency']
                let presenceConditionRegex = /([^a-zA-Z]+)([a-zA-Z]+)/
                let matches = presenceConditionRegex.exec(parameterObject['presenceCondition'])
                let execCond = '\"' + value + '\"' + matches[1] + '\"' + matches[2] + '\"'
                if (eval(execCond)) {
                    // The presence condition has been met, display the dependant parameter
                    let parameterSelector = '#' + presenceDependency + '_parameter'
                    $(parameterSelector).css('display', 'block')
                } else {
                    // The presence condition has not been met, hide the dependant parameter
                    let parameterSelector = '#' + presenceDependency + '_parameter'
                    $(parameterSelector).css('display', 'none')
                }
            }
        },
        onHide: function() {
            checkAcceptCondition() // Reevaluate the state of the ACCEPT button
        }
    })
    dropdownDiv.popup({
        on: 'hover'
    })

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
        $.each(parameterGroups, function(_index) {
            let dropdowns = $(this).children()
            let dropdownsOk = true
            
            // For each dropdown, check if a value was set; if not, break (return false)
            $.each(dropdowns, function(_index) {
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

// Checks whether the necessary number of extra input images have been selected or not and changes the state of the ACCEPT button accordingly
function checkExtraAcceptCondition(extraInputsSelected) {

    let enabling = true
    let acceptButton = $('#extraInputsActions div.ui.approve.primary.button')

    for (let paramName in extraInputsSelected) {
        if (extraInputsSelected.hasOwnProperty(paramName)) {
            if (extraInputsSelected[paramName] == false) {
                enabling = false
                break
            }
        }
    }

    if (enabling) {
        acceptButton.removeClass('disabled')
    } else {
        acceptButton.addClass('disabled')
    }

    return enabling
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

            // Perform AJAX calls which delete the uploaded files and the pickle files, since the processing has been completed
            deleteUploadsAjax(dataToProcess)
            deletePicklesAjax(dataToProcess)

            // Direct the user to the Results Step
			$('#operationSelectionContent').css('display', 'none')
			$('#resultsContent').css('display', 'block')
			$('#steps').children('.step').eq(1).removeClass('active')
			$('#steps').children('.step').eq(1).addClass('completed')
            $('#steps').children('.step').eq(2).addClass('active')
            
            // Populate the container holding resulting images
            populateResultsContainer(data)
            
            // Detach any existing click events and attach another one which deletes everything
            $('#homeButton').off('click')
                            .click(function() {
                                openResetDialog(data, 'TEMPDATA')
                            })
        },
        error: function(_request, _status, _error) {
            displayNotification({'text': 'An error occured during processing', 'type': 'error', 'theme': 'sunset'})
            processButton.removeClass('disabled')
        }
    })
}

// Prepares the form data and performs the AJAX call which uploads the extra input images to the server
function uploadExtraInputs(imageName) {

    // Build the request data
    let imageData = new FormData()
    
    for (let i = 0; i < extraInputsNames.length; i++) {
        imageData.append('extrafiles-' + (i + 1), extraInputFiles[extraInputsNames[i]])
    }

    imageData.append('image-name', imageName)
    imageData.append('params-names', extraInputsNames)

	$.ajax({
		url: '/uploads/extrainputs',
		method: 'POST',
		data: imageData,
		processData: false,
		contentType: false,
		success: function(_data) {},
		error: function(_request, _status, _error) {
			displayNotification({'text': 'Extra input files upload failed!', 'type': 'error'})			
			$('#uploadButton').removeClass('disabled')
		}
	})
}
