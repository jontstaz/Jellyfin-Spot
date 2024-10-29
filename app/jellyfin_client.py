import requests
import logging
import traceback
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class JellyfinClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "X-MediaBrowser-Token": self.api_key,
            "Content-Type": "application/json"
        }
        # Get the user ID during initialization
        self.user_id = self._get_user_id()

    def _get_user_id(self):
        try:
            response = self._make_request("/Users")
            # Get the first admin user or the first user if no admin
            admin_user = next((user for user in response if user.get('Policy', {}).get('IsAdministrator')), response[0])
            return admin_user.get('Id')
        except Exception as e:
            logger.error(f"Error getting user ID: {str(e)}")
            raise

    def _make_request(self, endpoint):
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            if isinstance(e, requests.exceptions.HTTPError):
                if e.response.status_code == 404:
                    logger.error("404 Error: The requested resource was not found.")
                elif e.response.status_code == 401:
                    logger.error("401 Error: Unauthorized. Please check your Jellyfin API key.")
            raise

    def get_user_stats(self):
        try:
            response = self._make_request("/Sessions")
            active_sessions = len([s for s in response if s.get('PlayState', {}).get('IsPaused') is False])
            users = {session.get('UserName') for session in response if session.get('UserName')}
            
            return {
                'active_sessions': active_sessions,
                'total_users': len(users)
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {'active_sessions': 0, 'total_users': 0}

    def get_library_stats(self):
        try:
            response = self._make_request("/Library/MediaFolders")
            libraries = response.get('Items', [])
            
            # Convert to expected format and include only movies and TV shows
            allowed_types = ['movies', 'tvshows']
            formatted_libraries = []
            for lib in libraries:
                collection_type = lib.get('CollectionType', '').lower()
                if collection_type in allowed_types:
                    formatted_libraries.append({
                        'Id': lib.get('Id'),
                        'Name': lib.get('Name'),
                        'CollectionType': collection_type
                    })
            
            return {'MediaContainer': {'Directory': formatted_libraries}}
        except Exception as e:
            logger.error(f"Error getting library stats: {str(e)}")
            return {'MediaContainer': {'Directory': []}}

    def get_library_contents(self, library_key):
        try:
            # First, get the library type from Items endpoint
            library_info = self._make_request(f"/Items?Ids={library_key}")
            collection_type = library_info.get('Items', [{}])[0].get('CollectionType', '').lower()

            # Base query parameters
            base_params = (
                f"ParentId={library_key}&"
                "Fields=Path,Overview,Genres,Studios,ProductionYear,OfficialRating,"
                "DateCreated,RunTimeTicks,MediaSources,Width,Height"
            )

            # Add type-specific parameters
            if collection_type == 'tvshows':
                query = f"/Users/{self.user_id}/Items?{base_params}&IncludeItemTypes=Series&Recursive=true"
            else:
                query = f"/Users/{self.user_id}/Items?{base_params}&IncludeItemTypes=Movie&Recursive=true"

            response = self._make_request(query)
            
            if not response or 'Items' not in response:
                logger.error("No items found in response")
                return None
            
            formatted_items = []
            for item in response.get('Items', []):
                try:
                    studios = item.get('Studios', [])
                    studio_name = studios[0].get('Name') if studios else 'N/A'
                    genres = ", ".join(item.get('Genres', [])) or 'N/A'
                    
                    # Calculate duration based on type
                    duration_ticks = item.get('RunTimeTicks', 0)
                    duration = f"{int(duration_ticks / (10000000 * 60)) if duration_ticks else 0} min"
                    
                    formatted_items.append({
                        'title': item.get('Name', 'N/A'),
                        'year': item.get('ProductionYear', 'N/A'),
                        'genres': genres,
                        'added_date': item.get('DateCreated', 'N/A')[:10] if item.get('DateCreated') else 'N/A',
                        'studio': studio_name,
                        'summary': item.get('Overview', 'No summary available.'),
                        'contentRating': item.get('OfficialRating', 'N/A'),
                        'rating': item.get('CommunityRating', 'N/A'),
                        'duration': duration,
                        'resolution': f"{item.get('Width', 'N/A')}x{item.get('Height', 'N/A')}",
                        'tagline': item.get('Tagline', ''),
                        'imageUrl': f"{self.base_url}/Items/{item.get('Id')}/Images/Primary"
                    })
                except Exception as item_error:
                    logger.error(f"Error processing item: {str(item_error)}")
                    continue
            
            return formatted_items
        except Exception as e:
            logger.error(f"Error getting library contents for key {library_key}: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def get_total_counts(self):
        try:
            movies_query = "/Users/{}/Items?IncludeItemTypes=Movie&Recursive=true".format(self.user_id)
            shows_query = "/Users/{}/Items?IncludeItemTypes=Series&Recursive=true".format(self.user_id)
            
            movies_response = self._make_request(movies_query)
            shows_response = self._make_request(shows_query)
            
            return {
                'total_movies': movies_response.get('TotalRecordCount', 0),
                'total_shows': shows_response.get('TotalRecordCount', 0)
            }
        except Exception as e:
            logger.error(f"Error getting total counts: {str(e)}")
            return {'total_movies': 0, 'total_shows': 0}