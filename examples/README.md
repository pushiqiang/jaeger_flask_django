
# jaeger use example

#### service[flask] ---> service_a[django] ---> service_b[django] ---> service_c[flask] ---> service_d[flask]

- service[flask]: using decorator tracing peer request
- service_a[django]: using django middleware tracing all request
- service_b[django]: using decorator tracing peer request
- service_c[flask]: using flask middleware(request hook) tracing all request
- service_d[flask]: using decorator tracing peer request


#### usage
```shell
1. sudo docker-compose up -d
2. enter every container(sudo docker exec -it your_container_id bash) and run server
3. curl 127.0.0.1:5000/error/
```

> notice: When requesting services `service_a` and `service_b', you must change the requested domain name to ip
> otherwise it will prompt `Invalid HTTP_HOST header`