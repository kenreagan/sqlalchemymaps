from App import create_app
from werkzeug.middleware import dispatcher, profiler
from prometheus_client import make_wsgi_app

app = create_app()

if __name__ == '__main__':
    app.wsgi_app = dispatcher.DispatcherMiddleware(app.wsgi_app,
        {
            '/metrics': make_wsgi_app()
        }
    )

    app.run(debug=True)
