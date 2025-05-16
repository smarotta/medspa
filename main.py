from app.server import HTTPServer, RequestHandler

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8000), RequestHandler)
    print('Server running on port 8000...')
    server.serve_forever() 