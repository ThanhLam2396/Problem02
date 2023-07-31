

# Problem 2 - Code
## Problem Statement:
Develop a Prometheus exporter that monitors the response time of a web application (Let’s say it’s the one you designed in Problem 1 or it can be any website that needs to be monitored), and exposes the metrics for Prometheus scraping. Additionally, you need to deploy Prometheus to collect and store the metrics, and build a Grafana dashboard to visualize the metrics in real-time.
### Requirements:
- Implement a Prometheus exporter that measures the response time of a website at regular intervals, using any preferred languages (e.g., Python, Golang, etc.).
- The exporter should expose the metrics in a format compatible with Prometheus scraping (e.g.,HTTP endpoint with metrics in Prometheus exposition format).
- Deploy Prometheus on a server or container to collect and store the exported metrics (preferably using Docker Compose or Kubernetes).
- Configure Prometheus to scrape the exporter’s endpoint and collect the response time metrics.
- Build a Grafana dashboard that displays the response time metrics from Prometheus in a visually appealing and informative way.
- The Grafana dashboard should include relevant graphs, charts, and visualizations to monitor the response time trends over time.
- Ensure the entire solution is well-documented with clear instructions on how to set up and run the exporter, Prometheus, and Grafana.
Additional Tasks (Optional):
- Implement additional metrics collection and export, such as HTTP status codes, error rates, or other relevant website performance indicators.
- Add alerts in Prometheus based on predefined thresholds for response time or other metrics.
- Enhance the Grafana dashboard with additional panels, annotations, or drill-down capabilities.
## Evaluation Criteria:
- Correctness and efficiency of the Prometheus exporter in measuring and exposing the response time metrics.
- Proper deployment and configuration of Prometheus for metric collection and storage.
- Implementation of a visually appealing and informative Grafana dashboard that effectively visualizes the response time metrics.
- Documentation quality and clarity of setup instructions for the entire solution.
- Optional tasks implementation (if attempted).
- Overall design and organization of the solution

# Resolve Problem

With the above requirement I will have the following plan:
- Launch Kubernetes cluster on Azure Cloud
- Install NGINX Ingress Controller using Helm
- Installing the Prometheus Stack and configuration
- Install Web Application for demo with Helm (Minio Application)
- Develop a Prometheus exporter that monitors the response time
- Config Prometheus get Metrics
- Build a dashboard based on the metrics just collected.
- Build alerts based on metrics
- Summary what I do and more info about my system 

## Launch k8s cluster on azure cloud
Prerequisites:
- Install the Azure CLI, Kubernetes CLI, Helm on local machine.
- Need an Azure account with an active subscription.

Login to Azure cloud
```
az login
```
Create a resource group

```
az group create --name ThanhLamResourceGroup --location eastus
```
Create an AKS cluster

```
az aks create -g  ThanhLamResourceGroup -n ThanhLam --enable-managed-identity --node-count 3 --enable-addons monitoring --generate-ssh-keys

```
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/75a237b3-6703-4b61-818d-653660b48d1e)

Connect to AKS cluster
```
az account set --subscription XXXXXXXXXXXXXXXXXX
az aks get-credentials --resource-group ThanhLamResourceGroup --name ThanhLam
```
Test Connect
```
kubectl get deployments --all-namespaces=true
kubectl get deployments -A
```
Output:
```
NAMESPACE           NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
gatekeeper-system   gatekeeper-audit        0/1     0            0           6s
gatekeeper-system   gatekeeper-controller   0/2     0            0           6s
kube-system         ama-logs-rs             1/1     1            1           8m8s
kube-system         azure-policy            0/1     0            0           7s
kube-system         azure-policy-webhook    0/1     0            0           7s
kube-system         coredns                 2/2     2            2           9m53s
kube-system         coredns-autoscaler      1/1     1            1           9m53s
kube-system         konnectivity-agent      2/2     2            2           9m52s
kube-system         metrics-server          2/2     2            2           9m52s
```
## Install NGINX Ingress Controller using Helm 
To install an NGINX Ingress controller using Helm, add the nginx-stable repository to helm, then run helm repo update . After we have added the repository we can deploy using the chart nginx-stable/nginx-ingress.
```
helm repo add nginx-stable https://helm.nginx.com/stable
helm repo update
helm install nginx-ingress nginx-stable/nginx-ingress --set rbac.create=true
```
Validate that NGINX is Running
```
kubectl get pods --all-namespaces -l app=nginx-ingress-nginx-ingress
```
Output:
```
NAMESPACE   NAME                                           READY   STATUS    RESTARTS   AGE
default     nginx-ingress-nginx-ingress-5d55d8b9dc-v46bg   1/1     Running   0          2m14s
```

