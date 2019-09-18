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
