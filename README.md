# SERPENT-chia-offline-transaction-sign-and-send
Tool that can send funds out of a wallet through the full node RPC, by using a mnemonic

## Contributors

![alt text](https://c.tenor.com/FDwYMy302gMAAAAM/tumbleweed-silence.gif?raw=true)

# High level overview
- The script's' functionalities:
    - it can generate a parent public key from a mnemonic
    - it can generate quantum resistent child public keys
    - it can generate a spend bundle with help from a running full node via its RPC interface
    - it can sign a spend bundle tx using the mnemonic
    - it can push the signed tx to the full node via its RPC interface
    
**The takeaway here is that the tool can send transactions from a wallet to another wallet without having to sync the wallet, just by using the full node.**

- !!! WARNING !!!
   - Because the tool needs your mnemonic to work, be REALLY CAREFUL not to accidentally share the mnemonic
   - The backend is posted here on github and I tried not to obfuscate anything so PLEASE feel free to review the code before you run it.

# Feedback/ Contribution
- Please post any issues you encountered or any feature requests using the issues tab.
- Also, feel free to contribute to the tool's development with a PR.

# How to use
The tool was tested just in Windows, but should work on every OS where python is supported.

It was designed from the ground-up to be used as a sub-module as well, so if you want to include it in a bigger set of scripts, you can do that 🙂. Just import _00_back_end.SERPENT_back_end and you are good to go.

NOTE#1: Using it as a sub-module may get you to fall into a rabbit hole. For that reason, recently a CLI interface was implemented which will completely isolate your scripts from SERPENT.

NOTE#2: Long story short you have 3 ways to use SERPENT in your scripts:

M#1 using the SERPENT class directly
M#2 using _00_CLI.py to direct your queries (recommended)
M#3 using the compiled CLI exe (more I/O overhead then M#2)

If you want fast support (faster than with github issues that is), join our Discord server: https://discord.gg/yPdCmHSgMe

## WINDOWS usage - instructions

1.1. Have the full node running and synced for the coin for which you want to do a transfer.

1.2. Run the compiled exe for windows and follow the instructions on screen.

GUI overview:
   
![alt text](ReadMe_res/GUI_overview.jpg?raw=true)

OR

2.1. Have the full node db of the coin you are about to check.

2.2. Use the compiled CLI interface you are more of a console type of person

2.2.1. Just launch the CLI in your favourite console with the -h switch to see the usage instructions; As of now those are:

![alt text](ReadMe_res/CLI_overview.jpg?raw=true)

# Support
Found this project useful? Send your ❤ in any form you can 🙂. Please contact me if you donated and want to be added to the contributors list !

- apple APPLE---apple1tdscevmlwa03rt464mr03tf6qs6y2xm3ay4z9lzn9pshad6jkp2s4crqd9
- beet XBT---xbt1kqflshzfhmushajg5hmsrus8rnf2qvh2cstl8wq7tlq2nrdk20msgc4c2g
- goldcoin OZT---ozt1u8klct3kcluvmu9hha8w6vte70d2z37zy7zydz55gygper0658rqkjqwts
- salvia XSLV---xslv19j3zexpgels2k8fkp30phxpxxz6syfzq52t2tuy8ac50nfmnennse9vjcw
- chia XCH---xch1glz7ufrfw9xfp5rnlxxh9mt9vk9yc8yjseet5c6u0mmykq8cpseqna6494
- chia-rose XCR---xcr1pdf0xetkr0k4pppqwv0hslvldr2qlrem09c00ks9y097zufn8drq5hlprx
- cryptodoge XCD---xcd1ds6jljkla5gwfjgty8w4q442uznmw9erwmwnvfspulqke3ya9nxqy9fe8t
- flax XFX---xfx13uwa4zqp0ah5740mknk0z8g3ejdl06sqq8ldvvk90tw058yy447saqjg3u
- fork XFK---xfk1cxkals86jtug06l5wc2m8nyz3ghxx5alqhj6tl3wjqhc7nagar9sus06un
- cannabis CANS---cans16ur4nqvvtdr8yduum5pljr3a73q33uuage6ktnsdr579xeerkc5q604j5v
- socks SOCK---sock1cwu9697vldmkk9mn2rs0ww45dx3aspvjqyygjaw4ucv6unaf8txqsajcvx
- wheat WHEAT---wheat1z4cz3434w48qumwt2f2dqtmgq4lfyv5aswmda7yfmamhml2afrzsa80mr2
- melati XMX---xmx1am6cjj5hrvwhjt8nvuytf2llnjhklpuzcjr4ywg7fe0n7a7n3tns3dj3jf
- taco XTX---xtx1crayqhdtx2rs5680q65c0c2ndaltje6vem0u0nnxtks4ucy058uqc0ak8m
- greendoge GDOG---gdog1ry524dunyuxkrjmzrdrgf5y6hzcdl0fghmncfcxxl83jknn82kmstzjjxk
- tad TAD---tad19s5nxa04znxsl7j6hud8p0uqtmnwd770d5a3nz40dtgwnuufjz0sgfcpnx
- covid COV---cov1ghxfysxsjknf7atnw7d4zqr9sfe9k4y9xc3lpwk5vv249wenlphssulqgp
- avocado AVO---avo1x9z98u6jkynkwutwd49cd58enqh3qfwlc3l7mamx2r6hgxdgqphs88t3yn
- spare SPARE---spare12e68ghay27pcdyuqcaz5qvtwst5mxzht33nxsxmygcd8nnxzhj6qjzytex
- sector XSC---xsc1lxkp9k64r77eh2rkhf6gxlukchnq26nvy6v5l9d6vyfs8jxqgvrs5vsrus
- cactus CAC---cac189er7g8gfsr6yl40t6gq8qygcrsjxkzhp50sk2xa6wh0f2nxzrhsm6rkfe
- flora XFL---xfl149k04h5p9crzsl0xz50efzka9clt56xtg5h33l35m8ld9h2knhqqvs7u76
- kale XKA---xka1m7hskvcd8xqx0a2e5nxc3ldn8gcz83pwvlkgd5x8vflaaq3uetmqj0ztk5
- maize XMZ---xmz1ycj7x6tsajgyannvr92udj23dsj6l4syqx38pmpzf6e7kkeeuvysscdvyw
- hddcoin HDD---hdd1qfs8hdtdrmsw9ya04cjex0d6dzkn7lfv7vp9g2dgup3p87ye9gqs6zvam2
- dogechia XDG---xdg17g6zx3u2a2zslwxrm0spv2297ygnuzhyme89x8kd5mrjz7mns39q6ge64c
- nchain ext9 NCH---nch1ae8hujcantv7naes30etvvcssm6uak9xzd5edwhtyq05adt60hkqlgyfmz
- chives XCC---xcc1amn5txlltvlcnlt6auw24ys6xku7t3npqt2szllassymswnehepszhnjar
- lucky SIX---six1r09eundsl9ntdw5vgq9xk9qedcvxdg7tg3urndcewppc3cn55p2syhu2d4
- BTCGreen xBTC---xbtc1njnsnayxuj4nn0fnzf2nsjnladh79spljx5vvs8v6vqhk9kp6rksgvyszh
- Olive XOL---xol15l6n5lj8splqasw7cr83c6cpdth93gu29vkf0dx0thkpnd2g36cqnearjs
- Beer XBR---xbr1gradjuw6sp78936ecumvjh4gx9kdu7g6gjdh4xdx9er9yk4zv9uqfxfxwm
- Pipscoin PIPS---pips13qcawq6y5dkxqtwnup04m2zmee9lpzsec0zyczt0pd0ra6cuut3qgvhj0k
- Scam SCM---scm1m3sh0pxvjcen2hyzmjgayac0x55ljhlwrptqu90thp6mtpfngx6qgkjwht
- peas PEA---pea1u2pn800fn36cg0lhwrcnpf82a2vsdjuhahdekawffew3u7u3c0xs25yqts
- mint XKM---xkm1k0nkq575wm3nmtkkxwrfmxg7qpt0hxe5m2fvw0dgvw3q0ynmzn3qqu5ntf
- Kiwi XKW---xkw1g9g80rq7exm9mqmzhwrug2qpkgh30dlgpcxkq7ca4x3d5deapm0swmgquy
- xcha XCA---xca1zeh3hlyuqau9a6h3xl3nq4efadam3xg5w672v3gvq7gwdyvaq6vs39rksp
- stor STOR---stor1vahvcz80arp2jl6v4np8grjxncrypzfelmm4uk0gvds5rpuf523qn9w482
- mogua MGA---mga1a9zhv34v75w8eazly5uuycx0tcskwmeyv8uu0kwc749k9wj866lq0val8m
- tranzact  TRZ---trz1mct7p22g2m9gn9m0xtuac4mnrwjkev0pqsxgx7tr6cjk2thnxmkq8q45ep
- Staicoin STAI---stai1m0axlhek947j5mz2wpvy0m9sky49h3jfqwqesy8rmzxfv9j9k5kq9zl6ft
- chaingreen CGN---cgn1llw5jp9ytz80pjhs96anxrcu7537mr45dg764xj2y3u8swmdf03ql63v0g
- lotus LCH---lch1yxmdv2jykwsvmwemka3uc2g3zg7dqfaevd8n2z2jht9nstsammtsyla2ex
- melon MELON---melon1uhrg7a43r0hv5n7k2tq9tsgq5adwc4fvjy7xfdjwqwz58vq2f24szftdfc
- kujenga XKJ---xkj14yyasecl9cygeu25ptx5562ulqj47pzkwsxrcdt20kdwhqkm0rjqvfedah
- Venidium XVM---xvm1h35hgaqxyvrgjmmr2qgr48ft0cxltyhnge6zkwkfsl9x93d4uq2qq9la0k
- aedge AEC---aec148wa08dgfdwuxrpq9sw0rylgnxlfllr9z2d7xsm6qatn5hfvmpfshu2nt6
- Skynet XNT---xnt1cq8xdu8svwhruefr5khzpqxturemtqrf6gk7uqjyjrhdl2dyapmsh9desg
- Shibgreen XSHIB---xshib1pkelrz8uml46m6hdw06ttezhaqasexe0527jce4cc03uj4fc8rcsaaatwy
- ethgreen XETH---xeth1e24uzser8h78gun2jppnqsgx7vsrktzkgdeuknat63ppcfw7htuq2pu73a
- PecanRolls ROLLS---rolls1lf7cwwl0cwtn6ua0uuncgj90czeg5j42083smq6afstvxsdl7m8syvztjy
- Silicoin SIT---sit183ks6unvnjhgz8augqe5hyj29uzc7za3ynf937eamn67cs74tnmquenyqh
