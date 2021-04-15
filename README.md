Simplest multi-semi-questional .py server-side layer for "Yandex mystem binary" to fastest convert it to TCP/HTTP service for your personal purposes... (THIS is only is POC. DO not Use it on Production!)

Yep. It works! But how and why? - Big question ))) ;)

USE: lanch scrypt with python2

EDIT:

BIND_ADDRESS = ('0.0.0.0', 8999) - BIND Address and Port BACKLOG = 15 BACKLOG (Queue of question memory/forgotten) CHILDNUM = 50 (number of parallel answer-child threads) DOCKER IMAGE: Coming Soon... one two days...

USE: SERVER-SIDE: python2.7 mystem_server.py

CLIENT-SIDE: nc <SERVER_IP> 8999<br>
 -->ну вы и придурки<br>
 <--{"analysis":[{"lex":"ну"}],"text":"ну"}<br>
 <--{"text":" "} <--{"analysis":[{"lex":"вы"}],"text":"вы"}<br>
 <--{"text":" "} <--{"analysis":[{"lex":"и"}],"text":"и"}<br>
 <--{"text":" "} <--{"analysis":[{"lex":"придурок"}],"text":"придурки"}<br>
 <--{"text":"\n"} <--<|><br>

END: See you soon..
