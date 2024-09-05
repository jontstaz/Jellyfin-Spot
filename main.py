import streamlit as st
import os
from app.plex_client import PlexClient
from app.utils import setup_logging
from app.display import display_library_contents, get_user_stats, get_library_stats, get_library_contents

# Initialize logging
logger = setup_logging()

def main():
    plex_server_url = os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
    plex_api_token = os.getenv("PLEX_API_TOKEN", "none")
    dashboard_title = os.getenv("DASHBOARD_TITLE", "PlexSpot")
    dashboard_icon = os.getenv("DASHBOARD_ICON", "https://cdn-icons-png.freepik.com/256/7664/7664156.png?uid=R161963193&ga=GA1.1.651749782.1725523197&semt=ais_hybrid")

    plex_client = PlexClient(plex_server_url, plex_api_token)

    st.set_page_config(page_title=dashboard_title, page_icon=dashboard_icon, layout="wide")

    # st.title(dashboard_title)

    st.markdown(f"""
        <h1 style="display: flex; align-items: center;">
            <img src="{dashboard_icon}" style="width: 30px; margin-right: 10px;">
            {dashboard_title}
        </h1>
        """, unsafe_allow_html=True)

    active_sessions, _ = get_user_stats(plex_client)
    col1, col2 = st.columns(2)
    col1.metric("Active Streams", active_sessions)

    library_stats = get_library_stats(plex_client)
    libraries = library_stats.get('MediaContainer', {}).get('Directory', [])

    if isinstance(libraries, dict):
        libraries = [libraries]

    library_names = {lib['@key']: lib['@title'] for lib in libraries}
    selected_library = st.selectbox("Select a Library", list(library_names.values()))

    selected_library_key = next(key for key, name in library_names.items() if name == selected_library)
    
    # Fetch and display the contents of the selected library
    library_content = get_library_contents(plex_client, selected_library_key)
    
    # Determine the type of library (movie, show, or artist) based on the content
    media_container = library_content.get('MediaContainer', {})
    library_type = 'artist' if 'Directory' in media_container else 'video'
    
    # Display the contents of the selected library and get the total items count
    total_items = display_library_contents(library_content, library_type)
    
    col2.metric("Library Total", total_items)

if __name__ == "__main__":
    main()

