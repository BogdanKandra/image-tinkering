// Attach handlers on document ready
$(document).ready(function() {

	let imgElement = $('#imagesrc')
	let fileInput = $('#fileInput')
	let uploadInput = $('#uploadInput')

	$(fileInput).change(function(event) {
		if (event.target.files.length != 0) {
			$(imgElement).attr('src', URL.createObjectURL(event.target.files[0]))
			$(uploadInput).attr('disabled', false)
		} else {
			$(uploadInput).attr('disabled', true)
		}
	})
})

// Makes a POST request, uploading the selected files to the server
// Upon completion of the upload, the server sends the URLs of the files and the function displays
// those files
function uploadFiles() {
	
	const files = $('#fileInput').prop('files')
	let imageData = new FormData()

	for (let i = 0; i < files.length; i++)
		imageData.append('files-' + (i + 1), files[i])

	$.ajax({
		url: '/uploads',
		method: 'POST',
		data: imageData,
		processData: false,
		contentType: false,
		success: function(data) {
			console.log('Succeeded')
			new Noty({
				text: 'Success!',
				type: 'success',
				layout: 'top',
				theme: 'relax',
				timeout: 5000
			}).show()
			console.log('>>> Data', data)
		},
		error: function() {
			new Noty({
				text: 'File upload failed!',
				type: 'error',
				layout: 'top',
				theme: 'relax',
				timeout: 5000
			})
			console.log('Errored')
		}
	})
}