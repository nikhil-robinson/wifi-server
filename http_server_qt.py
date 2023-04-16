from PyQt6.QtCore import QByteArray, QIODevice, QSettings
from PyQt6.QtNetwork import QHttpServer, QHttpRequestHeader, QHttpResponseHeader
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

# Define the handler function to handle incoming requests
def handle_request(request, response):
    # Get the HTTP request header
    request_header = request.header()

    # Get the HTTP method and URL
    http_method = request_header.methodString()
    url = request_header.path()

    # Prepare the HTTP response header
    response_header = QHttpResponseHeader()
    response_header.setStatusCode(200)
    response_header.setContentType('text/plain')
    response_header.setValue('Server', 'MyHTTPServer')

    # Prepare the HTTP response body
    response_body = QByteArray()
    response_body.append('Hello, World!')

    # Write the HTTP response header and body
    response.writeHead(response_header)
    response.write(response_body)

    # Close the response
    response.end()

# Create an instance of QHttpServer
server = QHttpServer()
server.listen(QHostAddress.LocalHostIPv4, 8080)
server.newRequest.connect(handle_request)

# Start the event loop
sys.exit(app.exec())
