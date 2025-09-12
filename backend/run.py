#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = bool(app.config.get('DEBUG', False))
    app.run(host=host, port=port, debug=debug)