## Installing the Prometheus Stack
Add the Helm repository and list the available charts:
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```
Create a values file for easy to config and modify if needed with value get from Prometheus Stack Heml chart
```
helm show values prometheus-community/kube-prometheus-stack > values.yaml
```
Change some config for the first install
```
# Enable ingress for Grafana
  ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
       - grafana.thanhlam.com
    path: /

# Enable ingress for Prometheus
ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
     - prometheus.thanhlam.com
    paths: 
    - /

# Enable ingress for Alertmanager
  ingress:
    enabled: true
    ingressClassName: nginx
    hosts: 
       - alertmanager.thanhlam.com
    paths:
     - /
```

Finally, install the kube-prometheus-stack, using Helm

```
helm install kube-prom-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace -f value.yaml
```

Output:
```
-----------Deployment---------
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
kube-prom-stack-grafana               1/1     1            1           25m
kube-prom-stack-kube-prome-operator   1/1     1            1           25m
kube-prom-stack-kube-state-metrics    1/1     1            1           25m
-----------Service-----------
NAME                                       TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
alertmanager-operated                      ClusterIP   None           <none>        9093/TCP,9094/TCP,9094/UDP   16m
kube-prom-stack-grafana                    ClusterIP   10.0.242.216   <none>        80/TCP                       24m
kube-prom-stack-kube-prome-alertmanager    ClusterIP   10.0.88.171    <none>        9093/TCP,8080/TCP            24m
kube-prom-stack-kube-prome-operator        ClusterIP   10.0.85.170    <none>        443/TCP                      24m
kube-prom-stack-kube-prome-prometheus      ClusterIP   10.0.185.137   <none>        9090/TCP,8080/TCP            24m
kube-prom-stack-kube-state-metrics         ClusterIP   10.0.55.130    <none>        8080/TCP                     24m
kube-prom-stack-prometheus-node-exporter   ClusterIP   10.0.225.131   <none>        9100/TCP                     24m
prometheus-operated                        ClusterIP   None           <none>        9090/TCP                     16m
-----------Ingress-----------
NAME                                      CLASS   HOSTS                       ADDRESS         PORTS   AGE
kube-prom-stack-grafana                   nginx   grafana.thanhlam.com        40.88.198.157   80      17m
kube-prom-stack-kube-prome-alertmanager   nginx   alertmanager.thanhlam.com   40.88.198.157   80      26m
kube-prom-stack-kube-prome-prometheus     nginx   prometheus.thanhlam.com     40.88.198.157   80      26m
```
Get password of Grafana application
```
kubectl get secret --namespace monitoring kube-prom-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```
Add host and our service with web browers
```
20.121.89.64 prometheus.thanhlam.com
20.121.89.64 alertmanager.thanhlam.com
20.121.89.64 grafana.thanhlam.com
```
Let's check on browers

Prometheus:
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/90bd5132-0344-4dfd-b77e-d3730a98ec0d)

Grafana:
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/99185fe6-1cd1-4482-9aa2-f2a685dc2524)

AlertManager:
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/40ca1d1f-254d-43d2-9674-e453a993429a)




## Install Minio with Helm ( Assume this is a web application I want to monitor) 
```
helm install minio --set auth.rootPassword=thanhlam --set ingress.enabled=true --set ingress.ingressClassName=nginx --set ingress.hostname=minio.thanhlam.com oci://registry-1.docker.io/bitnamicharts/minio
```
Output:
```
NAME: minio
LAST DEPLOYED: Sun Jul 30 11:22:18 2023
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: minio
CHART VERSION: 12.6.11
APP VERSION: 2023.7.18
** Please be patient while the chart is being deployed **
MinIO&reg; can be accessed via port  on the following DNS name from within your cluster:
   minio.default.svc.cluster.local
To get your credentials run:
   export ROOT_USER=$(kubectl get secret --namespace default minio -o jsonpath="{.data.root-user}" | base64 -d)
   export ROOT_PASSWORD=$(kubectl get secret --namespace default minio -o jsonpath="{.data.root-password}" | base64 -d)
