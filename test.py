import gdown

url = 'https://drive.google.com/uc?id=19BxYm9nMVORpQctrbvaoNITxFHdBdjke'
output = '20150428_collected_images.zip'
gdown.download(url, output, quiet=False)
