#!/usr/bin/env python
"""
Script pour démarrer Django avec HTTPS en développement
Nécessite django-extensions et Werkzeug
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recruitment_platform.settings")
    django.setup()
    
    # Démarrer le serveur avec HTTPS
    from django.core.management.commands.runserver import Command
    from django.core.servers.basehttp import WSGIServer
    from django.core.handlers.wsgi import WSGIHandler
    import ssl
    import socket
    
    # Configuration HTTPS
    server_address = ('127.0.0.1', 8000)
    httpd = WSGIServer(server_address, WSGIHandler())
    
    # Créer un contexte SSL auto-signé
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('localhost.pem', 'localhost-key.pem')
    
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print("🚀 Serveur Django HTTPS démarré sur https://127.0.0.1:8000/")
    print("⚠️  Certificat auto-signé - Acceptez l'avertissement de sécurité dans votre navigateur")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
        httpd.shutdown()

