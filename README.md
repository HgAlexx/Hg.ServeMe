# ServeMe.py / ServeMe.exe


A minimalist wrapper around http.server which will serve the directory in which it is started, mainly design to serve local documentation.


ServeMe:
- will only bind to the loopback address (127.0.0.1 or localhost)
- will try to bind to the first available port between 42000 and 42999
- will only serv static files (no processing)
- will not allow browsing outside the process directory and its children
- will self-terminate after 3 hours of inactivity
- can be started multiple times from different directory concurrently


Build using pyInstaller:
```
pyInstaller -F -w ServeMe.py
```

MIT License

Copyright (c) 2022 HgAlexx
