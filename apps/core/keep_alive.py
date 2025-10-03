"""
Système de keep-alive pour empêcher l'hibernation sur Render.com
"""

import threading
import time
import requests
import os
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class KeepAliveService:
    def __init__(self):
        self.enabled = getattr(settings, 'ENABLE_KEEP_ALIVE', True)
        self.interval = getattr(settings, 'KEEP_ALIVE_INTERVAL', 240)  # 4 minutes
        self.base_url = getattr(settings, 'RENDER_EXTERNAL_URL', 'https://recruitment-platform-vnjb.onrender.com')
        self.endpoints = [
            '/health/',
            '/ping/', 
            '/status/',
            '/api/health/'
        ]
        self.is_running = False
        
    def ping_endpoint(self, endpoint):
        """Envoie un ping à un endpoint spécifique"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            logger.info(f"🔄 Keep-alive ping {endpoint} - {response.status_code} à {datetime.now()}")
            return True
        except Exception as e:
            logger.warning(f"❌ Erreur keep-alive {endpoint}: {e}")
            return False
    
    def ping_rotation(self):
        """Effectue une rotation entre tous les endpoints"""
        import random
        endpoint = random.choice(self.endpoints)
        return self.ping_endpoint(endpoint)
    
    def keep_alive_loop(self):
        """Boucle principale de keep-alive"""
        self.is_running = True
        logger.info(f"🚀 Démarrage du service keep-alive (intervalle: {self.interval}s)")
        
        while self.is_running:
            try:
                # Ping aléatoire d'un endpoint
                success = self.ping_rotation()
                
                if not success:
                    # En cas d'échec, essayer un autre endpoint
                    for endpoint in self.endpoints:
                        if self.ping_endpoint(endpoint):
                            break
                
            except Exception as e:
                logger.error(f"❌ Erreur dans la boucle keep-alive: {e}")
            
            # Attendre l'intervalle configuré
            time.sleep(self.interval)
    
    def stop(self):
        """Arrête le service keep-alive"""
        self.is_running = False
        logger.info("🛑 Service keep-alive arrêté")

# Instance globale
keep_alive_service = KeepAliveService()

def start_keep_alive():
    """Démarre le service keep-alive"""
    if keep_alive_service.enabled and not keep_alive_service.is_running:
        thread = threading.Thread(target=keep_alive_service.keep_alive_loop, daemon=True)
        thread.start()
        return True
    return False

def stop_keep_alive():
    """Arrête le service keep-alive"""
    keep_alive_service.stop()