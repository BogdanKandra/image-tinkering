// Attach handlers on document ready
$(document).ready(function() {
	console.log('In script')

	let imgElement = $('#imagesrc')
	let fileInput = $('#fileInput')
	let uploadInput = $('#uploadInput')

	$(fileInput).change(function(event) {
		console.log('File was loaded')
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
	console.log('>>>', files)
	let imageData = new FormData();

	for (let i = 0; i < files.length; i++)
		imageData.append('files-' + (i + 1), files[i]);

	for (let p of imageData) {
	  console.log('>>>>>', p);
	}
	
	$.ajax({
		url: '/uploads',
		method: 'POST',
		data: imageData,
		processData: false,
		contentType: false,
		success: function(data) {
			console.log('Succeeded')
			console.log('>>> Data', data)
		},
		error: function() {
			console.log('Errored')
		}
	})
}