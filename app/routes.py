from flask import render_template, jsonify, abort, send_from_directory
from app import app, cache
from app.jellyfin_client import JellyfinClient
import os
from dotenv import load_dotenv
import traceback

# Load environment variables from .env file
load_dotenv()

jellyfin_server_url = os.getenv("JELLYFIN_SERVER_URL")
jellyfin_api_key = os.getenv("JELLYFIN_API_KEY")
dashboard_title = os.getenv("DASHBOARD_TITLE", "JellyfinSpot")
dashboard_icon = os.getenv("DASHBOARD_ICON", "https://cdn-icons-png.freepik.com/256/7664/7664156.png")
print(os.getenv("DASHBOARD_ICON"))
print(os.getenv("DASHBOARD_TITLE"))

# Update Flask app config with the loaded values
app.config['DASHBOARD_TITLE'] = dashboard_title
app.config['DASHBOARD_ICON'] = dashboard_icon

jellyfin_client = JellyfinClient(jellyfin_server_url, jellyfin_api_key)

@app.route('/manifest.json')
def manifest():
    return send_from_directory(app.static_folder, 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return app.send_static_file('service-worker.js')

@app.route('/')
def index():
    libraries = get_libraries()
    default_library = libraries[0]['key'] if libraries else None
    return render_template('index.html', 
                           title=app.config['DASHBOARD_TITLE'], 
                           icon=app.config['DASHBOARD_ICON'], 
                           default_library=default_library,
                           app_version=app.config['APP_VERSION'])

@app.route('/api/user_stats')
@cache.cached(timeout=60)
def user_stats():
    try:
        stats = jellyfin_client.get_user_stats()
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"Error in user_stats route: {str(e)}")
        return jsonify({'error': 'Unable to fetch user stats'}), 500

@app.route('/api/libraries')
@cache.cached(timeout=3600)
def get_libraries():
    library_stats = jellyfin_client.get_library_stats()
    libraries = library_stats.get('MediaContainer', {}).get('Directory', [])
    if isinstance(libraries, dict):
        libraries = [libraries]
    
    # Filter to only include Movies and Shows libraries, explicitly exclude YouTube
    allowed_types = ['movies', 'tvshows']
    excluded_ids = ['34f331a89ce405e2b877d68d5ee4d4a2']  # YouTube library ID
    filtered_libraries = [
        {'key': lib['Id'], 'title': lib['Name']} 
        for lib in libraries 
        if lib.get('CollectionType', '').lower() in allowed_types 
        and lib['Id'] not in excluded_ids
    ]
    
    return filtered_libraries

@app.route('/api/library_contents/<library_key>')
@cache.cached(timeout=3600)
def library_contents(library_key):
    try:
        contents = jellyfin_client.get_library_contents(library_key)
        if not contents:
            app.logger.error(f"No contents returned for library key: {library_key}")
            return jsonify({'error': 'No library contents found'}), 404

        return jsonify(contents)
    except Exception as e:
        app.logger.error(f"Error in library_contents route: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Unable to fetch library contents'}), 500

@app.route('/api/genres/<library_key>')
@cache.cached(timeout=3600)
def get_genres(library_key):
    contents = jellyfin_client.get_library_contents(library_key)
    if not contents:
        return jsonify([])
    
    all_genres = set()
    for item in contents:
        genres = item.get('genres', '').split(', ')
        all_genres.update(genre for genre in genres if genre and genre != 'N/A')
    
    return jsonify(sorted(list(all_genres)))

@app.route('/api/total_counts')
@cache.cached(timeout=3600)
def get_total_counts():
    try:
        counts = jellyfin_client.get_total_counts()
        return jsonify(counts)
    except Exception as e:
        app.logger.error(f"Error in total_counts route: {str(e)}")
        return jsonify({'error': 'Unable to fetch total counts'}), 500
