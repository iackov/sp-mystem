Simplest multi-semi-questional .py server-side layer for "Yandex mystem binary" to fastest convert it to TCP/telnet-like service for your personal purposes... (THIS is only is POC. DO not Use it on Production!)

Yep. It works! But how and why? - Big question ))) ;)

USE: lanch scrypt with python2

EDIT:

BIND_ADDRESS = ('0.0.0.0', 8999)

- BIND Address and Port

- BACKLOG = 15 BACKLOG (Queue of question memory/forgotten)

- CHILDNUM = 50 (number of parallel answer-child threads)


USE: SERVER-SIDE: python2.7 mystem_server.py

CLIENT-SIDE: nc <SERVER_IP> 8999

-->ну вы и придурки

<--{"analysis":[{"lex":"ну"}],"text":"ну"}

<--{"text":" "} <--{"analysis":[{"lex":"вы"}],"text":"вы"} <--{"text":" "} <--{"analysis":[{"lex":"и"}],"text":"и"}

<--{"text":" "} <--{"analysis":[{"lex":"придурок"}],"text":"придурки"}

<--{"text":"\n"} <--<|>


END: See you soon..

DOCKER IMAGE and executable Releases for Windows and Linux: Coming Soon... now - really!

