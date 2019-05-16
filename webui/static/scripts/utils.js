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