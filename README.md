# auditdPy_Kafka


下载程序
-----
##### 下载程序
```
git clone https://github.com/Mosuan/AuditdPy_kafka && cd AuditdPy_Kafka
```

##### 依赖库
```
pip install -r requirements.txt
```

##### 安装auditd(centos 6.x自带)
```
sudo apt-get install auditd
```

配置
----
##### 查看并复制auditd的规则
```
cat ./docs/rule.txt
```

##### 将auditd规则粘贴覆盖到rules
```
sudo vim /etc/audit/audit.rules
```

##### 重启auditd
```
sudo /etc/init.d/auditd restart
```

##### 查看auditd规则是否加载上(结果不是No rules)
```
sudo auditctl -l
```

#### auditdPy_kafka 配置

##### 编辑配置文件 `vim ./lib/config.py`
```
#-*- coding:utf-8 -*-

# redis config
redis_host = '10.102.5.119'
redis_pass = 'Mosuan'
redis_db = 0
redis_port = 6379
redis_key = 'logstash:redis'

# kafka config
# kafka地址
kafka_host = '10.102.5.119'
# kafka端口
kafka_port = '9092'
# kafka topic
kafka_topic = 'huobi_logger'

# 消息队列名称，目前可填kafka或者redis
log_status = 'kafka'

# 是否生成错误log
log_key = False
```

##### 命令白名单配置 ./main.py 文件 self.command_white 变量
```
# 支持正则，添加规则的时候必须指定以什么开头和什么结尾，不然误报漏报估计会很严重
# 例子：
self.command_white = [
            "^(sudo ausearch) -",
            "^grep [a-zA-Z1-9]{1,20}",
            "^ifconfig -a",
        ]
```

##### 运行程序
```
sudo python main.py
```

参考
----
[Auditd文档][1]


  [1]: https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/security_guide/sec-understanding_audit_log_files
