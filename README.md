Bridge for cellular modem using hologram network. Bridges cellular network and pushover to send alerts.

Example Docker-Compose:
```yaml
cellular_bridge:
    image: cellular_bridge
    container_name: cellular_bridge
    restart: 'always'
    environment:
      - PUSHOVER_TOKEN=xxxxxx
      - PUSHOVER_USER=xxxxx
      - SIM_KEY=xxxxx
      # Optional port (cannot be privileged port)
      - LISTEN_PORT=9999
      # Optional IP (default: 0.0.0.0)
    ports:
        - 11111:11111
```
