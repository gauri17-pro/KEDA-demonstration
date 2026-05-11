## Steps to be followed 

- Execute installkeda-prom.sh
```
chmod +x installkeda-prom.sh
./installkeda-prom.sh
```

- Edit the prometheus-server service to change the type to NodePort
```
kubectl edit svc/prometheus-server -n monitoring
```

- Edit the evaluationInterval to 10ms
```
kubectl edit cm prometheus-server -n monitoring 
```

- Create the secret for docker credentials
```
kubectl create secret docker-registry docker-creds \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=gauris17 \
  --docker-password='Password@123' 
```

- Apply the deployment
```
kubectl apply -f Deployment.yaml
```

- Expose the service
```
kubectl port-forward svc/prometheus-server 5000:5000
```

- Apply the scaledObject
```
kubectl apply -f scaledObject.yaml
```

- Install hey
```
apt install hey
hey -n 5000 -c 500 http://localhost:5000 
```
