
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
2. enter every container(sudo docker exec -it your_container_id bash) and run server:
    service: python service.py
    service_a: python manage.py runserver 0.0.0.0:5000
    service_b: python manage.py runserver 0.0.0.0:5000
    service_c: python service.py
    service_d: python service.py
3. curl 127.0.0.1:5000/error/
4. vist http://localhost:16686, view Jaeger UI
```

> notice: When requesting services `service_a` and `service_b', you must change the requested domain name to ip
> otherwise it will prompt `Invalid HTTP_HOST header`

#### Jaeger UI
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210306205656432.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3B1c2hpcWlhbmc=,size_16,color_FFFFFF,t_70#pic_center)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210306205701756.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3B1c2hpcWlhbmc=,size_16,color_FFFFFF,t_70#pic_center)

![在这里插入图片描述](https://img-blog.csdnimg.cn/2021030620570551.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3B1c2hpcWlhbmc=,size_16,color_FFFFFF,t_70#pic_center)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210306205705961.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3B1c2hpcWlhbmc=,size_16,color_FFFFFF,t_70#pic_center)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210306205705530.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3B1c2hpcWlhbmc=,size_16,color_FFFFFF,t_70#pic_center)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210306205700924.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3B1c2hpcWlhbmc=,size_16,color_FFFFFF,t_70#pic_center)
