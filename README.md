# <img src="https://cdn-icons-png.freepik.com/256/7664/7664156.png?uid=R161963193&ga=GA1.1.651749782.1725523197&semt=ais_hybrid" alt="iCON" width="30" height="30"> PlexSpot

[Dockerhub - ziadhorat/plex-spot](https://hub.docker.com/r/ziadhorat/plex-spot)

![DemoGif](https://github.com/user-attachments/assets/d893729d-7bb4-451c-8e22-7ffb79b2d61a)

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

### Creating a Plex API Token
[Plex Guide - Step by Step - Getting Plex Token, Nimrod](https://digiex.net/threads/plex-guide-step-by-step-getting-plex-token.15402/)

## Docker Run Command
If you prefer to run the container using `docker run`, use the following command:
```bash
docker run -d --name plex-spot \
  -p 8501:8501 \
  -e PLEX_API_TOKEN=your_plex_api_token_here \
  -e PLEX_SERVER_URL=http://localhost:32400 \
  ziadhorat/plex-spot
```
Open a web browser and navigate to `http://container-ip:8501`.

## Deploy with docker compose
`docker-compose.yml`:
```yaml
version: '3'
services:
  plex-spot:
    container_name: plex-spot
    ports:
      - "8501:8501"
    environment:
      - PLEX_API_TOKEN=your_plex_api_token_here
      - PLEX_SERVER_URL=http://localhost:32400
    image: ziadhorat/plex-spot
```
Open a web browser and navigate to `http://container-ip:8501`.

## Build & Run (docker compose)

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

## Notes
- If you use a reverse proxy, you will require websocket support/enabled.
- Tested with Movie/TV/Music Libraries (Supports 1 server only).

## TODO
- Add ARM architecture support for the Docker image.
- Implement pagination for better handling of large libraries.
- Display poster or artist covers, with IMDb links if available.
- Add support for multiple Plex servers (e.g., PLEX1, PLEX2).
- Extend support to additional media servers like Emby or Jellyfin.
- Consider querying Tautulli instead of Plex for better data access.
- Test the compose file - docker-compose.yml.
  
## Contributing
Feel free to submit issues or pull requests. Contributions are welcome!

## License
This project is licensed under the MIT License. See the LICENSE file for details.
