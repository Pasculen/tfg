import os

from flask import Flask
from flaskthreads import AppContextThread
from sqlite3 import connect



HOST = '127.0.1.1'
PORT = 1234

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    # register the database commands
    from flaskr import db

    db.init_app(app)

    # apply the blueprints to the app
    from flaskr import blog

    app.register_blueprint(blog.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")


    # socket-reading thread
    def thread_job():

        import OpenSSL
        from OpenSSL.SSL import TLSv1_2_METHOD, FILETYPE_PEM, VERIFY_FAIL_IF_NO_PEER_CERT
        import socket
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization

        def hola():
            pass

        # Create context for de TLS session
        context = OpenSSL.SSL.Context(TLSv1_2_METHOD)

        # Load server private key and cert
        context.use_privatekey_file(os.path.join(app.instance_path, "server_key.pem"))
        context.use_certificate_file(os.path.join(app.instance_path, "server_cert.pem"))

        # Add verify mode
        context.set_verify(VERIFY_FAIL_IF_NO_PEER_CERT, hola)

        # Load root certificate
        context.load_verify_locations(cafile=os.path.join(app.instance_path, "certificate.pem"))

        # Create the initial connection with the above context and a socket
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setblocking(1)
        soc.bind((HOST, PORT))
        soc.listen(1)
        conn_ini = OpenSSL.SSL.Connection(context, soc)

        
        # Accept client onnection
        while 1:
            conn, addr = conn_ini.accept()
            conn.set_accept_state()
            print("Connected by "+str(addr))

            while 1:
                try:
                    data = conn.read(1024)

                    # Connect to the flask database
                    conn_db = connect(os.path.join(app.instance_path, "flaskr.sqlite")) 
                    curs = conn_db.cursor()
                    evidencias = data.decode().split('\n')

                    for e in evidencias:
                        if e != '':
                            if "_rule" in e:
                                e = e.split('. ')[1]
                                e = "AUDITD: "+e

                                query = 'SELECT * FROM evidence WHERE body="{}";'.format(e)
                                curs.execute(query)
                                rows = curs.fetchall()
                                res = len(rows)
                                if res == 1:
                                    continue
                            else:
                                e = "INOTIFY: "+e

                            curs.execute("INSERT INTO evidence (body) VALUES (?);",
                                [e],
                                )
                    conn_db.commit()
                    conn_db.close()
                    #print(data.decode())
                except OpenSSL.SSL.SysCallError as e:
                    #if e[0] == -1 or e[1] == 'Unexpected EOF':
                    conn.shutdown()
                    break

    with app.app_context():
        t = AppContextThread(target=thread_job)
        t.start()
        #t.join()

    return app