To connect to your MinIO&reg; server using a client:
- Run a MinIO&reg; Client pod and append the desired command (e.g. 'admin info'):
   kubectl run --namespace default minio-client \
     --rm --tty -i --restart='Never' \
     --env MINIO_SERVER_ROOT_USER=$ROOT_USER \
     --env MINIO_SERVER_ROOT_PASSWORD=$ROOT_PASSWORD \
     --env MINIO_SERVER_HOST=minio \
     --image docker.io/bitnami/minio-client:2023.7.18-debian-11-r0 -- admin info minio
To access the MinIO&reg; web UI:
- Get the MinIO&reg; URL:
   You should be able to access your new MinIO&reg; web UI through
   http://minio.thanhlam.com/minio/
```

```
default             pod/minio-6cbd95646d-csbwk                                   1/1  
default             service/minio                                                ClusterIP      10.0.95.61     <none>          9000/TCP,9001/TCP              2m7s
default             deployment.apps/minio                                 1/1     1            1           2m7s
default             replicaset.apps/minio-6cbd95646d                                 1         1         1       2m8s
```

Check on browers:
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/3a53702f-af56-4db1-a975-1c619c8e5264)


## Develop a Prometheus exporter that monitors the response time

As requested, I will write an exporter to get the response time of a web application.
#### My first idea: 
I will get the logs access of ingress-controller , then will write a small application to read the logs and calculate and expose metrics in prometheus format.


However while doing it I feel it is very complicated, because to be able to calculate and store the information, it is necessary to configure the database or use very complicated ways to be able to do this, it takes a lot of time. So I gave up on this method and made the 2nd simple way.

#### My second idea:
I searched the internet and found a python library to support writing exporter for prometheus and expose it according to prometheus standards
The code is located in the exporter folder, it's a simple script.

#### Coding
My script is based on prometheus client library
Python Link library: https://github.com/prometheus/client_python

````
from prometheus_client import Gauge, start_http_server
import requests
import time
import os

response_time_metric = Gauge('website_response_time_seconds', 'Website response time in seconds', ['url'])
WEBSITE_URL = os.getenv('WEBSITE_URL')
PORT = os.getenv('PORT')

WEBSITE_URL = "http://minio.thanhlam.com"
PORT = 8000
def measure_response_time(url):
    try:
        start_time = time.time()
        response = requests.get(url)
        response_time = time.time() - start_time
        response_time_metric.labels(url=url).set(response_time)
    except Exception as e:
        print(f"Error measuring response time for {url}: {e}")

if __name__ == '__main__':
    start_http_server(PORT)
    while True:
        measure_response_time(WEBSITE_URL)
        time.sleep(5)
````
#### Setup Image
After I finished writing the script and test, I wrote the Dockerfile for the script

```
FROM python:3.9 as build 
WORKDIR /code/app/
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .
FROM gcr.io/distroless/python3-debian11
COPY --from=build /code/app/ /code/app/
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
WORKDIR /code/app/

ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages
EXPOSE 8000
CMD ["run.py"]
```
And build and push the image to DockerHub
```
cd exporter
docker build -t thanhlam2396/thanhlam_exporter:1.0 .
docker push thanhlam2396/thanhlam_exporter:1.0
```
Output:
```
REPOSITORY                       TAG       IMAGE ID       CREATED       SIZE
thanhlam2396/thanhlam_exporter   2.0       a9dcf3d7fa56   2 hours ago   70.2MB
thanhlam2396/thanhlam_exporter   1.0       8992c41035b2   2 hours ago   70.2MB
thanhlam_exporter                latest    2846d2b5ce82   2 hours ago   70.2MB
thanhlam2396/thanhlam_exporter   latest    2846d2b5ce82   2 hours ago   70.2MB
```

### Setup configuration deploy to Kubernetes cluster
Create the pod yaml and deploy to k8s
```
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: thanhlam-exporter
  name: thanhlam-exporter
spec:
  hostAliases:
  - ip: "20.121.89.64"
    hostnames:
    - "minio.thanhlam.com"
  containers:
  - image: thanhlam2396/thanhlam_exporter:1.0
    name: thanhlam-exporter
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}

