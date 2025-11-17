# Python user API service integrated with OPA

## Installation
1. Install docker (or alternatives), minikube, kubectl.
2. Execute:
    ```
    $ minikube start
    $ minikube tunnel
    ```
   Tunnel will ask for sudo password at some point. Leave tunnel running, open new terminal.
3. Setup minikube cluster:
    ```
    $ python3 -m venv-ansible
    $ source venv-ansible/bin/activate
    $ cd ansible
    $ ansible-galaxy install -r requirements.yml
    $ pip install -r requirements.txt
    $ ansible-playbook -i inventory/all.yaml kubernetes.yaml
    ```
    Argocd password will be printed during playbook run.
4. Open https://localhost and try to login in argocd with `admin:<password>`
5. Open http://localhost:5555/api/ and try to execute requests with auth `admin:12345`

## Cluster Apps
- my-cool-service - python server, which stores user data in sqlitedb. User with role `admin` can add new users, `editor` can view users.
- opa - Open Policy Agent receives user data from `my-cool-service` and validates if user is able to perform actions taking into consideration his **role**.
- replicator - replicates `opa` token to `my-cool-service` namespace.

## my-cool-service
### Config Env Vars
- OPA_HOST - fqdn address of `opa` service (default: localhost)
- OPA_PORT - port of `opa` service (default: 8181)
- OPA_SSL - if mtls should be enabled between `opa` and `my-cool-service` (default: false)
- OPA_TOKEN - token from `opa` api (default: unset) 

### Build Docker
```
 $ docker build -t njuhaandrej/my-cool-service:0.0.<version> -t njuhaandrej/my-cool-service:latest .
 $ docker push -a njuhaandrej/my-cool-service
```

### Requests
#### POST api/users
```
curl -X 'POST' \
  'http://localhost:5555/api/users/' \
  -H 'accept: application/json' \
  -H 'authorization: Basic YWRtaW46MTIzNDU=' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "editor",
  "email": "editor@localhost",
  "role": "editor",
  "password": "12345"
}'
=>
{
  "name": "editor",
  "email": "editor@localhost"
}
```
#### GET api/users
```
curl -X 'GET' \
  'http://localhost:5555/api/users/' \
  -H 'accept: application/json' \
  -H 'authorization: Basic ZWRpdG9yOjEyMzQ1'
 =>
 [
  {
    "name": "admin",
    "email": "admin@localhost"
  },
  {
    "name": "editor",
    "email": "editor@localhost"
  }
]
```