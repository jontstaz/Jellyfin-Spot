import streamlit as st
import xmltodict
import logging
import requests
import pandas as pd
import os
from app.cache_manager import cache_manager

logger = logging.getLogger(__name__)
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

def display_library_contents(library_content, library_type):
    try:
        media_items = library_content.get('MediaContainer', {}).get('Video', []) or library_content.get('MediaContainer', {}).get('Directory', [])
        if isinstance(media_items, dict):
            media_items = [media_items]

        table_data = []
        for item in media_items:
            title = item.get('@title', 'N/A')
            year = item.get('@year', 'N/A')
            genres = item.get('Genre', [])
            if isinstance(genres, list):
                genres = ", ".join(genre.get('@tag', 'N/A') for genre in genres)
            elif isinstance(genres, dict):
                genres = genres.get('@tag', 'N/A')
            else:
                genres = 'N/A'

            table_data.append({
                "Title": title,
                "Year": year,
                "Genres": genres
            })

        if table_data:
            sorted_table_data = sorted(table_data, key=lambda x: x['Title'])
            
            # Convert list of dicts to DataFrame
            df = pd.DataFrame(sorted_table_data)
            
            # Display the DataFrame without index column
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            return len(sorted_table_data)
        else:
            st.write("No media found in this library.")
            return 0
    except Exception as e:
        logger.error(f"Error displaying library contents: {e}")
        st.write("Error displaying library contents.")
        return 0

@cache_manager(ttl=3600)
def get_user_stats(plex_client):
    try:
        user_stats = plex_client.get_user_stats()
        if DEBUG:
            logger.info(f"Fetching user stats from Plex server: {plex_client.base_url}")
        return user_stats
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        return {}

        media_container = user_stats.get('MediaContainer', {})
        active_sessions = int(media_container.get('@size', 0))
        users = {video['User']['@title'] for video in media_container.get('Video', []) if isinstance(video, dict) and 'User' in video}
        total_users = len(users)
        return active_sessions, total_users
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        logger.error(f"User stats response: {user_stats}")
        return 0, 0


@cache_manager(ttl=3600)
def get_library_stats(plex_client):
    try:
        return plex_client.get_library_stats()
    except Exception as e:
        logger.error(f"Error fetching library stats: {e}")
        return {}

@cache_manager(ttl=3600)
def get_library_contents(plex_client, library_key):
    try:
        url = f"{plex_client.base_url}/library/sections/{library_key}/all"
        response = requests.get(url, headers=plex_client.headers)
        response.raise_for_status()
        return xmltodict.parse(response.text)
    except Exception as e:
        logger.error(f"Error fetching library contents: {e}")
        return {}

