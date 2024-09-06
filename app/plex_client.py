import requests
import xmltodict
import logging
import os

logger = logging.getLogger(__name__)

class PlexClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.headers = {
            "X-Plex-Token": self.token
        }
        
        if os.getenv("DEBUG", "false").lower() == "true":
            logger.debug(f"PlexClient initialized with URL: {self.base_url} and Token: {self.token}")

    def get_user_stats(self):
        url = f"{self.base_url}/status/sessions"
        if os.getenv("DEBUG", "false").lower() == "true":
            logger.debug(f"Fetching user stats from Plex server: {url}")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = xmltodict.parse(response.text)
        media_container = data.get('MediaContainer', {})
        sessions = media_container.get('Video', [])
        
        if not isinstance(sessions, list):
            sessions = [sessions]
        
        active_sessions = len(sessions)
        users = {video['User']['@title'] for video in sessions if 'User' in video}
        total_users = len(users)
        
        return {
            'active_sessions': active_sessions,
            'total_users': total_users
        }

    def get_library_stats(self):
        url = f"{self.base_url}/library/sections"
        if os.getenv("DEBUG", "false").lower() == "true":
            logger.debug(f"Fetching library stats from Plex server: {url}")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return xmltodict.parse(response.text)

