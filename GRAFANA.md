# Grafana Dashboard Guide

This guide explains how to access, modify, and persist changes to the Grafana dashboard in the Open5GS Docker environment.

## 1. Accessing Grafana

- **URL**: [http://<DOCKER_HOST_IP>:3000](http://localhost:3000)
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin` (or as defined in `.env`)

## 2. Dashboard Structure

The Grafana configuration is stored in the `grafana/` directory of this repository:

```
grafana/
├── dashboards/
│   ├── open5gs_dashboard.json  # The actual dashboard definition
│   └── open5gs_dashboard.yml   # Provisioning config pointing to the JSON
└── datasources/
    └── prometheus_open5gs.yml  # Datasource configuration
```

In `sa-deploy.yaml`, this directory is mounted to `/etc/grafana/provisioning/`, ensuring that Grafana loads these settings on startup.

## 3. How to Modify the Dashboard

Since the dashboard is provisioned from a file, **changes made directly in the Grafana UI will be lost** if the container is recreated, unless you save them back to the JSON file.

### Step-by-Step Workflow:

1.  **Edit in UI**:
    - Log in to Grafana.
    - Open the **Open5GS Dashboard**.
    - Make your desired changes (add panels, change queries, adjust layout).
    - **Save** the dashboard in the UI to test your changes.

2.  **Export JSON**:
    - Click the **Share** icon (top right).
    - Go to the **Export** tab.
    - Toggle **"Export for sharing externally"** (optional, cleans up some IDs).
    - Click **Save to file** or **View JSON** and copy the content.

3.  **Update the Repository**:
    - Replace the content of `grafana/dashboards/open5gs_dashboard.json` with your exported JSON.
    - Save the file.

4.  **Verify Persistence**:
    - Restart the Grafana container to ensure the new provisioning works:
      ```bash
      docker compose -f sa-deploy.yaml restart grafana
      ```
    - Reload the page; your changes should persist.

## 4. Adding a New Dashboard

To add a completely new dashboard:

1.  **Create JSON**:
    - Create your dashboard in the Grafana UI and export the JSON (as above).
    - Save it as `grafana/dashboards/my_new_dashboard.json`.

2.  **Update Provisioning (Optional)**:
    - The `open5gs_dashboard.yml` is configured to load *all* JSON files in the directory, so you typically **do not** need to edit it.
    - Just restarting the Grafana container should pick up the new file.

## 5. Troubleshooting

- **Datasource Issues**: If panels show "No Data", check `grafana/datasources/prometheus_open5gs.yml` and ensure the `url` points to the correct Metrics container IP (usually handled by `${METRICS_IP}` in `.env`).
- **Provisioning Logs**: Check Grafana logs for provisioning errors:
  ```bash
  docker logs grafana
  ```
