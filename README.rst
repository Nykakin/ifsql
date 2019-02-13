=======
ifsql
=======

Allows to analyze filesystem using sql calls.

```bash
mariusz ~ $ ifsql /etc
> SELECT * FROM . LIMIT 10                                                                                                                                                              
file_name       dirname    full_path            file_type      file_size  access_time                 modification_time             group_id    owner_id    depth
--------------  ---------  -------------------  -----------  -----------  --------------------------  --------------------------  ----------  ----------  -------
.               ./         /etc/.               D                  12288  2019-02-13 15:29:09.723951  2019-01-19 23:04:47.775768           0           0        0
subgid          ./         /etc/subgid          F                     21  2018-02-28 00:42:07.321301  2015-08-26 23:34:27.740051           0           0        1
manpath.config  ./         /etc/manpath.config  F                   5174  2019-02-13 00:08:42.879798  2018-02-09 14:32:41                  0           0        1
rmt             ./         /etc/rmt             F                    268  2018-02-28 00:33:15.456767  2014-04-26 14:31:15                  0           0        1
hosts.deny      ./         /etc/hosts.deny      F                    711  2017-05-24 10:42:22.320242  2015-04-22 14:30:42                  0           0        1
ntp.conf        ./         /etc/ntp.conf        F                   2517  2019-02-13 00:10:10.276481  2018-02-14 09:23:36                  0           0        1
hosts           ./         /etc/hosts           F                    226  2019-02-13 15:11:57.863075  2018-07-05 13:04:49.741096           0           0        1
libao.conf      ./         /etc/libao.conf      F                     27  2018-02-28 07:45:52.036656  2015-01-08 03:19:20                  0           0        1
hostname        ./         /etc/hostname        F                     16  2019-02-13 13:16:29.049417  2018-07-05 13:04:49.741096           0           0        1
mtab            ./         /etc/mtab            L                     19  2019-02-12 23:49:00.417468  2017-05-11 21:40:26.214376           0           0        1
> SELECT dirname, SUM(file_size) FROM . WHERE dirname LIKE './%java%' GROUP BY dirname                                                                                                  
dirname                                        SUM(file_size)
-------------------------------------------  ----------------
./.java                                                  4096
./.java/.systemPrefs                                        0
./java                                                 135674
./java-11-openjdk                                       33878
./java-11-openjdk/management                            21471
./java-11-openjdk/security                              57028
./java-11-openjdk/security/policy                       10594
./java-11-openjdk/security/policy/limited                1359
./java-11-openjdk/security/policy/unlimited               339
./java-8-openjdk                                        50562
./java-8-openjdk/images                                  4096
./java-8-openjdk/images/cursors                          1274
./java-8-openjdk/management                             24860
./java-8-openjdk/security                               46540
./java/security                                          6585
./java/security/security.d                                  0
./ssl/certs/java                                       176466
> SELECT file_name, file_type from apt WHERE depth = 1                                                                                                                                  
file_name                 file_type
------------------------  -----------
sources.list              F
sources.list.save         F
trusted.gpg~              F
trusted.gpg               F
sources.list.distUpgrade  F
apt.conf.d                D
sources.list.d            D
preferences.d             D
trusted.gpg.d             D
```


Description
===========

To run tests:

```
python setup.py test
```


Note
====

This project has been set up using PyScaffold 2.5.8. For details and usage
information on PyScaffold see http://pyscaffold.readthedocs.org/.