```
Deploy the pod
```
kubectl apply -f ingress-thanhlam-exporter.yaml
```
Output:
```
default  pod    ●  1/1    0 Running      0   2    n/a    n/a    n/a    n/a 10.244.4.14  
```

Create service for pod above

````
k expose pod thanhlam-exporter --port=8000 --target-port=8000
````

Create ingress for pod
````
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: thanhlam-exporter-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: thanhlam-exporter.thanhlam.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: thanhlam-exporter
            port:
              number: 8000
````
And deploy it to k8s
```
kubecll apply -f ingress-thanhlam-exporter.yaml
```
Check the resource on k8s we have like this
```
NAME                                                                  READY   STATUS    RESTARTS   AGE
pod/thanhlam-exporter                                                 1/1     Running   0          105m

NAME                                                     TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)             AGE
service/thanhlam-exporter                                ClusterIP   10.0.127.5   <none>        8000/TCP            102m

NAME                        CLASS   HOSTS                            ADDRESS        PORTS   AGE
minio                       nginx   minio.thanhlam.com               20.121.89.64   80      28h
thanhlam-exporter-ingress   nginx   thanhlam-exporter.thanhlam.com   20.121.89.64   80      100m

```
Now we can access the thanhlam-exporter.thanhlam.com endpoint in the browser and see the exported metrics in the prometheus format.
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/d3e5e6ff-5729-49b5-bbf7-361769e7e1af)

*** By the way:
For more information and to draw more informative and beautiful dashboards. I will further configure Ingress-controller metrics and blackbox exporter.

### Config Promethues get Metrics
Configure prometheus to get metrics from the exporter just deployed above.
Edit the values.yaml file that was created when installing prometheus
```
  additionalServiceMonitors:
   - name: thanhlam-exporter
     selector:
       matchLabels:
         run: thanhlam-exporter
     namespaceSelector:
       any: true
     endpoints:
       - port: thanhlam
         interval: 1m
   - name: prometheus-ingress
     selector:
       matchLabels:
         app.kubernetes.io/name: ingress-nginx
         app.kubernetes.io/component: controller
     namespaceSelector:
       any: true
     endpoints:
       - port: prometheus
         interval: 1m

...
    additionalScrapeConfigs: 
      - job_name: blackbox
        metrics_path: /probe
        params:
          module: [http_2xx]
        static_configs:
          # Add URLs as target parameter
          - targets:
            - https://startalk.vn
            - https://www.google.com
            - http://minio.thanhlam.com
            - http://prometheus.thanhlam.com
            - http://alertmanager.thanhlam.com
            - http://grafana.thanhlam.com
        relabel_configs:
        - source_labels: [__address__]
          target_label: __param_target
        - source_labels: [__param_target]
          # Important!     
          target_label: target
          # Ensure blackbox-exporter is reachable from Prometheus
        - target_label: __address__ 
          replacement: blackbox-exporter-prometheus-blackbox-exporter.default:9115
...

