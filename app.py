from flask import Flask, request, jsonify
from azure.storage.blob import BlockBlobService, ContentSettings
import subprocess
import os
import ffmpeg

account_name = "moviestarstorage"
account_key =  "7zXsCWqv5Du6vnO7gf7qGVNDQZoU8HOi7kNeI20q/x9gyAHn3in6lUwBqNZGa0wOzvUkKy317b//j8Y+vDXfPQ=="

app = Flask(__name__)
block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)



@app.route("/", methods=['GET'])
def watermark():
	url = ""
	data = {'url': url}
	try:
		url = ""
		container = request.args.get('container', type=str)
		blob = request.args.get('blob', type=str)
		block_blob_service.get_blob_to_path(container, blob, 'video.mp4')
		watermarking()
		block_blob_service.create_blob_from_path(
		"watermarked",
		blob,
		"output.mp4",
		content_settings=ContentSettings(content_type='video')
		)
		url = "https://" + account_name + ".blob.core.windows.net/watermarked/"+blob
		data = {'url': url}
	except: 
		url = ""
	finally:
		if os.path.isfile(str(os.getcwd())+"/raw.mp4"):
			os.remove(str(os.getcwd())+"/raw.mp4")
		if os.path.isfile(str(os.getcwd())+"/audio.mp3"):
			os.remove(str(os.getcwd())+"/audio.mp3")
		if os.path.isfile(str(os.getcwd())+"/output.mp4"):
			os.remove(str(os.getcwd())+"/output.mp4")
		if os.path.isfile(str(os.getcwd())+"/video.mp4"):
			os.remove(str(os.getcwd())+"/video.mp4")



	return jsonify(data)

def watermarking():
	subprocess.call("ffmpeg -i video.mp4 -f mp3 -ab 192000 -vn audio.mp3", shell=True)
	in_file = ffmpeg.input('video.mp4')
	overlay_file = ffmpeg.input('watermark.png')
	stream = in_file.overlay(overlay_file)
	output = ffmpeg.output(stream, "raw.mp4")
	ffmpeg.run(output)
	subprocess.call("ffmpeg -i raw.mp4 -i audio.mp3 -c copy output.mp4", shell=True)
	return



if __name__ == "__main__":
	app.run(debug=True)
