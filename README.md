# stttt2003pk_game_server_manager_api

## Introduction

* 正逢中国的新春佳节，在此祝各位新年快乐、身体健康、阖家幸福
过年的时候终于是一年可以清闲（就那么一点点）的时候，除了各种拜年陪吃饭什么的，终于可以在家看看文档撸撸代码什么的，然后花了大概几个小时撸了**这样一个demo**

* 本想撸点什么大的系统什么的，但是三姑六婆们实在太trouble了，so就撸了个用shell脚本控制call of duty 4安装、启动、关闭以及检查状态的脚本，就当时复习一下shell了，话说平时工作主要是python和运维为主，真心有点生疏了花了一天的时间

[stttt2003pk cod4server shell](https://github.com/stttt2003pk/stttt2003pk.cod4server)

![](https://raw.github.com/stttt2003pk/stttt2003pk_game_server_manager_api/master/screenshot/cod4servershell.png)

* 想想现在自动化运维都需要有平台、有API去控制业务的发布，控制这些游戏服务器的起停汇报状态等等，花了几个小时撸了这个example
* 首先考虑复习一下socket编程，然后考虑我们的自动化运维平台在使用过程中严重阻塞的问题

## Model Selection

* 链接中[这个](https://github.com/stttt2003pk/EWP_OMS)项目是一个极好的reference，运用了django以及其最擅长的ORM实现了saltstack+CMDB+zabbix监控的运维平台也给了我很多的启示
* [yorkoliu大神的这个django+各种多机管理工具的平台也是一个很好的借鉴](https://github.com/jackyang997/https-github.com-yorkoliu-pyauto/tree/master/%E7%AC%AC%E5%8D%81%E4%B8%89%E7%AB%A0)

### Non-blocking

* 尽管运维平台不需要考虑太多并发的问题，CMDB也可以做个简单的管理即可，但是我发现django模型下当前connection的连接阻塞的非常厉害，或许是我不太知道怎么去解决这个问题
* 另外一个问题是django对于ORM的操作和一些webframe细节实在限制的太死了，说个更蛋疼的问题，mysql需要在5.7支持json，在我的开发环境下需要去弄，另外还需要很多时间去熟悉，so我开始选择其他的思路

#### Scense

我们发布的过程往往是这样子的

* 打包更新游戏安装包Hotfix之类的
* 运维平台发布到一定target的nginx目标群，让nginx提供静态文件给服务器去下载(这里就是一个阻塞的根源，项目代码中涉及的使命召唤4的服务器bz2打包文件有接近4G的大小，如果在发布过程中该connection要阻塞的时间会非常的长。很多兄弟会说saltstatck或者ansible之类的去copy部署能解决这个问题，**但其实saltstack解决的是多目标多进程的问题，ansible就更加不用说了本身是队列阻塞的**)，当看到发布过程浏览器一直在转圈圈是不是会很方，所以就考虑来解决一下这个问题。
* 运维平台发指令到游戏服务器，让游戏服务器去执行下载更新包，解压后安装，启动游戏等等。这种为了灵活时间我们都自行封装socket去实现，当然现在这样造轮子已经不提倡了，不过就当做是复习一下socket编程了。**这里问题也很严重，socket本来也是IO密集型的操作，同样会阻塞的非常厉害，试想如果用原生的socket撇开木偶和salt（当然现在不用这些工具显得有些蠢，崇拜大神们早轮子的精神吖），就完全让自己变成了队列阻塞的ansible，而这种在操作很多台gameserver的时候几乎是不可以接受的，we want efficiency**

### Tornado
* 用Tornado和django、flask甚至nginx、haproxy去比静态，完全没有优势，ab打个700qps，4core8G各种僵硬，大家都一样，当然nginx和haproxy不止这种IO级别，更不用说这次的需求是一个几G的使命召唤4安装包
* gen.coroutine和iostream.IOStream是非常好的解决方案，所以花了几个小时写了这么一个东东

## Core Code Share

### salt rsync copy and hash_check encapsulation

* [这里对需要用salt传输文件到nginx上的方法重新封装了一下](https://github.com/stttt2003pk/stttt2003pk_game_server_manager_api/blob/master/saltwork.py)
* 有时候文件有点大我们就做一些md5check来确认发布的文件是不是全了

### gen.coroutine + ThreadPoolExecutor

* 当salt rsync、copy或者执行md5check的过程都是阻塞的很厉害的
* 将这些操作扔到异步线程去处理
* 但是这些同步阻塞的函数怎么异步呢？gen.coroutine配合协程来解决这个问题

```
class rsyncHandler(BaseHandler):
    executor = ThreadPoolExecutor(1)
    saltrun = saltstackwork()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        .....
            ret_rsync =yield self.__rsyn_cmd(tgt, source_file, dst_file)
        ......
            self.write(ret_str)
            self.finish()

    @run_on_executor
    def __rsyn_cmd(self, tgt, source_file, dst_file):
        ret = self.saltrun.__rsync_cmd__(tgt, source_file, dst_file)
        return ret
```

通过这种方式我用postman做了个简单的测试

packhandler的get方法是一个从mysql读取table的动作
postman中的操作是发布游戏服务包

可以看到rsync发布更新包的过程连接阻塞的很厉害一直在loading，以前用其他框架浏览器里面的数据库信息会读不出来，一直在转圈或者超时，用协程和线程池很好的解决了这个问题

* 这里我只选择了开一个线程池，数据库的读取还是在主进程中去处理的，当然线程爱开多少开多少
* 另外我在想其他的框架是否也能实现这种类似协程generator的工作呢，**值得去挖掘和尝试了**

![](https://raw.github.com/stttt2003pk/stttt2003pk_game_server_manager_api/master/screenshot/rsync.png)

* non-block的传到发布服务器上，供游戏下载更新了，接下来做服务器agent该做的事情

![](https://raw.github.com/stttt2003pk/stttt2003pk_game_server_manager_api/master/screenshot/nginx.png)

### iostream.IOStream + socket

* socket的密集IO是一直需要解决的问题，无论借助了什么工具去游戏服务器操作，当服务器多的时候这个问题依然需要去解决，否则前端的阻塞各种僵硬各种方
* [reference](http://strawhatfy.github.io/2015/09/27/tornado.iostream/)

因此做了这个尝试，对socket的操作在tornado下面重新封装一下

```
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
self.stream = iostream.IOStream(s)
```

* 服务器agent收到指令执行相应操作

* [前面写过各类agent这里就不详述了](https://github.com/stttt2003pk/stttt2003pk_monitor_agent_cherry)，这里弄个简单单线程的

```
......
     if check_code == check_code_true:
         print 'auth ok'

         job_type = self.__read_ShortInt()
         print 'job_type:%d'%job_type

         if not isinstance(job_type, int):
             self.cs.close()

         if job_type == 1:

             joblist_id = self.__read_Int()
             command = self.__read_Char()

             self.__report_status(joblist_id)
             self.__game(command)

         self.cs.close()
.....

    def __game(self, action):
        game_file_dir = '/var/gamefile/cod4server/'
        cod4server_script_name = 'cod4server.sh'
        command = 'cd %s && %s%s %s' %(game_file_dir, game_file_dir, cod4server_script_name, action)
        job_can_do = ['st','sp','ai']
        if action in job_can_do:
            ret = self.__commnad(command)
            print ret
        else:
            print 'action do not support'

```

简单的操作安装部署操作启动关闭

尽管连接一直阻塞，后台在做解压安装需要很多时间，却没有影响我做数据库读取或者对其他agent的socket操作
![](https://raw.github.com/stttt2003pk/stttt2003pk_game_server_manager_api/master/screenshot/socket.png)
![](https://raw.github.com/stttt2003pk/stttt2003pk_game_server_manager_api/master/screenshot/socket1.png)

死循环监听的agent就按照[前面提到的脚本](https://github.com/stttt2003pk/stttt2003pk.cod4server)跑完了业务，然后close掉连接
![](https://raw.github.com/stttt2003pk/stttt2003pk_game_server_manager_api/master/screenshot/socket2.png)

## Plan&Vision

* 花了两天做这个**异步非阻塞尝试**还是很有收获的，尽管需要结合CMDB、编写各类agent管理和监控业务、以及结合zabbix的做一套业务平台还是需要很多时间，目前做了原型和尝试，可能后面开发的系统会往这个方向去改进
* 对于tornado的研究还需要更深入一些
* 同样需要去对django和mysql有更深入的熟悉，尝试在django用mysql作为CMDB的项目当中有所突破




