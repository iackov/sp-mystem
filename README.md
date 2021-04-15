# sp-mystem
Simplest multi-semi-questional .py server-side layer for "Yandex mystem binary" to fastest convert it to TCP/HTTP service for your personal purposes... (THIS is only is POC. DO not Use it on Production!)

Yep. It works! But how and why? - Big question ))) ;)

USE:
lanch scrypt python2

EDIT:

BIND_ADDRESS = ('0.0.0.0', 8999) - BIND Address and Port
BACKLOG = 15 BACKLOG (Queue of question memory/forgotten)
CHILDNUM = 50 (number of parallel answer-child threads)
