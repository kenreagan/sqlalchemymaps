from App import create_app
from werkzeug.middleware import dispatcher, profiler
from prometheus_client import prometheus

app = create_app()

if __name__ == '__main__':
    dispatcher.DispatcherMiddleware(
        app=app,
        prometheus
    )
    prof = profiler.ProfilerMiddleware(
        app,
        open('profiler.prof', 'wb'),
        sort_by=('time')
    )
    app.run(debug=True)
