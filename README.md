# <img src="https://cdn-icons-png.freepik.com/256/7664/7664156.png?uid=R161963193&ga=GA1.1.651749782.1725523197&semt=ais_hybrid" alt="iCON" width="30" height="30"> PlexSpot

[Dockerhub - ziadhorat/micro-plex-dashboard](https://hub.docker.com/r/ziadhorat/micro-plex-dashboard)

![image](https://github.com/user-attachments/assets/b73ed36e-cb28-4403-b73c-e7d23602f4dc)

## Overview
This aims to be a simple & small application that serves as a public frontend for a Plex server. 

It displays user and library statistics in a clean, intuitive interface.

Sometimes I am asked what is on my Plex server. This is my attempt at a set and forget solution.

## Features
- Display library items with totals & currently watching users.
- Simple deployment using Docker and Docker Compose.

## Environment Variables
- `PLEX_API_TOKEN`: Your Plex API token. **[Required]**
- `PLEX_SERVER_URL`: URL of your plex server, include `http`/`https`, exclude trailing `/`. **[Required]**
- `DASHBOARD_TITLE`: Page & Site title can be configured here. **[Optional]**
- `DASHBOARD_ICON`: Page & Site icon can be configured here. **[Optional]**

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/ziadhorat/Plex-Spot.git
cd Plex-Spot
```
### 2. Create a `.env` file
Copy the .env.example to .env and fill in the necessary values

### 3. Build and run using Docker Compose
```bash
docker-compose up --build
```
### 4. Access the app
Open a web browser and navigate to `http://localhost:8501`.

## Creating a Plex API Token
[Plex Guide - Step by Step - Getting Plex Token, Nimrod](https://digiex.net/threads/plex-guide-step-by-step-getting-plex-token.15402/)

## Docker Run Command
If you prefer to run the container using `docker run`, use the following command:
```bash
docker run -d --name micro-plex-dashboard \
  -p 8501:8501 \
  -e PLEX_API_TOKEN=your_plex_api_token_here \
  -e PLEX_SERVER_URL=http://localhost:32400 \
  ziadhorat/micro-plex-dashboard
```

## Notes
- If you use a reverse proxy, you will require websocket support/enabled.
- Only tested with Movie/TV/Music Libraries.

## TODO
- ARM Support on Docker image.
- Pagination might be required for large library support.
- Poster/Artist cover to be displayed along with IMDB links if available.
- Support for multiple servers (PLEX1, PLEX2).
- Support for additional media sources (Emby/Jellyfin).
- Maybe better to query Tautulli instead of Plex?
  
## Contributing
Feel free to submit issues or pull requests. Contributions are welcome!

## License
This project is licensed under the MIT License. See the LICENSE file for details.
