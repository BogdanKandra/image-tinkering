"use strict";

let attachedResetButtonClick = false

// For each result file, creates a container holding the file and a revealing "SAVE" button over the file
function populateResultsContainer(data) {

	let resultsContainer = $('#resultsContainer')

	for (const name of data) {

		// Build the img element to be displayed
		let path = '../static/tempdata/' + name
		let image = $('<img>').addClass('hoverable_image')
		image.prop('src', path)
		image.prop('alt', 'Image Preview not Available')
		image.prop('height', '200')

		// Build the div holding the revealing "SAVE" button
		let saveDiv = $('<div>').addClass('configure_container')
		let saveButton = $('<button>').addClass('ui primary button')
		saveButton.html('SAVE')
		saveButton.click(function() {
            saveFile(path)
        })
		saveDiv.append(saveButton)

		// Build the containing div
		let container = $('<div>').addClass('hoverable_container')
		container.append(image).append(saveDiv)

		resultsContainer.append(container)

		// Bind click event for the "DISCARD" button
		if (!attachedResetButtonClick) {
			$('#resultsButtons .ui.button').click(function() {
				openResetDialog(data)
			})
			attachedResetButtonClick = true
		}
	}
}

// Downloads the file to the 'downloads' directory of the user
function saveFile(path) {

    let download_name = path.substring(path.lastIndexOf("/") + 1).split("_")[0] + "_processed"
    let link = $('<a>')
    link.prop('href', path)
    link.prop('download', download_name)
    link[0].click()
}

// Opens up a dialog asking the user whether they are sure they want to reset
function openResetDialog(data) {
	
	let resetButton = $('#resultsButtons .ui.button')
	resetButton.addClass('disabled')

	let notificationText = 'Doing this will send you back to the File Selection Step. Are you sure you want to proceed?'

	new Noty({
		text: notificationText,
		layout: 'top',
		theme: 'sunset',
		closeWith: [],
		buttons: [
			Noty.button('YES', 'ui button positive tiny', function($noty) {
				resetButton.removeClass('disabled')
				$noty.close()
				resetProgress()         // Cancel all selections, starting from file selection
				deleteResultsAjax(data)	// Delete the result files from the server
			}),
			Noty.button('NO', 'ui button negative tiny', function($noty) {
				resetButton.removeClass('disabled')
				$noty.close()
			})
		]
	}).show()
}

// Resets the selections made by the user so far, sending them back to the File Selection Step
function resetProgress() {

	// Direct the user back to the File Selection Step
	$('#resultsContent').css('display', 'none')
	$('#fileSelectionContent').css('display', 'block')
	let steps = $('#steps').children('.step')
	steps.first().addClass('active')
	steps.first().removeClass('completed')
	steps.eq(1).removeClass('completed')
	steps.eq(2).removeClass('active')
	steps.eq(2).removeClass('completed')

	// Remove old content from each screen
	$('#filesCount').html('No Files loaded yet')
	$('#fileNames').empty()
	$('#filesContainer').empty()
	$('#filesAndOperationsContainer').empty()
	$('#configurationButtons .ui.button').addClass('disabled')
	$('#resultsContainer').empty()
	$('#steps').css('position', 'fixed')
	operationConfigurations = []
	dataToProcess = {}
	configuredImages = 0
}

// Performs an AJAX call which deletes all input and result files
function deleteResultsAjax(fileNamesList) {

	$.ajax({
        url: '/cleanup/',
        method: 'POST',
        data: JSON.stringify({'filenames': fileNamesList}),
        contentType: 'application/json',
        success: function(data) {
			console.log(data)
        },
        error: function(request, status, error) {
			console.log('An error occured during deletion of files')
        }
    })
}