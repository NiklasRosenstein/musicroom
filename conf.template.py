
host = '0.0.0.0'
port = 5000
debug = True
secret_key = 'replace this with a random string (required for cookies)'

# Arguments passed to pony.orm.Database.bind()
database = {
  'provider': 'postgres',
  'host': 'localhost',
  'port': 5432,
  'user': 'mroom',
  'password': 'mroom',
  'database': 'mroom'
}

# Google API key with access to the YouTube Data API.
google_api_key = "Google API KEY Here"
