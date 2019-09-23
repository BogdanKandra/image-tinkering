// Displays a simple notification having the properties specified in the object parameter
function displayNotification(parameters) {
    let text = parameters.hasOwnProperty('text') ? parameters['text'] : 'Default Notification Text'
    let type = parameters.hasOwnProperty('type') ? parameters['type'] : 'success'
    let layout = parameters.hasOwnProperty('layout') ? parameters['layout'] : 'top'
    let theme = parameters.hasOwnProperty('theme') ? parameters['theme'] : 'relax'
    let timeout = parameters.hasOwnProperty('timeout') ? parameters['timeout'] : 5000

    new Noty({
        text: text,
        type: type,
        layout: layout,
        theme: theme,
        timeout: timeout
    }).show()
}

// Switches the application mode between 'Image' and 'Video'
// TODO - Implement Video mode
function changeMode() {

	let visibleContent = $('#switchMode').find('.visible').first()
	let hiddenContentIcon = $('#switchMode').find('.hidden').first().find('.icon').first()

	if (visibleContent.html().includes('VIDEO')) {
		visibleContent.html('SWITCH TO IMAGE MODE')
	} else {
		visibleContent.html('SWITCH TO VIDEO MODE')
	}

	hiddenContentIcon.toggleClass('image')
	hiddenContentIcon.toggleClass('video')
}

// Performs an AJAX call which deletes the resulting images (processed images and pickles) for each of the given list of processed files
function deleteTempdataAjax(fileNamesList) {

	$.ajax({
        url: '/cleanup/tempdata',
        method: 'POST',
        data: JSON.stringify({'filenames': fileNamesList}),
        contentType: 'application/json',
        success: function(_data) {},
        error: function(_request, _status, _error) {
			console.log('>>> An error occured during deletion of processed files and pickles')
        }
    })
}

// Performs an AJAX call which deletes the pickle files which resulted after the initialisation process, for each of the given list of processed files
function deletePicklesAjax(fileNamesList) {

    $.ajax({
        url: '/cleanup/pickles',
        method: 'POST',
        data: JSON.stringify({'filenames': fileNamesList}),
        contentType: 'application/json',
        success: function(_data) {},
        error: function(_request, _status, _error) {
            console.log('>>> An error occured during deletion of pickles')
        }
    })
}

// Performs an AJAX call which deletes uploaded images (input image and extra input images, if any), for each of the given keys in the data to process or list of filenames
function deleteUploadsAjax(dataToProcessObject) {

	$.ajax({
		url: '/cleanup/uploads',
		method: 'POST',
		data: JSON.stringify({'data': dataToProcessObject}),
		contentType: 'application/json',
		success: function(_data) {},
		error: function(_request, _status, _error) {
			console.log('>>> An error occured during deletion of uploads')
		}
	})
}

// Performs an AJAX call which deletes any existent extra input images associated to the image to be configured
function deleteExtraInputsAjax(imageName) {

    $.ajax({
        url: '/cleanup/extras',
        method: 'POST',
        data: JSON.stringify({'name': imageName}),
        contentType: 'application/json',
        success: function(_data) {},
        error: function(_request, _status, _error) {
            console.log('>>> An error occured during deletion of extra input images')
        }
    })
}
