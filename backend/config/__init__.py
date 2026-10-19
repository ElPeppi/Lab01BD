# Driver de MySQL:
#  - En local se usa mysqlclient (extensión en C, la más rápida).
#  - En AWS Lambda no se empaqueta mysqlclient (necesita librerías nativas de Linux),
#    así que se usa PyMySQL, que es Python puro y se hace pasar por "MySQLdb".
try:
    import MySQLdb  # noqa: F401
except ImportError:
    import pymysql

    pymysql.version_info = (2, 2, 7, "final", 0)  # Django 6 exige "mysqlclient >= 2.2.1"
    pymysql.install_as_MySQLdb()