```
Update the value to prometheus with helm
```
helm upgrade kube-prom-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace -f values.yaml
```

Then you go to prometheus in browser access to target panel and check. It will be like this:
Ingress Metrics and ThanhLam-Exporter(My exporter) 
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/58b54a7c-ee24-4291-8537-6aeefd200a3f)
Blackbox Exporter:
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/33685c97-fa16-4be4-8b9c-771e80c74974)

## Build a dashboard based on the metrics just collected.
After drawing is done, the dashboard will look like this
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/6c3a493b-1482-44eb-a02f-e67cd3eb5301)
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/b1733d5d-db5b-4d81-ba13-808e890be437)


## Build alerts based on metrics
Here I will choose the metrics for alerts as follows
- BlackboxProbeFailed: Will warn when an endpoint being monitored is down or inaccessible.
- BlackboxProbeHttpFailure: Will warn when an endpoint returns status code values ​​other than 2xx or 3xx
- BlackboxSlowProbe: Will warn when an endpoint returns response time greater than 1s

- BlackboxSslCertificateWillExpireSoon: Will warn when an endpoint is about to expire tls (before 3 days)

- NginxLatencyHigh: Will warn when an endpoint returns response time greater than 3s (ingress layer)

To configure alerts, open the values.yaml file and configure the following:
```
additionalPrometheusRulesMap:
  rule-name:
      groups:
        - name: blackbox
          rules:
            - alert: BlackboxProbeFailed
              expr: probe_success == 0
              for: 1m
              annotations:
                summary: Blackbox probe failed (instance {{ $labels.instance }})
                description: "Probe failed\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
              labels:
                responsible: DevOps Team
                severity: critical
            - alert: BlackboxProbeHttpFailure
              expr: probe_http_status_code <= 199 OR probe_http_status_code > 400
              for: 1m
              annotations:
                summary: Blackbox probe HTTP failure (instance {{ $labels.instance }})
                description: "HTTP status code is not 200-399 [400 for graphql]\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
              labels:
                responsible: DevOps Team
                severity: critical
            - alert: BlackboxSlowProbe
              expr: avg_over_time(probe_duration_seconds[1m]) > 1
              for: 1m
              labels:
                responsible: DevOps Team
                severity: critical
              annotations:
                summary: Blackbox slow probe (instance {{ $labels.instance }})
                description: "Blackbox probe took more than 1s to complete\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
            - alert: BlackboxSslCertificateWillExpireSoon
              expr: 0 <= round((last_over_time(probe_ssl_earliest_cert_expiry[10m]) - time()) / 86400, 0.1) < 3
              for: 0m
              labels:
                severity: critical
              annotations:
                summary: Blackbox SSL certificate will expire soon (instance {{ $labels.instance }})
                description: "SSL certificate expires in less than 3 days\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
        - name: ingress
          rules:
            - alert: NginxLatencyHigh
              expr: >-
                histogram_quantile(0.99, sum(rate(nginx_ingress_controller_request_duration_seconds_bucket[30m])) by (host, node)) > 3
              for: 5m
              annotations:
                description: >-
                  Nginx latency high (instance {{ $labels.instance }}), p99 latency is higher than 3 seconds
                dashboard: "{{ $externalURL }}/../d/ingress/helm-ingress"
              labels:
                responsible: DevOps Team
                severity: warning
```

Update the value to prometheus with helm
```
helm upgrade kube-prom-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace -f values.yaml
```
Then you go to prometheus in browser access to alerts panel and check. It will be like this
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/e0291b45-4b3d-433a-9c20-45fc35e564bb)
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/36aab9fd-93d2-4d79-af7c-e75f6d23e0a4)
## SUMMARY
After fulfilling all the requirements, our system will look like this:
### Kubernetes Cluster:
Deployments:
<img width="1506" alt="image" src="https://github.com/ThanhLam2396/Problem02/assets/39935839/a1e34398-6fde-449c-a240-7cc6e404388f">
Pods: 
<img width="1505" alt="image" src="https://github.com/ThanhLam2396/Problem02/assets/39935839/7c179ccc-3b85-4b1b-a3d2-39888892e145">
Services:
<img width="1512" alt="image" src="https://github.com/ThanhLam2396/Problem02/assets/39935839/5dc9c5d0-80a9-4673-9090-1e081175cf35">
Ingress:
<img width="1510" alt="image" src="https://github.com/ThanhLam2396/Problem02/assets/39935839/c2a37c1c-2773-4b6c-9bfb-f7e055671019">

### Web Applications (Minio):
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/cbe0ae45-3e97-4cc8-b023-fe2ca17bd545)

### Exporter
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/32051b8e-f211-4d55-a991-9b1290c6dec7)

### Prometheus
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/08acc7f3-badc-4026-b385-d79924f008f8)
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/9a2fb8c7-3fdb-416a-ba63-df26bc330426)

### Grafana
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/436cab62-8e07-4904-b312-866041225ea3)

### Alertmanager
![image](https://github.com/ThanhLam2396/Problem02/assets/39935839/ff7b057d-faf1-4fcb-8f93-d39f9b0e5c82)


## NOTE:
To be able to access all the resources I have configured above please add host
```
sudo vim /etc/hosts
```
```
20.121.89.64 minio.thanhlam.com
20.121.89.64 prometheus.thanhlam.com
20.121.89.64 alertmanager.thanhlam.com
20.121.89.64 grafana.thanhlam.com
20.121.89.64 thanhlam-exporter.thanhlam.com
```

#### Application URLs:
User and Pass to access will be sent in the attached email. I will maintain this system for 5 days. This system is just a testing and is completely isolated, so security issues will be ignored.


Web Application (minio): http://minio.thanhlam.com

Prometheus: http://prometheus.thanhlam.com

Alertmanager: http://alertmanager.thanhlam.com

Grafana: http://grafana.thanhlam.com

Exporter: http://thanhlam-exporter.thanhlam.com
