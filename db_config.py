from flask_mysqldb import MySQL

def init_mysql(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '30305'
    app.config['MYSQL_DB'] = 'epidemic_management'
    return MySQL(app)
